import re
import socket
from typing import List, Dict, Any, Optional
import httpx

from app.modules.base import BaseModule
from app.schemas import Finding

class LocationModule(BaseModule):
    name = "location"
    description = "Geointelligence engine: performs IP address geolocation, domain server location, GPS coordinate reverse geocoding, and address/place geocoding via OpenStreetMap and telecom IP registries."

    def __init__(self):
        super().__init__()
        self.http_headers = {
            "User-Agent": "Trinetra-OSINT-Platform/1.0 (Defensible Geointelligence Module; contact@trinetra.local)"
        }

    def _detect_target_type(self, target: str) -> str:
        """
        Detects whether target is:
        - 'coordinates' (e.g. '37.7749, -122.4194')
        - 'ip' (e.g. '8.8.8.8' or IPv6)
        - 'domain' (e.g. 'example.com')
        - 'address' (e.g. 'Eiffel Tower, Paris' or '10 Downing St, London')
        """
        clean = target.strip()
        
        # Check coordinates: e.g. 37.7749, -122.4194
        coord_match = re.match(r"^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$", clean)
        if coord_match:
            return "coordinates"

        # Check IPv4
        ipv4_match = re.match(r"^(\d{1,3}\.){3}\d{1,3}$", clean)
        if ipv4_match:
            return "ip"

        # Check IPv6
        if ":" in clean and len(clean.split(":")) >= 3:
            return "ip"

        # Check domain (no spaces, contains dot, valid TLD pattern)
        if " " not in clean and re.match(r"^[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", clean):
            return "domain"

        return "address"

    async def _query_ip_geolocation(self, client: httpx.AsyncClient, ip: str, original_target: str) -> List[Finding]:
        findings = []
        try:
            url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    country = data.get("country", "Unknown")
                    region = data.get("regionName", "Unknown")
                    city = data.get("city", "Unknown")
                    zip_code = data.get("zip", "")
                    lat = data.get("lat")
                    lon = data.get("lon")
                    isp = data.get("isp", "Unknown")
                    org = data.get("org", "Unknown")
                    as_num = data.get("as", "Unknown")
                    timezone = data.get("timezone", "Unknown")

                    # Try reverse DNS lookup for PTR record
                    try:
                        ptr_host = socket.gethostbyaddr(ip)[0]
                    except Exception:
                        ptr_host = "No PTR record found"

                    osm_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=12/{lat}/{lon}"
                    gmaps_link = f"https://www.google.com/maps?q={lat},{lon}"

                    evidence = (
                        f"IP Geolocation confirmed: {city}, {region}, {country} (Postal: {zip_code}). "
                        f"Coordinates: {lat}, {lon}. ISP: {isp} | Org: {org} | AS: {as_num}. "
                        f"Timezone: {timezone}. PTR Host: {ptr_host}."
                    )

                    findings.append(self.create_finding(
                        source="IP Geolocation Telemetry Registry",
                        exact_url=osm_link,
                        evidence_snippet=evidence,
                        confidence=0.92,
                        target=original_target,
                        confidence_reasoning="Authoritative regional ISP subnet allocation and BGP routing registration.",
                        category="Geolocation",
                        verified=True,
                        raw_metadata={
                            "ip": ip,
                            "country": country,
                            "country_code": data.get("countryCode"),
                            "region": region,
                            "city": city,
                            "postal_code": zip_code,
                            "latitude": lat,
                            "longitude": lon,
                            "isp": isp,
                            "org": org,
                            "as": as_num,
                            "timezone": timezone,
                            "ptr_host": ptr_host,
                            "osm_url": osm_link,
                            "google_maps_url": gmaps_link
                        }
                    ))
        except Exception as e:
            findings.append(self.create_finding(
                source="IP Geolocation Query",
                exact_url=f"http://ip-api.com/json/{ip}",
                evidence_snippet=f"Failed to query IP geolocation: {str(e)}",
                confidence=0.1,
                target=original_target,
                confidence_reasoning="Network lookup exception.",
                category="Error"
            ))
        return findings

    async def _query_reverse_coordinates(self, client: httpx.AsyncClient, lat: float, lon: float, original_target: str) -> List[Finding]:
        findings = []
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                display_name = data.get("display_name", "Unknown Location")
                address = data.get("address", {})
                
                road = address.get("road", "")
                suburb = address.get("suburb") or address.get("neighbourhood", "")
                city = address.get("city") or address.get("town") or address.get("village", "")
                county = address.get("county", "")
                state = address.get("state", "")
                country = address.get("country", "")
                postcode = address.get("postcode", "")

                osm_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=17/{lat}/{lon}"
                gmaps_url = f"https://www.google.com/maps?q={lat},{lon}"

                evidence = (
                    f"Physical Address resolved from coordinates ({lat}, {lon}): {display_name}. "
                    f"Road: {road} | City/Town: {city} | State: {state} | Country: {country} | Postal: {postcode}."
                )

                findings.append(self.create_finding(
                    source="OpenStreetMap Nominatim Reverse Geocoder",
                    exact_url=osm_url,
                    evidence_snippet=evidence,
                    confidence=0.98,
                    target=original_target,
                    confidence_reasoning="Direct GPS coordinate resolution via OpenStreetMap spatial ontology.",
                    category="Geolocation",
                    verified=True,
                    raw_metadata={
                        "latitude": lat,
                        "longitude": lon,
                        "display_name": display_name,
                        "address": address,
                        "road": road,
                        "city": city,
                        "state": state,
                        "country": country,
                        "postcode": postcode,
                        "osm_url": osm_url,
                        "google_maps_url": gmaps_url
                    }
                ))
        except Exception as e:
            findings.append(self.create_finding(
                source="Nominatim Geocoder",
                exact_url=f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}",
                evidence_snippet=f"Failed to reverse-geocode coordinates: {str(e)}",
                confidence=0.1,
                target=original_target,
                confidence_reasoning="Reverse geocoding query exception.",
                category="Error"
            ))
        return findings

    async def _query_forward_address(self, client: httpx.AsyncClient, address_query: str) -> List[Finding]:
        findings = []
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": address_query,
                "format": "json",
                "addressdetails": "1",
                "limit": "3"
            }
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                results = resp.json()
                if not results:
                    findings.append(self.create_finding(
                        source="OpenStreetMap Nominatim Geocoder",
                        exact_url=f"https://www.openstreetmap.org/search?query={address_query}",
                        evidence_snippet=f"No matching physical places or addresses found for query '{address_query}'.",
                        confidence=0.4,
                        target=address_query,
                        confidence_reasoning="Zero results returned by spatial database.",
                        category="Geolocation"
                    ))
                    return findings

                for idx, r in enumerate(results):
                    lat = float(r.get("lat", 0))
                    lon = float(r.get("lon", 0))
                    display_name = r.get("display_name", "")
                    place_type = r.get("type", "location")
                    category = r.get("class", "place")
                    addr = r.get("address", {})

                    osm_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}"
                    gmaps_url = f"https://www.google.com/maps?q={lat},{lon}"

                    evidence = (
                        f"Location #{idx + 1} ({place_type.title()} / {category}): {display_name}. "
                        f"Coordinates: {lat}, {lon}. Country: {addr.get('country', '')}."
                    )

                    findings.append(self.create_finding(
                        source="OpenStreetMap Nominatim Geocoder",
                        exact_url=osm_url,
                        evidence_snippet=evidence,
                        confidence=0.95 - (idx * 0.05),
                        target=address_query,
                        confidence_reasoning="Spatial geocoding match against global OpenStreetMap cartography.",
                        category="Geolocation",
                        verified=True,
                        raw_metadata={
                            "latitude": lat,
                            "longitude": lon,
                            "display_name": display_name,
                            "place_type": place_type,
                            "category": category,
                            "address": addr,
                            "boundingbox": r.get("boundingbox", []),
                            "osm_url": osm_url,
                            "google_maps_url": gmaps_url
                        }
                    ))
        except Exception as e:
            findings.append(self.create_finding(
                source="Nominatim Geocoder",
                exact_url=f"https://www.openstreetmap.org/search?query={address_query}",
                evidence_snippet=f"Failed forward geocode: {str(e)}",
                confidence=0.1,
                target=address_query,
                confidence_reasoning="Forward geocode network exception.",
                category="Error"
            ))
        return findings

    async def run(self, target: str, options: Optional[Dict[str, Any]] = None) -> List[Finding]:
        target = target.strip()
        target_type = self._detect_target_type(target)
        findings: List[Finding] = []

        async with httpx.AsyncClient(timeout=10.0, headers=self.http_headers) as client:
            if target_type == "coordinates":
                parts = [p.strip() for p in target.split(",")]
                lat = float(parts[0])
                lon = float(parts[1])
                findings = await self._query_reverse_coordinates(client, lat, lon, target)

            elif target_type == "ip":
                findings = await self._query_ip_geolocation(client, target, target)

            elif target_type == "domain":
                # First resolve domain to IP
                try:
                    resolved_ip = socket.gethostbyname(target)
                    dns_finding = self.create_finding(
                        source="DNS A Record Exchanger",
                        exact_url=f"dns://{target}",
                        evidence_snippet=f"Domain '{target}' resolved to server IP: {resolved_ip}.",
                        confidence=0.99,
                        target=target,
                        confidence_reasoning="Standard socket DNS A-record resolution.",
                        category="Infrastructure",
                        verified=True,
                        raw_metadata={"domain": target, "ip": resolved_ip}
                    )
                    findings.append(dns_finding)
                    # Query IP geolocation for domain server
                    geo_findings = await self._query_ip_geolocation(client, resolved_ip, target)
                    findings.extend(geo_findings)
                except Exception as e:
                    findings.append(self.create_finding(
                        source="DNS Resolver",
                        exact_url=f"dns://{target}",
                        evidence_snippet=f"Failed to resolve domain '{target}' to IP: {str(e)}",
                        confidence=0.1,
                        target=target,
                        confidence_reasoning="DNS resolution failure.",
                        category="Error"
                    ))

            else: # "address" or place query
                findings = await self._query_forward_address(client, target)

        return findings
