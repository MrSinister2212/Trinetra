import os
import json
from jinja2 import Environment, FileSystemLoader

from app.schemas import Finding, RedactionRules
from app.reporting.engine import ReportEngine
from app.reporting.exporters import ReportExporter

def generate_samples():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_reports")
    os.makedirs(out_dir, exist_ok=True)

    templates_dir = os.path.join(os.path.dirname(__file__), "app", "reporting", "templates")
    jinja_env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)

    mock_findings = [
        Finding(
            id="fnd_usr_01",
            source="GitHub",
            exact_url="https://github.com/alex-devsec",
            evidence_snippet="Active public profile with 38 repositories, member of DevSecOps org. Last commit 2 days ago.",
            confidence=0.96,
            confidence_reasoning="Direct profile HTTP 200 with matching bio token.",
            timestamp="2026-10-25T14:10:00Z",
            module="username",
            target="alex-devsec",
            category="Code & Dev",
            verified=True,
            raw_metadata={"public_repos": 38, "followers": 112}
        ),
        Finding(
            id="fnd_usr_02",
            source="Twitter/X",
            exact_url="https://x.com/alex_devsec",
            evidence_snippet="Verified handle claiming Security Researcher role. Pinned thread links to personal portfolio.",
            confidence=0.91,
            confidence_reasoning="Handle exact match on primary social platform.",
            timestamp="2026-10-25T14:11:15Z",
            module="username",
            target="alex_devsec",
            category="Social",
            verified=True,
            raw_metadata={"variant_of": "alex-devsec"}
        ),
        Finding(
            id="fnd_eml_01",
            source="DNS MX Resolver",
            exact_url="dns://alex-security.io/MX",
            evidence_snippet="Mail exchangers resolve to Google Workspace (aspmx.l.google.com). SPF record enforced.",
            confidence=0.99,
            confidence_reasoning="Authoritative DNS MX query confirmed active routing.",
            timestamp="2026-10-25T14:12:00Z",
            module="email_domain",
            target="alex-security.io",
            category="Infrastructure",
            verified=True,
            raw_metadata={"priority": 1, "exchange": "aspmx.l.google.com"}
        ),
        Finding(
            id="fnd_eml_02",
            source="crt.sh Certificate Transparency",
            exact_url="https://api.alex-security.io",
            evidence_snippet="Discovered active subdomain api.alex-security.io logged in Let's Encrypt certificate transparency audit log.",
            confidence=0.95,
            confidence_reasoning="Cryptographic TLS issuance record in global CT log.",
            timestamp="2026-10-25T14:12:30Z",
            module="email_domain",
            target="alex-security.io",
            category="Infrastructure",
            verified=True,
            raw_metadata={"subdomain": "api.alex-security.io"}
        ),
        Finding(
            id="fnd_phn_01",
            source="ITU-T Telecommunication Registry",
            exact_url="tel:+14155552671",
            evidence_snippet="Valid North American mobile number (+1 415-555-2671). Assigned carrier range: T-Mobile USA. Region: San Francisco, California.",
            confidence=0.98,
            confidence_reasoning="Authoritative libphonenumber E.164 syntax and carrier range allocation.",
            timestamp="2026-10-25T14:14:00Z",
            module="phone",
            target="+1 415-555-2671",
            category="Telecom Metadata",
            verified=True,
            raw_metadata={"line_type": "Mobile", "carrier": "T-Mobile USA"}
        ),
        Finding(
            id="fnd_img_01",
            source="EXIF Metadata Extractor",
            exact_url="embedded://media/headshot.jpg",
            evidence_snippet="Camera: Sony A7 IV. Exposure: 1/250s at f/2.8. Captured: 2025-08-14 16:22:10. Software: Lightroom v12.1. GPS coordinates embedded in header: 37.7749, -122.4194.",
            confidence=0.97,
            confidence_reasoning="Parsed direct EXIF tags from supplied artifact.",
            timestamp="2026-10-25T14:16:00Z",
            module="image",
            target="headshot.jpg",
            category="Metadata",
            verified=True,
            raw_metadata={"camera": "Sony A7 IV", "gps": {"latitude": 37.7749, "longitude": -122.4194}}
        ),
        Finding(
            id="fnd_drk_01",
            source="Ahmia Onion Search Index",
            exact_url="http://pasteonionexample5xyz.onion/raw/alex-sec",
            evidence_snippet="Metadata mention: Public pastebin repository referencing monitored domain alex-security.io. [Scripts stripped, media download blocked]",
            confidence=0.82,
            confidence_reasoning="Indexed public onion search hit referencing monitored domain string.",
            timestamp="2026-10-25T14:18:00Z",
            module="darkweb",
            target="alex-security.io",
            category="Dark Web Mention",
            verified=False,
            raw_metadata={"sanitized": True}
        )
    ]

    case_data = {
        "id": "CASE-2026-0881",
        "title": "Comprehensive Digital Footprint & Threat Assessment",
        "investigator": "Chief OSINT Specialist M. Sharma",
        "classification": "Confidential",
        "purpose": "Authorized Digital Footprint Assessment & Identity Corroboration"
    }

    # Strict citation-compliant summary
    executive_summary = (
        "An investigation into target entities confirmed active development presence on GitHub [fnd_usr_01]. "
        "Associated social footprint was corroborated on Twitter/X under handle variant alex_devsec [fnd_usr_02]. "
        "Domain infrastructure routing was validated via DNS MX exchangers [fnd_eml_01] and Certificate Transparency logs [fnd_eml_02]. "
        "Public telecommunication records map the associated inquiry number to a California mobile allocation [fnd_phn_01]. "
        "Forensic image evaluation extracted metadata confirming capture via Sony A7 IV [fnd_img_01]. "
        "Gated onion indexing noted a single historical text paste mentioning the corporate domain [fnd_drk_01]."
    )

    analyst_narrative = (
        "The subject exhibits a high-visibility open-source development profile [fnd_usr_01]. "
        "Infrastructure analysis reveals consistent deployment of enterprise security controls including Google Workspace and TLS certificates [fnd_eml_01] [fnd_eml_02]. "
        "All findings represent publicly indexable entries gathered under lawful purpose [fnd_usr_01]."
    )

    engine = ReportEngine(app_version="1.0.0")
    context = engine.prepare_report_context(
        case_data=case_data,
        findings=mock_findings,
        executive_summary=executive_summary,
        analyst_narrative=analyst_narrative,
        template_type="technical_report",
        analyst_name="Chief OSINT Specialist M. Sharma"
    )

    template = jinja_env.get_template("technical_report.html")
    rendered_html = template.render(context)

    # 1. HTML
    html_file = os.path.join(out_dir, "sample_report.html")
    with open(html_file, "wb") as f:
        f.write(ReportExporter.export_html(rendered_html))
    print(f"Generated: {html_file}")

    # 2. PDF
    pdf_file = os.path.join(out_dir, "sample_report.pdf")
    with open(pdf_file, "wb") as f:
        f.write(ReportExporter.export_pdf(rendered_html))
    print(f"Generated: {pdf_file}")

    # 3. DOCX
    docx_file = os.path.join(out_dir, "sample_report.docx")
    with open(docx_file, "wb") as f:
        f.write(ReportExporter.export_docx(context))
    print(f"Generated: {docx_file}")

    # 4. Markdown
    md_file = os.path.join(out_dir, "sample_report.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(ReportExporter.export_markdown(context))
    print(f"Generated: {md_file}")

    # 5. JSON
    json_file = os.path.join(out_dir, "sample_report.json")
    with open(json_file, "w", encoding="utf-8") as f:
        f.write(ReportExporter.export_json(context))
    print(f"Generated: {json_file}")

    # 6. CSV
    csv_file = os.path.join(out_dir, "sample_report.csv")
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write(ReportExporter.export_csv(context))
    print(f"Generated: {csv_file}")

    # 7. Checksum SHA-256
    sha_file = os.path.join(out_dir, "sample_report.sha256")
    with open(sha_file, "w", encoding="utf-8") as f:
        f.write(ReportExporter.generate_tamper_checksum(rendered_html.encode("utf-8")))
    print(f"Generated: {sha_file}")

    print("All sample reports generated successfully!")

if __name__ == "__main__":
    generate_samples()
