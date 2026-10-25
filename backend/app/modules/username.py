import asyncio
import json
import os
import re
from typing import List, Dict, Any, Optional
import httpx

from app.modules.base import BaseModule
from app.schemas import Finding
from app.config import settings

class UsernameModule(BaseModule):
    name = "username"
    description = "Checks usernames across 500+ platforms, generates leetspeak/affix variants, and queries archive & search engines."

    def __init__(self, sites_file: Optional[str] = None):
        if sites_file is None:
            sites_file = os.path.join(os.path.dirname(__file__), "data", "sites.json")
        self.sites_file = sites_file
        self.sites = self._load_sites()

    def _load_sites(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.sites_file):
            try:
                with open(self.sites_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def generate_variants(self, username: str) -> List[str]:
        """
        Generates realistic username variants (batman, batman_, b4tman, batman123, etc.)
        """
        variants = set()
        clean = username.strip().lower()
        variants.add(clean)
        
        # Leetspeak transforms
        if 'a' in clean:
            variants.add(clean.replace('a', '4', 1)) # single substitution: batman -> b4tman
            variants.add(clean.replace('a', '4'))    # all occurrences: batman -> b4tm4n
        if 'e' in clean:
            variants.add(clean.replace('e', '3'))
        if 'i' in clean:
            variants.add(clean.replace('i', '1'))
        if 'o' in clean:
            variants.add(clean.replace('o', '0'))
        if 's' in clean:
            variants.add(clean.replace('s', '5'))

        leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
        leet_variant = "".join(leet_map.get(c, c) for c in clean)
        if leet_variant != clean:
            variants.add(leet_variant)

        # Affixes and separators
        variants.add(f"{clean}_")
        variants.add(f"_{clean}")
        variants.add(f"{clean}1")
        variants.add(f"{clean}123")
        variants.add(f"{clean}_dev")
        variants.add(f"{clean}_sec")
        variants.add(f"the_{clean}")
        variants.add(f"real_{clean}")

        if "_" in clean:
            variants.add(clean.replace("_", "-"))
            variants.add(clean.replace("_", ""))
        elif "-" in clean:
            variants.add(clean.replace("-", "_"))
            variants.add(clean.replace("-", ""))

        return sorted(list(variants))

    async def _check_single_site(
        self,
        client: httpx.AsyncClient,
        site: Dict[str, Any],
        username: str
    ) -> Optional[Finding]:
        url = site["url"].format(username)
        check_type = site.get("check_type", "status_code")
        error_code = site.get("error_code", 404)
        error_msg = site.get("error_message", "Not Found")
        rank = site.get("rank", 50)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            resp = await client.get(url, headers=headers, follow_redirects=True, timeout=6.0)
            status = resp.status_code
            content = resp.text

            # Check existence criteria
            found = False
            confidence = 0.50

            if check_type == "status_code":
                if status == 200:
                    found = True
                    # Higher confidence if username explicitly appears in HTML title or body
                    if username.lower() in content.lower():
                        confidence = 0.90 if rank <= 10 else 0.82
                    else:
                        confidence = 0.65
                elif status == error_code:
                    found = False
            elif check_type == "message":
                if status == 200 and error_msg.lower() not in content.lower():
                    found = True
                    confidence = 0.88 if username.lower() in content.lower() else 0.70

            if found:
                # Extract clean snippet
                snippet = f"Active account profile discovered on {site['name']} for handle '{username}'."
                # Try finding a brief title or bio from response HTML
                title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
                if title_match:
                    page_title = title_match.group(1).strip().replace("\n", " ")
                    snippet += f" Page title: {page_title[:100]}"

                reasoning = (
                    f"HTTP status {status} returned with valid profile response. "
                    f"Username token confirmed in body: {username.lower() in content.lower()}. "
                    f"Platform rank {rank} (confidence calibrated to reduce false positives)."
                )

                return self.create_finding(
                    source=site["name"],
                    exact_url=url,
                    evidence_snippet=snippet,
                    confidence=confidence,
                    target=username,
                    confidence_reasoning=reasoning,
                    category=site.get("category", "Social"),
                    verified=(confidence >= 0.85),
                    raw_metadata={
                        "platform": site["name"],
                        "http_status": status,
                        "check_type": check_type,
                        "category": site.get("category", "Social")
                    }
                )
        except Exception:
            return None
        return None

    async def search_archive_and_mentions(self, client: httpx.AsyncClient, username: str) -> List[Finding]:
        """
        Queries Wayback Machine CDX and public search indexes for historical and web-wide mentions.
        """
        findings = []
        # 1. Wayback Machine CDX query
        cdx_url = f"https://web.archive.org/cdx/search/cdx?url=*{username}*&output=json&limit=5"
        try:
            resp = await client.get(cdx_url, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 1: # Row 0 is header
                    for row in data[1:]:
                        original_url = row[2]
                        timestamp = row[1]
                        wayback_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
                        snippet = f"Wayback Machine archive snapshot from {timestamp} mentioning target in URL: {original_url}"
                        findings.append(self.create_finding(
                            source="Wayback Machine CDX",
                            exact_url=wayback_url,
                            evidence_snippet=snippet,
                            confidence=0.88,
                            target=username,
                            confidence_reasoning="Archived snapshot confirmed in Internet Archive CDX Index.",
                            category="Archive",
                            verified=True,
                            raw_metadata={"archive_timestamp": timestamp, "original_url": original_url}
                        ))
        except Exception:
            pass

        # 2. Open Search Engine Mention Index (fallback / SearXNG if configured)
        if settings.SEARXNG_URL:
            try:
                search_url = f"{settings.SEARXNG_URL}/search?q=%22{username}%22&format=json"
                resp = await client.get(search_url, timeout=5.0)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])[:5]
                    for r in results:
                        findings.append(self.create_finding(
                            source=r.get("engine", "Web Search Mention"),
                            exact_url=r.get("url", ""),
                            evidence_snippet=r.get("content", f"Web mention discovered for term '{username}'"),
                            confidence=0.75,
                            target=username,
                            confidence_reasoning="Search engine indexed page containing quoted handle.",
                            category="Search Mention",
                            verified=False,
                            raw_metadata={"engine": r.get("engine")}
                        ))
            except Exception:
                pass

        return findings

    async def run(self, target: str, options: Optional[Dict[str, Any]] = None) -> List[Finding]:
        options = options or {}
        max_sites = options.get("max_sites", 500)
        generate_variants = options.get("generate_variants", False)
        check_web_mentions = options.get("check_web_mentions", True)

        findings: List[Finding] = []
        semaphore = asyncio.Semaphore(25) # 25 concurrent connections

        # Determine target list (either primary username or top variants)
        targets_to_check = [target]
        if generate_variants:
            variants = self.generate_variants(target)[:4] # top 4 variants
            for v in variants:
                if v not in targets_to_check:
                    targets_to_check.append(v)

        sites_subset = self.sites[:max_sites] if self.sites else []

        async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
            async def bounded_check(s, u):
                async with semaphore:
                    return await self._check_single_site(client, s, u)

            # Prioritize top 30 sites for primary target
            tasks = [bounded_check(s, target) for s in sites_subset]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, Finding):
                    findings.append(res)

            # If check web mentions requested
            if check_web_mentions:
                archive_findings = await self.search_archive_and_mentions(client, target)
                findings.extend(archive_findings)

        return findings
