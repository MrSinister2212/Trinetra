import io
import csv
import json
import hashlib
from typing import Dict, Any, List
from xhtml2pdf import pisa
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class ReportExporter:
    @staticmethod
    def export_html(rendered_html: str) -> bytes:
        return rendered_html.encode("utf-8")

    @staticmethod
    def export_pdf(rendered_html: str) -> bytes:
        """
        Converts rendered HTML with styling, watermarks, and tables into PDF bytes.
        """
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            io.BytesIO(rendered_html.encode("utf-8")),
            dest=pdf_buffer
        )
        if pisa_status.err:
            raise RuntimeError(f"PDF generation error code: {pisa_status.err}")
        return pdf_buffer.getvalue()

    @staticmethod
    def export_docx(context: Dict[str, Any]) -> bytes:
        """
        Builds a structured DOCX report document.
        """
        doc = Document()
        case = context.get("case", {})
        
        # Cover Page / Header
        title = doc.add_heading(f"TRINETRA INVESTIGATION REPORT: {case.get('title', 'OSINT Dossier')}", level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        meta_p = doc.add_paragraph()
        meta_p.add_run(f"Case ID: {case.get('id', 'N/A')}\n").bold = True
        meta_p.add_run(f"Classification: {case.get('classification', 'Confidential')}\n")
        meta_p.add_run(f"Lead Analyst: {context.get('analyst', 'Analyst')}\n")
        meta_p.add_run(f"Investigation Date: {context.get('generated_at', 'Now')}\n")
        meta_p.add_run(f"Purpose: {case.get('purpose', 'Authorized Investigation')}\n")
        doc.add_paragraph("―" * 40)

        # Executive Summary
        doc.add_heading("1. Executive Summary", level=1)
        summary_text = context.get("executive_summary", "No executive summary drafted.")
        doc.add_paragraph(summary_text)

        # Methodology & Scope
        doc.add_heading("2. Scope & Methodology", level=1)
        doc.add_paragraph(
            "This report aggregates findings collected via the TRINETRA Open Source Intelligence platform. "
            "All sources were queried using lawful, publicly available interfaces with strict privacy controls, "
            "rate limiting, and content sanitization."
        )

        # Analyst Narrative
        if context.get("analyst_narrative"):
            doc.add_heading("3. Analyst Narrative & Lead Evaluation", level=1)
            doc.add_paragraph(context.get("analyst_narrative"))

        # Findings Table
        doc.add_heading("4. Corroborated Findings & Evidence", level=1)
        findings = context.get("findings", [])
        
        table = doc.add_table(rows=1, cols=5)
        table.style = 'Light Shading Accent 1' if 'Light Shading Accent 1' in [s.name for s in doc.styles] else 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "ID"
        hdr_cells[1].text = "Module / Source"
        hdr_cells[2].text = "Confidence"
        hdr_cells[3].text = "URL"
        hdr_cells[4].text = "Evidence Snippet"

        for f in findings:
            row_cells = table.add_row().cells
            row_cells[0].text = f.id
            row_cells[1].text = f"{f.module}\n({f.source})"
            row_cells[2].text = f"{int(f.confidence * 100)}%"
            row_cells[3].text = f.exact_url
            row_cells[4].text = f.evidence_snippet

        # Hash Manifest & Chain of Custody
        doc.add_heading("5. Appendix: Chain of Custody & Hash Manifest", level=1)
        doc.add_paragraph("Tamper-evident SHA-256 evidence hashes:")
        for m in context.get("hash_manifest", []):
            doc.add_paragraph(f"[{m.get('item_id')}] {m.get('source')}: {m.get('sha256')} ({m.get('captured_at')})", style='List Bullet')

        docx_buffer = io.BytesIO()
        doc.save(docx_buffer)
        return docx_buffer.getvalue()

    @staticmethod
    def export_markdown(context: Dict[str, Any]) -> str:
        case = context.get("case", {})
        md = []
        md.append(f"# TRINETRA INVESTIGATION REPORT: {case.get('title', 'OSINT Dossier')}")
        md.append(f"**Classification:** {case.get('classification', 'Confidential')}  ")
        md.append(f"**Case ID:** `{case.get('id', 'N/A')}`  ")
        md.append(f"**Analyst:** {context.get('analyst')}  ")
        md.append(f"**Generated:** {context.get('generated_at')}  ")
        md.append(f"**Purpose:** {case.get('purpose', 'Authorized Investigation')}  \n")
        md.append("---\n")

        md.append("## 1. Executive Summary")
        md.append(context.get("executive_summary", "_No executive summary provided._") + "\n")

        if context.get("analyst_narrative"):
            md.append("## 2. Analyst Narrative & Corroboration")
            md.append(context.get("analyst_narrative") + "\n")

        md.append("## 3. Findings Index")
        md.append("| Finding ID | Target | Module | Source | Confidence | Exact URL | Verified |")
        md.append("|:---|:---|:---|:---|:---|:---|:---:|")
        for f in context.get("findings", []):
            ver = "✓" if f.verified else "✗"
            md.append(f"| `{f.id}` | `{f.target}` | {f.module} | {f.source} | {int(f.confidence*100)}% | [{f.exact_url}]({f.exact_url}) | {ver} |")
            md.append(f"> **Snippet ({f.id}):** {f.evidence_snippet}\n>")

        md.append("\n## 4. Hash Manifest & Chain of Custody")
        md.append("| Item ID | Source | SHA-256 Digest | Captured At |")
        md.append("|:---|:---|:---|:---|")
        for m in context.get("hash_manifest", []):
            md.append(f"| `{m['item_id']}` | {m['source']} | `{m['sha256']}` | {m['captured_at']} |")

        return "\n".join(md)

    @staticmethod
    def export_json(context: Dict[str, Any]) -> str:
        """
        Serializes machine-readable report schema.
        """
        serializable = dict(context)
        # Convert findings objects to dicts
        serializable["findings"] = [f.model_dump() if hasattr(f, "model_dump") else dict(f) for f in context.get("findings", [])]
        serializable["verified_findings"] = [f.model_dump() if hasattr(f, "model_dump") else dict(f) for f in context.get("verified_findings", [])]
        serializable["unverified_findings"] = [f.model_dump() if hasattr(f, "model_dump") else dict(f) for f in context.get("unverified_findings", [])]
        return json.dumps(serializable, indent=2, default=str)

    @staticmethod
    def export_csv(context: Dict[str, Any]) -> str:
        """
        Generates CSV of all findings.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Finding ID", "Target", "Module", "Source", "Confidence", "Exact URL", "Verified", "Snippet", "Reasoning", "Timestamp"])
        for f in context.get("findings", []):
            writer.writerow([
                f.id,
                f.target,
                f.module,
                f.source,
                f.confidence,
                f.exact_url,
                f.verified,
                f.evidence_snippet,
                f.confidence_reasoning,
                f.timestamp
            ])
        return output.getvalue()

    @staticmethod
    def generate_tamper_checksum(content_bytes: bytes) -> str:
        """
        Generates a SHA-256 digital checksum manifest for export files.
        """
        sha = hashlib.sha256(content_bytes).hexdigest()
        return f"# TRINETRA Tamper-Evident Report Verification\nSHA-256: {sha}\nAlgorithm: SHA256\n"
