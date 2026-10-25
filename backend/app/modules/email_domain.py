import re
import asyncio
from typing import List, Dict, Any, Optional
import httpx
import dns.resolver

from app.modules.base import BaseModule
from app.schemas import Finding
from app.config import settings

class EmailDomainModule(BaseModule):
    name = "email_domain"
    description = "Performs email validation, MX inspection, HIBP breach audits, DNS enumeration, RDAP lookup, and crt.sh certificate transparency."

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    async def _check_mx_records(self, domain: str) -> List[Dict[str, Any]]:
        records = []
        try:
            loop = asyncio.get_running_loop()
            answers = await loop.run_in_executor(None, lambda: dns.resolver.resolve(domain, 'MX'))
            for rdata in answers:
                records.append({
                    "preference": rdata.preference,
                    "exchange": str(rdata.exchange).rstrip(".")
                })
        except Exception:
            pass
        return records

    async def _check_dns_records(self, domain: str) -> Dict[str, List[str]]:
        results = {}
        loop = asyncio.get_running_loop()
        for record_type in ['A', 'AAAA', 'TXT', 'NS']:
            try:
                answers = await loop.run_in_executor(None, lambda rt=record_type: dns.resolver.resolve(domain, rt))
                results[record_type] = [str(r).strip('"') for r in answers]
            except Exception:
                results[record_type] = []
        return results

    async def _check_hibp_breaches(self, client: httpx.AsyncClient, email: str) -> List[Finding]:
        """
        Queries breach exposure via Have I Been Pwned API or verified breach index.
        CRITICAL ETHICAL RULE: Only report that a breach occurred, breach date, and data classes.
        NEVER output passwords.
        """
        findings = []
        headers = {
            "User-Agent": "TRINETRA-OSINT-BreachAuditor-v1.0"
        }
        if settings.HIBP_API_KEY:
            headers["hibp-api-key"] = settings.HIBP_API_KEY

        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
        try:
            resp = await client.get(url, headers=headers, timeout=6.0)
            if resp.status_code == 200:
                breaches = resp.json()
                for b in breaches:
                    name = b.get("Name", "Unknown Breach")
                    date = b.get("BreachDate", "Unknown Date")
                    classes = ", ".join(b.get("DataClasses", []))
                    snippet = (
                        f"Account exposed in verified security incident '{name}' on {date}. "
                        f"Compromised attribute classes: {classes}. [Note: Passwords/credentials are never stored or displayed]."
                    )
                    findings.append(self.create_finding(
                        source=f"HaveIBeenPwned - {name}",
                        exact_url=f"https://haveibeenpwned.com/account/{email}",
                        evidence_snippet=snippet,
                        confidence=0.98,
                        target=email,
                        confidence_reasoning="Confirmed entry in HaveIBeenPwned verified breach registry.",
                        category="Breach Exposure",
                        verified=True,
                        raw_metadata={
                            "breach_title": name,
                            "breach_date": date,
                            "pwn_count": b.get("PwnCount", 0),
                            "data_classes": b.get("DataClasses", [])
                        }
                    ))
            elif resp.status_code == 404:
                # No breach record found
                pass
        except Exception:
            pass

        return findings

    async def _check_rdap(self, client: httpx.AsyncClient, domain: str) -> Optional[Finding]:
        """Queries authoritative RDAP registry for domain registration metadata"""
        rdap_url = f"https://rdap.org/domain/{domain}"
        try:
            resp = await client.get(rdap_url, follow_redirects=True, timeout=6.0)
            if resp.status_code == 200:
                data = resp.json()
                status_list = ", ".join(data.get("status", []))
                registrar = "Unknown"
                entities = data.get("entities", [])
                for entity in entities:
                    if "registrar" in entity.get("roles", []):
                        vcard = entity.get("vcardArray", [])
                        if len(vcard) > 1:
                            for item in vcard[1]:
                                if item[0] == "fn":
                                    registrar = item[3]
                
                events = {e.get("eventAction"): e.get("eventDate") for e in data.get("events", [])}
                created_date = events.get("registration", "Unknown")
                exp_date = events.get("expiration", "Unknown")

                snippet = (
                    f"Domain RDAP registration active. Registrar: {registrar}. "
                    f"Created: {created_date}, Expires: {exp_date}. Status: {status_list}."
                )
                return self.create_finding(
                    source="RDAP Domain Registry",
                    exact_url=rdap_url,
                    evidence_snippet=snippet,
                    confidence=0.99,
                    target=domain,
                    confidence_reasoning="Direct query to authoritative IANA/ICANN RDAP server.",
                    category="Domain Registration",
                    verified=True,
                    raw_metadata={
                        "registrar": registrar,
                        "registration_date": created_date,
                        "expiration_date": exp_date,
                        "status": status_list
                    }
                )
        except Exception:
            return None
        return None

    async def _check_certificate_transparency(self, client: httpx.AsyncClient, domain: str) -> List[Finding]:
        """Enumerates active subdomains from crt.sh Certificate Transparency logs"""
        findings = []
        crt_url = f"https://crt.sh/?q=%.{domain}&output=json"
        try:
            resp = await client.get(crt_url, timeout=7.0)
            if resp.status_code == 200:
                entries = resp.json()
                unique_subdomains = set()
                for entry in entries[:25]: # limit to top 25 recent
                    name_value = entry.get("name_value", "")
                    for sub in name_value.split("\n"):
                        sub = sub.strip().lower()
                        if sub and domain in sub and not sub.startswith("*"):
                            unique_subdomains.add(sub)

                for sub in list(unique_subdomains)[:15]:
                    snippet = f"Subdomain discovered via Certificate Transparency logs: {sub}"
                    findings.append(self.create_finding(
                        source="crt.sh Certificate Transparency",
                        exact_url=f"https://{sub}",
                        evidence_snippet=snippet,
                        confidence=0.95,
                        target=domain,
                        confidence_reasoning="Cryptographic TLS certificate issued and logged in CT audit log.",
                        category="Infrastructure",
                        verified=True,
                        raw_metadata={"subdomain": sub}
                    ))
        except Exception:
            pass
        return findings

    async def run(self, target: str, options: Optional[Dict[str, Any]] = None) -> List[Finding]:
        options = options or {}
        findings: List[Finding] = []
        target = target.strip()

        async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
            # Check if email or domain
            if "@" in target:
                email = target.lower()
                domain = email.split("@")[-1]

                # 1. Format validation
                is_valid_format = bool(self.EMAIL_REGEX.match(email))
                findings.append(self.create_finding(
                    source="Email Format Validator",
                    exact_url=f"mailto:{email}",
                    evidence_snippet=f"Syntax analysis: RFC 5322 compliance is {is_valid_format}.",
                    confidence=1.0 if is_valid_format else 0.1,
                    target=email,
                    confidence_reasoning="RFC 5322 regex parser validation.",
                    category="Format Verification",
                    verified=is_valid_format
                ))

                # 2. MX records for email host
                mx_records = await self._check_mx_records(domain)
                if mx_records:
                    mx_str = ", ".join([f"{r['exchange']} (pri {r['preference']})" for r in mx_records])
                    findings.append(self.create_finding(
                        source="DNS MX Resolver",
                        exact_url=f"dns://{domain}/MX",
                        evidence_snippet=f"Active mail exchangers for @{domain}: {mx_str}",
                        confidence=0.98,
                        target=email,
                        confidence_reasoning="Authoritative DNS query returned active MX routing records.",
                        category="Infrastructure",
                        verified=True,
                        raw_metadata={"mx_records": mx_records}
                    ))
                else:
                    findings.append(self.create_finding(
                        source="DNS MX Resolver",
                        exact_url=f"dns://{domain}/MX",
                        evidence_snippet=f"No MX records found for domain @{domain}. Deliverability is doubtful.",
                        confidence=0.85,
                        target=email,
                        confidence_reasoning="DNS resolution returned no MX entries.",
                        category="Infrastructure",
                        verified=False
                    ))

                # 3. Breach check
                if options.get("check_breaches", True):
                    breach_findings = await self._check_hibp_breaches(client, email)
                    findings.extend(breach_findings)

            else:
                # Target is a domain
                domain = target.lower().replace("https://", "").replace("http://", "").split("/")[0]

                # 1. DNS records
                dns_results = await self._check_dns_records(domain)
                for rtype, values in dns_results.items():
                    if values:
                        snippet = f"DNS {rtype} records: {', '.join(values[:5])}"
                        findings.append(self.create_finding(
                            source=f"DNS {rtype} Resolver",
                            exact_url=f"dns://{domain}/{rtype}",
                            evidence_snippet=snippet,
                            confidence=0.99,
                            target=domain,
                            confidence_reasoning=f"Resolved authoritative {rtype} records from nameserver.",
                            category="Infrastructure",
                            verified=True,
                            raw_metadata={"type": rtype, "records": values}
                        ))

                # 2. RDAP registration
                rdap_finding = await self._check_rdap(client, domain)
                if rdap_finding:
                    findings.append(rdap_finding)

                # 3. Certificate Transparency
                if options.get("check_subdomains", True):
                    ct_findings = await self._check_certificate_transparency(client, domain)
                    findings.extend(ct_findings)

        return findings
