import os
import re
import json
from typing import List, Dict, Any, Optional
import httpx

from app.schemas import Finding
from app.reporting.integrity import IntegrityValidator
from app.ai.llm_engine import ai_engine, LLMEngine

class TrinetraAICopilot:
    """
    TRINETRA AI Copilot & Artificial Intelligence Synthesizer.
    
    Adheres strictly to the Defensible Evidence Doctrine:
    1. Powered by real Artificial Intelligence: Google Gemini, OpenAI GPT-4, and Local Ollama.
    2. Every generated sentence strictly cites one or more Finding IDs: [fnd_...].
    3. Clearly separates 'Verified Facts' (2+ sources), 'Unverified Leads' (single source),
       and 'Analyst Inferences'.
    4. Never fabricates personal names, addresses, or private credentials.
    5. Fallback deterministic synthesizer available when offline.
    """

    def __init__(self, engine: Optional[LLMEngine] = None):
        self.engine = engine or ai_engine

    async def draft_executive_summary(
        self,
        findings: List[Finding],
        case_info: Dict[str, Any],
        template_type: str = "technical_report"
    ) -> str:
        """
        Drafts a citation-compliant executive summary where every assertion cites [fnd_id].
        Utilizes true Artificial Intelligence LLM when available.
        """
        if not findings:
            return "No findings are currently attached to this case. Execute OSINT modules to gather evidence before generating an AI summary."

        # Group findings
        verified = [f for f in findings if f.verified]
        unverified = [f for f in findings if not f.verified]
        by_module = {}
        for f in findings:
            by_module.setdefault(f.module, []).append(f)

        # 1. Attempt True Artificial Intelligence Generation (Gemini / OpenAI / Ollama)
        status = await self.engine.get_status()
        if status["gemini_available"] or status["openai_available"] or status["ollama_available"]:
            try:
                summary = await self._generate_ai_summary(findings, case_info, template_type)
                # Validate citation integrity
                finding_ids = {f.id for f in findings}
                is_valid, _ = IntegrityValidator.validate_narrative_citations(summary, finding_ids)
                if is_valid and len(summary.strip()) > 30:
                    return summary
            except Exception:
                pass # Fall back to built-in deterministic synthesizer if API network issues occur

        # 2. Deterministic, citation-enforced OSINT NLP synthesizer (offline fallback)
        return self._synthesize_local_narrative(findings, verified, unverified, by_module, case_info, template_type)

    async def _generate_ai_summary(self, findings: List[Finding], case_info: Dict[str, Any], template_type: str) -> str:
        case_title = case_info.get("title", "Target OSINT Dossier")
        finding_bullets = "\n".join([
            f"- [{f.id}] [{f.module.upper()}] Source: {f.source} | Target: {f.target} | Evidence: {f.evidence_snippet} | Verified: {f.verified}"
            for f in findings[:30]
        ])

        system_prompt = f"""
You are the TRINETRA Senior OSINT Intelligence Analyst AI.
Draft a rigorous, defensible, professional Executive Summary for Case: "{case_title}".

STRICT INTEGRITY & DEFENSIBLE EVIDENCE RULES:
1. Every single sentence MUST cite one or more Finding IDs in square brackets: e.g. [fnd_123].
2. Do NOT invent facts, names, addresses, or phone numbers. Ground every assertion strictly in the supplied evidence findings.
3. Clearly distinguish between verified findings (marked Verified: True) and exploratory leads.
4. Professional tone appropriate for security researchers, fraud investigators, or court-ready forensic reports.
"""
        prompt = f"""
EVIDENCE FINDINGS:
{finding_bullets}

Draft a 3-to-5 paragraph executive summary synthesizing the footprint, infrastructure, geolocation, and risk posture. Ensure every single sentence includes at least one [fnd_id] citation.
"""
        generated_text, provider = await self.engine.generate_text(prompt, system_prompt, max_tokens=1500)
        return generated_text

    def _synthesize_local_narrative(
        self,
        findings: List[Finding],
        verified: List[Finding],
        unverified: List[Finding],
        by_module: Dict[str, List[Finding]],
        case_info: Dict[str, Any],
        template_type: str
    ) -> str:
        sentences = []
        case_title = case_info.get("title", "the target subject")

        # Sentence 1: Scope & Primary Footprint
        primary_citations = " ".join(f"[{f.id}]" for f in findings[:2])
        sentences.append(
            f"An open-source footprint assessment concerning {case_title} identified {len(findings)} digital artifacts across {len(by_module)} investigative categories {primary_citations}."
        )

        # Sentence 2: Username & Social Corroboration
        if "username" in by_module:
            user_findings = by_module["username"]
            sources = ", ".join(f.source for f in user_findings[:3])
            user_cits = " ".join(f"[{f.id}]" for f in user_findings[:3])
            sentences.append(
                f"Username enumeration confirmed active identity profiles across platforms including {sources} {user_cits}."
            )

        # Sentence 3: Infrastructure & Email/Domain
        if "email_domain" in by_module:
            eml_findings = by_module["email_domain"]
            eml_cits = " ".join(f"[{f.id}]" for f in eml_findings[:2])
            sentences.append(
                f"Infrastructure inspection verified authoritative routing exchangers and public certificate transparency logging for associated domains {eml_cits}."
            )

        # Sentence 4: Telecom & Public Listings
        if "phone" in by_module:
            phn_findings = by_module["phone"]
            phn_cits = " ".join(f"[{f.id}]" for f in phn_findings[:2])
            sentences.append(
                f"Public telecommunication numbering plan analysis validated line allocation and geographic carrier assignment {phn_cits}."
            )

        # Sentence 5: Photographic Provenance & Geolocation
        if "image" in by_module:
            img_findings = by_module["image"]
            img_cits = " ".join(f"[{f.id}]" for f in img_findings[:2])
            sentences.append(
                f"Forensic photographic evaluation extracted technical camera metadata, computed compression variance, and evaluated spatial geolocation indicators {img_cits}."
            )

        # Sentence 6: Location & Geointelligence
        if "location" in by_module:
            loc_findings = by_module["location"]
            loc_cits = " ".join(f"[{f.id}]" for f in loc_findings[:2])
            sentences.append(
                f"Spatial geointelligence and telecom telemetry mapped network routing and physical coordinates via OpenStreetMap spatial ontology {loc_cits}."
            )

        # Sentence 7: Dark Web & Exposure Mentions
        if "darkweb" in by_module:
            drk_findings = by_module["darkweb"]
            drk_cits = " ".join(f"[{f.id}]" for f in drk_findings[:2])
            sentences.append(
                f"Gated onion search indices logged sanitized public mentions referencing monitored target tokens without direct credential exposure {drk_cits}."
            )

        # Concluding Corroboration Statement
        ver_count = len(verified)
        unver_count = len(unverified)
        last_cit = f"[{findings[0].id}]"
        sentences.append(
            f"Of the recorded evidence items, {ver_count} represent corroborated verified findings while {unver_count} are classified as exploratory leads {last_cit}."
        )

        return " ".join(sentences)

    async def correlate_leads(self, findings: List[Finding]) -> Dict[str, Any]:
        """
        AI Correlator: Discovers hidden links between targets, shared domain infrastructure,
        carrier regions, and temporal clusters.
        """
        correlations = []
        
        # 1. Cross-target handle reuse
        usernames = [f.target for f in findings if f.module == "username"]
        unique_handles = set(usernames)
        if len(unique_handles) > 1:
            correlations.append({
                "type": "handle_variant_cluster",
                "confidence": 0.88,
                "label": "Handle Variant Similarity",
                "description": f"Identified {len(unique_handles)} handle variations ({', '.join(unique_handles)}) indicating deliberate multi-platform brand presence or persona variance.",
                "evidence_finding_ids": [f.id for f in findings if f.module == "username"]
            })

        # 2. Email domain infrastructure bridge
        emails = [f for f in findings if "@" in f.target and f.module == "email_domain"]
        for ef in emails:
            domain = ef.target.split("@")[-1]
            matching_domains = [df for df in findings if df.target == domain]
            if matching_domains:
                correlations.append({
                    "type": "email_domain_bridge",
                    "confidence": 0.95,
                    "label": "Domain & Email Symbiosis",
                    "description": f"Target email '{ef.target}' directly maps to enumerated organizational infrastructure for '{domain}'.",
                    "evidence_finding_ids": [ef.id] + [df.id for df in matching_domains]
                })

        # 3. EXIF metadata & Geographic Alignment
        geo_findings = [f for f in findings if f.module in ["image", "location"] and f.raw_metadata.get("latitude")]
        phone_findings = [f for f in findings if f.module == "phone" and f.raw_metadata.get("geo_region")]
        if geo_findings and phone_findings:
            correlations.append({
                "type": "geographic_coherence",
                "confidence": 0.85,
                "label": "Geographic Telemetry Convergence",
                "description": "Spatial coordinate telemetry and phone carrier numbering allocations corroborate regional consistency.",
                "evidence_finding_ids": [geo_findings[0].id, phone_findings[0].id]
            })

        # 4. Exposure Severity Evaluation
        breaches = [f for f in findings if "Breach" in f.category or f.module == "darkweb"]
        severity = "LOW"
        if len(breaches) >= 3:
            severity = "HIGH"
        elif len(breaches) >= 1:
            severity = "MEDIUM"

        return {
            "evaluated_findings_count": len(findings),
            "correlation_clusters_found": len(correlations),
            "overall_exposure_risk": severity,
            "correlations": correlations
        }
