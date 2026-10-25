import re
from typing import List, Dict, Any, Optional
import httpx
import phonenumbers
from phonenumbers import geocoder, carrier, number_type

from app.modules.base import BaseModule
from app.schemas import Finding
from app.config import settings

class PhoneModule(BaseModule):
    name = "phone"
    description = "Validates and parses public phone footprints (E.164, region, carrier, line type) and searches public open web listings without querying people-search brokers."

    def _get_number_type_name(self, ntype: int) -> str:
        types_map = {
            phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line (Landline)",
            phonenumbers.PhoneNumberType.MOBILE: "Mobile",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
            phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
            phonenumbers.PhoneNumberType.VOIP: "VoIP (Voice over IP)",
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
            phonenumbers.PhoneNumberType.PAGER: "Pager",
            phonenumbers.PhoneNumberType.UAN: "Universal Access Number",
            phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail Service",
            phonenumbers.PhoneNumberType.UNKNOWN: "Unknown"
        }
        return types_map.get(ntype, "Unknown")

    async def _search_public_web_footprint(self, client: httpx.AsyncClient, formatted_num: str) -> List[Finding]:
        """
        Searches the open web for public pages where the exact phone number appears
        (e.g., official public business listings, press releases, corporate contact pages).
        STRICT COMPLIANCE: Do not query people-search brokers, do not return person names or photos.
        """
        findings = []
        if not settings.SEARXNG_URL:
            return findings

        try:
            # Query exact number
            search_url = f"{settings.SEARXNG_URL}/search?q=%22{formatted_num}%22&format=json"
            resp = await client.get(search_url, timeout=6.0)
            if resp.status_code == 200:
                results = resp.json().get("results", [])[:5]
                for r in results:
                    url = r.get("url", "")
                    # Filter out known people-search broker domains
                    broker_domains = ["truepeoplesearch", "whitepages", "fastpeoplesearch", "spokeo", "beenverified", "radaris"]
                    if any(b in url.lower() for b in broker_domains):
                        continue

                    snippet = r.get("content", f"Public open web occurrence of number '{formatted_num}'")
                    findings.append(self.create_finding(
                        source="Public Web Index",
                        exact_url=url,
                        evidence_snippet=snippet,
                        confidence=0.80,
                        target=formatted_num,
                        confidence_reasoning="Discovered indexed public web page containing exact formatted phone number.",
                        category="Public Listing",
                        verified=False,
                        raw_metadata={"source_engine": r.get("engine")}
                    ))
        except Exception:
            pass

        return findings

    async def run(self, target: str, options: Optional[Dict[str, Any]] = None) -> List[Finding]:
        options = options or {}
        default_region = options.get("default_region", "US")
        findings: List[Finding] = []

        try:
            parsed = phonenumbers.parse(target, default_region)
        except phonenumbers.NumberParseException as e:
            findings.append(self.create_finding(
                source="ITU-T libphonenumber",
                exact_url=f"tel:{target}",
                evidence_snippet=f"Invalid phone number syntax: {str(e)}",
                confidence=0.1,
                target=target,
                confidence_reasoning="Phone number failed international telecommunication syntax validation.",
                category="Validation Error",
                verified=False
            ))
            return findings

        is_valid = phonenumbers.is_valid_number(parsed)
        is_possible = phonenumbers.is_possible_number(parsed)
        e164_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        international_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        national_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)

        # Broad administrative region & carrier (telecom metadata only)
        geo_region = geocoder.description_for_number(parsed, "en") or "Global / Unspecified"
        carrier_name = carrier.name_for_number(parsed, "en") or "Unspecified Carrier"
        line_type_str = self._get_number_type_name(number_type(parsed))

        # 1. Primary Telecom Metadata Finding
        snippet = (
            f"Valid international phone number ({e164_format}). Line type: {line_type_str}. "
            f"Assigned Carrier: {carrier_name}. Geographic assignment: {geo_region}. "
            f"Formatting: National: {national_format}, International: {international_format}."
        )
        findings.append(self.create_finding(
            source="ITU-T Telecommunication Registry",
            exact_url=f"tel:{e164_format}",
            evidence_snippet=snippet,
            confidence=0.99 if is_valid else 0.65,
            target=e164_format,
            confidence_reasoning="Authoritative ITU-T numbering plan parsing and carrier range allocation.",
            category="Telecom Metadata",
            verified=is_valid,
            raw_metadata={
                "e164": e164_format,
                "country_code": parsed.country_code,
                "national_number": parsed.national_number,
                "line_type": line_type_str,
                "carrier": carrier_name,
                "geo_region": geo_region,
                "is_valid": is_valid,
                "is_possible": is_possible
            }
        ))

        # 2. Search open web public footprint
        async with httpx.AsyncClient(timeout=7.0, verify=False) as client:
            web_findings = await self._search_public_web_footprint(client, international_format)
            findings.extend(web_findings)

        return findings
