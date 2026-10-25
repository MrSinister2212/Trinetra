import pytest
from app.schemas import Finding
from app.ai.copilot import TrinetraAICopilot
from app.reporting.integrity import IntegrityValidator

@pytest.fixture
def copilot():
    return TrinetraAICopilot()

@pytest.fixture
def mock_findings():
    return [
        Finding(
            id="fnd_001",
            source="GitHub",
            exact_url="https://github.com/alex-sec",
            evidence_snippet="Active developer repository.",
            confidence=0.95,
            confidence_reasoning="Handle verified on GitHub.",
            timestamp="2026-10-25T12:00:00Z",
            module="username",
            target="alex-sec",
            category="Code & Dev",
            verified=True
        ),
        Finding(
            id="fnd_002",
            source="DNS MX Resolver",
            exact_url="dns://alex-security.io/MX",
            evidence_snippet="Active mail exchangers for alex-security.io.",
            confidence=0.98,
            confidence_reasoning="DNS MX answered.",
            timestamp="2026-10-25T12:01:00Z",
            module="email_domain",
            target="alex-security.io",
            category="Infrastructure",
            verified=True
        ),
        Finding(
            id="fnd_003",
            source="Ahmia Onion Search Index",
            exact_url="http://pasteexample.onion/raw",
            evidence_snippet="Pastebin mention of alex-security.io.",
            confidence=0.75,
            confidence_reasoning="Onion index match.",
            timestamp="2026-10-25T12:02:00Z",
            module="darkweb",
            target="alex-security.io",
            category="Dark Web Mention",
            verified=False
        )
    ]

@pytest.mark.asyncio
async def test_ai_draft_adheres_to_citations(copilot, mock_findings):
    case_info = {"title": "Operation Horizon", "id": "CASE-01"}
    summary = await copilot.draft_executive_summary(mock_findings, case_info)

    assert len(summary) > 50
    # Every sentence must pass strict citation validation
    is_valid, uncited = IntegrityValidator.validate_narrative_citations(summary, {f.id for f in mock_findings})
    assert is_valid is True
    assert len(uncited) == 0

@pytest.mark.asyncio
async def test_ai_lead_correlation(copilot, mock_findings):
    correlation = await copilot.correlate_leads(mock_findings)

    assert correlation["evaluated_findings_count"] == 3
    assert "overall_exposure_risk" in correlation
    assert correlation["overall_exposure_risk"] in ["LOW", "MEDIUM", "HIGH"]
