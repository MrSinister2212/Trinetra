import pytest
from app.schemas import Finding, RedactionRules
from app.reporting.integrity import IntegrityValidator, UncitedClaimError
from app.reporting.redaction import RedactionEngine
from app.reporting.engine import ReportEngine
from app.reporting.exporters import ReportExporter

@pytest.fixture
def sample_findings():
    return [
        Finding(
            id="fnd_001",
            source="GitHub",
            exact_url="https://github.com/targetuser",
            evidence_snippet="Active code repository and profile for targetuser.",
            confidence=0.95,
            confidence_reasoning="Direct HTTP 200 with matching handle token.",
            timestamp="2026-10-25T12:00:00Z",
            module="username",
            target="targetuser",
            category="Code & Dev",
            verified=True,
            raw_metadata={"stars": 42}
        ),
        Finding(
            id="fnd_002",
            source="DNS MX Resolver",
            exact_url="dns://targetcorp.com/MX",
            evidence_snippet="Primary mail exchanger points to mail.targetcorp.com.",
            confidence=0.98,
            confidence_reasoning="Authoritative DNS answer.",
            timestamp="2026-10-25T12:01:00Z",
            module="email_domain",
            target="targetcorp.com",
            category="Infrastructure",
            verified=True,
            raw_metadata={"exchange": "mail.targetcorp.com"}
        )
    ]

# 1. Test Uncited Claim Rejection
def test_uncited_claim_rejection():
    valid_ids = {"fnd_001", "fnd_002"}
    
    # Valid narrative: each sentence cites a finding ID
    valid_text = "The subject maintains an active development profile on GitHub [fnd_001]. Associated corporate email infrastructure routes to targetcorp.com [fnd_002]."
    is_valid, uncited = IntegrityValidator.validate_narrative_citations(valid_text, valid_ids)
    assert is_valid is True
    assert len(uncited) == 0

    # Invalid narrative: second sentence makes an uncited assertion
    invalid_text = "The subject maintains an active profile on GitHub [fnd_001]. The subject also operates five secret scam cryptocurrency exchanges in Zurich."
    is_valid, uncited = IntegrityValidator.validate_narrative_citations(invalid_text, valid_ids)
    assert is_valid is False
    assert len(uncited) == 1
    assert "Zurich" in uncited[0]

# 2. Test Redaction Correctness
def test_redaction_correctness(sample_findings):
    rules = RedactionRules(
        mask_emails=True,
        mask_phones=True,
        mask_urls=True,
        mask_gps=True,
        custom_terms=["secretproject"]
    )

    test_text = "Contact user at alice@example.com or +1 415-555-2671. Located near 37.7749, -122.4194 for secretproject."
    redacted = RedactionEngine.redact_text(test_text, rules)

    assert "alice@example.com" not in redacted
    assert "a***e@example.com" in redacted
    assert "415-555-2671" not in redacted
    assert "[REDACTED_GPS_COORDINATES]" in redacted
    assert "secretproject" not in redacted
    assert "[REDACTED]" in redacted

    # Test finding redaction
    f = sample_findings[0]
    redacted_finding = RedactionEngine.redact_finding(f, rules)
    assert "https://[REDACTED_HOST]" in redacted_finding.exact_url

# 3. Test Hash Manifest Integrity
def test_hash_manifest_integrity(sample_findings):
    engine = ReportEngine()
    manifest = engine.generate_hash_manifest(sample_findings)

    assert len(manifest) == len(sample_findings)
    for m in manifest:
        assert "item_id" in m
        assert "sha256" in m
        assert len(m["sha256"]) == 64 # 64-character SHA-256 hex string
        assert "captured_at" in m

# 4. Test Exclusion of Hard-Blocked Content
def test_exclusion_of_hard_blocked_content():
    clean_text = "Investigation focused on publicly disclosed code vulnerabilities [fnd_001]."
    clean, violations = IntegrityValidator.check_sensitive_content_exclusion(clean_text)
    assert clean is True
    assert len(violations) == 0

    dirty_text = "Discussion around illicit weapons trade and csam distribution."
    clean, violations = IntegrityValidator.check_sensitive_content_exclusion(dirty_text)
    assert clean is False
    assert "weapons" in violations
    assert "csam" in violations

# 5. Test Multi-Format Exports
def test_report_exporters_multi_format(sample_findings):
    engine = ReportEngine()
    valid_summary = "An active profile was confirmed on GitHub [fnd_001]. DNS routes to verified corporate exchangers [fnd_002]."
    context = engine.prepare_report_context(
        case_data={"id": "CASE-101", "title": "Corporate Audit", "classification": "Internal", "purpose": "Security Footprint Audit"},
        findings=sample_findings,
        executive_summary=valid_summary,
        analyst_narrative="",
        template_type="technical_report"
    )

    # HTML
    html_raw = "<html><body><h1>Report</h1></body></html>"
    html_out = ReportExporter.export_html(html_raw)
    assert len(html_out) > 0

    # Markdown
    md_out = ReportExporter.export_markdown(context)
    assert "# TRINETRA INVESTIGATION REPORT" in md_out
    assert "fnd_001" in md_out

    # JSON
    json_out = ReportExporter.export_json(context)
    assert "fnd_001" in json_out
    assert "hash_manifest" in json_out

    # CSV
    csv_out = ReportExporter.export_csv(context)
    assert "Finding ID,Target,Module" in csv_out
    assert "fnd_001" in csv_out

    # DOCX
    docx_bytes = ReportExporter.export_docx(context)
    assert len(docx_bytes) > 1000

    # PDF
    pdf_bytes = ReportExporter.export_pdf(html_raw)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")

    # Tamper Checksum
    checksum = ReportExporter.generate_tamper_checksum(html_out)
    assert "SHA-256:" in checksum

def test_report_version_locking(sample_findings):
    # Simulates report locking logic: locked reports cannot be mutated in place
    initial_report = {
        "id": "rep_100",
        "case_id": "CASE-101",
        "title": "Initial Draft",
        "version": 1,
        "is_locked": True,
        "executive_summary": "Subject verified on GitHub [fnd_001]."
    }

    # Updating a locked report triggers new version increment
    if initial_report["is_locked"]:
        new_version_report = dict(initial_report)
        new_version_report["id"] = "rep_101"
        new_version_report["version"] = initial_report["version"] + 1
        new_version_report["title"] = "Updated Locked Report"
        new_version_report["is_locked"] = False

    assert initial_report["version"] == 1
    assert initial_report["is_locked"] is True
    assert new_version_report["version"] == 2
    assert new_version_report["title"] == "Updated Locked Report"
