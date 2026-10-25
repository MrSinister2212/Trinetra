import pytest
import os
from unittest.mock import AsyncMock, patch
import httpx

from app.modules.username import UsernameModule
from app.schemas import Finding

@pytest.fixture
def username_module():
    return UsernameModule()

def test_variant_generation(username_module):
    variants = username_module.generate_variants("batman")
    assert "batman" in variants
    assert "batman_" in variants
    assert "b4tman" in variants
    assert "batman123" in variants
    assert "the_batman" in variants

@pytest.mark.asyncio
async def test_username_site_check_found(username_module):
    site = {
        "name": "GitHub",
        "category": "Code & Dev",
        "url": "https://github.com/{}",
        "check_type": "status_code",
        "error_code": 404,
        "rank": 1
    }

    mock_resp = httpx.Response(
        status_code=200,
        text="<html><title>batman (Bruce Wayne) · GitHub</title><body>batman profile</body></html>",
        request=httpx.Request("GET", "https://github.com/batman")
    )

    async with httpx.AsyncClient() as client:
        with patch.object(client, "get", new=AsyncMock(return_value=mock_resp)):
            finding = await username_module._check_single_site(client, site, "batman")
            assert finding is not None
            assert isinstance(finding, Finding)
            assert finding.source == "GitHub"
            assert finding.exact_url == "https://github.com/batman"
            assert finding.confidence >= 0.85
            assert finding.verified is True
            assert "batman" in finding.evidence_snippet.lower()

@pytest.mark.asyncio
async def test_username_site_check_not_found(username_module):
    site = {
        "name": "GitHub",
        "category": "Code & Dev",
        "url": "https://github.com/{}",
        "check_type": "status_code",
        "error_code": 404,
        "rank": 1
    }

    mock_resp = httpx.Response(
        status_code=404,
        text="Not Found",
        request=httpx.Request("GET", "https://github.com/nonexistentuser999")
    )

    async with httpx.AsyncClient() as client:
        with patch.object(client, "get", new=AsyncMock(return_value=mock_resp)):
            finding = await username_module._check_single_site(client, site, "nonexistentuser999")
            assert finding is None
