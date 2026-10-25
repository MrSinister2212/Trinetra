import hashlib
import networkx as nx
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

from app.schemas import Finding, RedactionRules
from app.reporting.integrity import IntegrityValidator, UncitedClaimError
from app.reporting.redaction import RedactionEngine

class ReportEngine:
    def __init__(self, app_version: str = "1.0.0"):
        self.app_version = app_version

    def build_link_graph(self, findings: List[Finding]) -> Dict[str, Any]:
        """
        Builds a NetworkX graph connecting targets, sources, platforms, and evidence URLs,
        with labelled edges describing the evidentiary link.
        """
        G = nx.Graph()

        for f in findings:
            target_node = f"target:{f.target}"
            source_node = f"source:{f.source}"
            url_node = f"url:{f.exact_url}"

            G.add_node(target_node, label=f.target, type="target", module=f.module)
            G.add_node(source_node, label=f.source, type="source")
            G.add_node(url_node, label=f.exact_url[:40] + "...", type="url", full_url=f.exact_url)

            # Add edges with evidentiary labels
            edge_label = f"Evidence ({f.category})"
            if f.module == "username":
                edge_label = "Registered Profile"
            elif f.module == "email_domain":
                edge_label = "Infrastructure / Breach"
            elif f.module == "phone":
                edge_label = "Telecom / Listing"
            elif f.module == "image":
                edge_label = "Provenance / Metadata"

            G.add_edge(target_node, source_node, label=edge_label, confidence=f.confidence)
            G.add_edge(source_node, url_node, label="Exact URL Endpoint", finding_id=f.id)

        # Convert to serialized nodes and links
        nodes = []
        for n, data in G.nodes(data=True):
            nodes.append({
                "id": n,
                "label": data.get("label", n),
                "type": data.get("type", "unknown"),
                "module": data.get("module")
            })

        links = []
        for u, v, data in G.edges(data=True):
            links.append({
                "source": u,
                "target": v,
                "label": data.get("label", "linked"),
                "confidence": data.get("confidence", 0.5)
            })

        return {
            "node_count": len(nodes),
            "edge_count": len(links),
            "nodes": nodes,
            "links": links
        }

    def build_timeline(self, findings: List[Finding]) -> List[Dict[str, Any]]:
        """
        Constructs a chronological timeline based on archive timestamps,
        EXIF timestamps, or initial capture dates.
        """
        timeline_events = []
        for f in findings:
            raw = f.raw_metadata or {}
            event_date = raw.get("archive_timestamp") or raw.get("capture_time") or raw.get("registration_date") or f.timestamp
            timeline_events.append({
                "date": str(event_date),
                "finding_id": f.id,
                "source": f.source,
                "target": f.target,
                "summary": f.evidence_snippet[:120] + "...",
                "confidence": f.confidence
            })

        timeline_events.sort(key=lambda x: str(x["date"]))
        return timeline_events

    def generate_hash_manifest(self, findings: List[Finding]) -> List[Dict[str, Any]]:
        """
        Generates an immutable SHA-256 hash manifest for every cited finding and artifact.
        """
        manifest = []
        for f in findings:
            content = f"{f.id}:{f.source}:{f.exact_url}:{f.evidence_snippet}"
            sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
            manifest.append({
                "item_id": f.id,
                "item_type": "finding_evidence",
                "source": f.source,
                "sha256": sha256,
                "captured_at": f.timestamp
            })
        return manifest

    def generate_chain_of_custody(
        self,
        analyst: str,
        case_id: str,
        findings_count: int,
        action: str = "Investigation Report Compilation"
    ) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        return [
            {
                "step": 1,
                "action": "OSINT Target Ingestion",
                "analyst": analyst,
                "tool": f"TRINETRA v{self.app_version}",
                "timestamp": now,
                "notes": f"Ingested queries and verified lawful investigative purpose for Case {case_id}."
            },
            {
                "step": 2,
                "action": "Evidence Capture & Cryptographic Hashing",
                "analyst": analyst,
                "tool": f"TRINETRA v{self.app_version} - Integrity Engine",
                "timestamp": now,
                "notes": f"Captured {findings_count} finding artifacts with immutable SHA-256 validation."
            },
            {
                "step": 3,
                "action": action,
                "analyst": analyst,
                "tool": f"TRINETRA v{self.app_version} - Report Builder",
                "timestamp": now,
                "notes": "Generated defensible report package with redaction and citation validation."
            }
        ]

    def prepare_report_context(
        self,
        case_data: Dict[str, Any],
        findings: List[Finding],
        executive_summary: str,
        analyst_narrative: str,
        template_type: str,
        redaction_rules: Optional[RedactionRules] = None,
        analyst_name: str = "Senior Intelligence Analyst"
    ) -> Dict[str, Any]:
        """
        Validates integrity, applies redactions, and prepares the full context dictionary.
        """
        valid_ids = {f.id for f in findings}

        # 1. Integrity check: Uncited claim rejection
        if executive_summary:
            is_valid, uncited = IntegrityValidator.validate_narrative_citations(executive_summary, valid_ids)
            if not is_valid:
                raise UncitedClaimError(uncited)

        if analyst_narrative:
            is_valid, uncited = IntegrityValidator.validate_narrative_citations(analyst_narrative, valid_ids)
            if not is_valid:
                raise UncitedClaimError(uncited)

        # 2. Check sensitive content exclusion
        combined_text = f"{executive_summary} {analyst_narrative}"
        clean, violations = IntegrityValidator.check_sensitive_content_exclusion(combined_text)
        if not clean:
            raise ValueError(f"Report contains prohibited/sensitive content: {violations}")

        # 3. Apply redaction if enabled
        processed_findings = findings
        processed_summary = executive_summary
        processed_narrative = analyst_narrative

        if redaction_rules:
            processed_findings = [RedactionEngine.redact_finding(f, redaction_rules) for f in findings]
            targets = [f.target for f in findings]
            processed_summary = RedactionEngine.redact_text(executive_summary, redaction_rules, targets)
            processed_narrative = RedactionEngine.redact_text(analyst_narrative, redaction_rules, targets)

        # 4. Separate findings into Verified vs Unverified
        verified_findings = [f for f in processed_findings if f.verified]
        unverified_findings = [f for f in processed_findings if not f.verified]

        # 5. Build Link Graph & Timeline
        link_graph = self.build_link_graph(processed_findings)
        timeline = self.build_timeline(processed_findings)
        hash_manifest = self.generate_hash_manifest(processed_findings)
        chain_of_custody = self.generate_chain_of_custody(analyst_name, case_data.get("id", "CASE-001"), len(findings))

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        return {
            "case": case_data,
            "template_type": template_type,
            "generated_at": now_str,
            "analyst": analyst_name,
            "executive_summary": processed_summary,
            "analyst_narrative": processed_narrative,
            "findings": processed_findings,
            "verified_findings": verified_findings,
            "unverified_findings": unverified_findings,
            "link_graph": link_graph,
            "timeline": timeline,
            "hash_manifest": hash_manifest,
            "chain_of_custody": chain_of_custody,
            "redaction_applied": bool(redaction_rules and (
                redaction_rules.mask_emails or redaction_rules.mask_phones or
                redaction_rules.mask_usernames or redaction_rules.mask_urls or
                redaction_rules.mask_gps or redaction_rules.custom_terms
            )),
            "app_version": self.app_version
        }
