import pytest
from app.modules.phone import PhoneModule
from app.schemas import Finding

@pytest.fixture
def phone_module():
    return PhoneModule()

@pytest.mark.asyncio
async def test_valid_phone_parsing(phone_module):
    # Google headquarters public number
    target = "+1 650 253 0000"
    findings = await phone_module.run(target)
    assert len(findings) >= 1

    primary = findings[0]
    assert primary.module == "phone"
    assert primary.confidence >= 0.90
    assert primary.verified is True
    assert primary.raw_metadata["e164"] == "+16502530000"
    assert primary.raw_metadata["country_code"] == 1
    assert "Fixed Line" in primary.raw_metadata["line_type"] or "Mobile" in primary.raw_metadata["line_type"] or "Fixed Line or Mobile" in primary.raw_metadata["line_type"]

    # Strict compliance verification: No personal name or private location
    assert "person_name" not in primary.raw_metadata
    assert "photo" not in primary.raw_metadata
    assert "real_time_gps" not in primary.raw_metadata

@pytest.mark.asyncio
async def test_invalid_phone_number(phone_module):
    findings = await phone_module.run("not-a-number")
    assert len(findings) == 1
    assert findings[0].confidence <= 0.2
    assert "Invalid phone number" in findings[0].evidence_snippet
