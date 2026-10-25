import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.modules.email_domain import EmailDomainModule
from app.schemas import Finding

@pytest.fixture
def email_module():
    return EmailDomainModule()

@pytest.mark.asyncio
async def test_email_format_validation(email_module):
    findings_valid = await email_module.run("investigator@example.com", {"check_breaches": False})
    format_finding = next(f for f in findings_valid if f.source == "Email Format Validator")
    assert format_finding.verified is True
    assert format_finding.confidence == 1.0

    findings_invalid = await email_module.run("invalid..email@@domain.com", {"check_breaches": False})
    format_invalid = next(f for f in findings_invalid if f.source == "Email Format Validator")
    assert format_invalid.verified is False
    assert format_invalid.confidence < 0.5

@pytest.mark.asyncio
async def test_hibp_breach_check_no_passwords(email_module):
    mock_breaches = [
        {
            "Name": "Adobe",
            "Title": "Adobe Systems",
            "Domain": "adobe.com",
            "BreachDate": "2013-10-04",
            "PwnCount": 152445165,
            "DataClasses": ["Email addresses", "Password hints", "Usernames"]
        }
    ]

    mock_resp = httpx.Response(
        status_code=200,
        json=mock_breaches,
        request=httpx.Request("GET", "https://haveibeenpwned.com/api/v3/breachedaccount/test@example.com")
    )

    async with httpx.AsyncClient() as client:
        with patch.object(client, "get", new=AsyncMock(return_value=mock_resp)):
            findings = await email_module._check_hibp_breaches(client, "test@example.com")
            assert len(findings) == 1
            f = findings[0]
            assert f.category == "Breach Exposure"
            assert "Adobe" in f.evidence_snippet
            assert "password" not in f.evidence_snippet.lower() or "never stored or displayed" in f.evidence_snippet
            # Crucial ethical rule: no actual passwords in metadata
            assert "passwords" not in f.raw_metadata

@pytest.mark.asyncio
async def test_ct_subdomains_extraction(email_module):
    mock_ct = [
        {"name_value": "api.example.com\nexample.com"},
        {"name_value": "mail.example.com"}
    ]
    mock_resp = httpx.Response(
        status_code=200,
        json=mock_ct,
        request=httpx.Request("GET", "https://crt.sh/?q=%.example.com&output=json")
    )
    async with httpx.AsyncClient() as client:
        with patch.object(client, "get", new=AsyncMock(return_value=mock_resp)):
            findings = await email_module._check_certificate_transparency(client, "example.com")
            subdomains = [f.raw_metadata.get("subdomain") for f in findings]
            assert "api.example.com" in subdomains
            assert "mail.example.com" in subdomains
