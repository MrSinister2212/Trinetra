import pytest
import os
from unittest.mock import AsyncMock, patch
import httpx
from fastapi import HTTPException

from app.modules.darkweb import DarkWebModule

@pytest.fixture
def darkweb_module():
    return DarkWebModule()

@pytest.mark.asyncio
async def test_safety_gate_rejection_on_missing_box(darkweb_module):
    # Missing 'amnesic_os_or_isolated_vm'
    incomplete_gate = {
        "amnesic_os_or_isolated_vm": False,
        "hardware_devices_disabled": True,
        "tor_connection_active": True,
        "no_personal_accounts_logged": True,
        "no_file_downloads_agreed": True,
        "lawful_purpose_accepted": True
    }

    async with httpx.AsyncClient() as client:
        with pytest.raises(HTTPException) as exc_info:
            await darkweb_module.verify_safety_gate(incomplete_gate, client)
        assert exc_info.value.status_code == 403
        assert "amnesic_os_or_isolated_vm" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_safety_gate_tor_backend_verification(darkweb_module):
    all_boxes_ticked = {
        "amnesic_os_or_isolated_vm": True,
        "hardware_devices_disabled": True,
        "tor_connection_active": True,
        "no_personal_accounts_logged": True,
        "no_file_downloads_agreed": True,
        "lawful_purpose_accepted": True
    }

    # Simulate check.torproject.org saying IsTor = False
    mock_resp = httpx.Response(
        status_code=200,
        json={"IsTor": False, "IP": "198.51.100.1"},
        request=httpx.Request("GET", "https://check.torproject.org/api/ip")
    )

    # Disable test mode bypass during this specific test
    with patch.dict(os.environ, {"TRINETRA_TEST_MODE": "0"}):
        async with httpx.AsyncClient() as client:
            with patch.object(client, "get", new=AsyncMock(return_value=mock_resp)):
                with pytest.raises(HTTPException) as exc_info:
                    await darkweb_module.verify_safety_gate(all_boxes_ticked, client)
                assert exc_info.value.status_code == 403
                assert "active connection through the Tor network" in str(exc_info.value.detail)

def test_hard_block_filtering(darkweb_module):
    # CSAM keyword
    assert darkweb_module.is_hard_blocked("monitored child abuse leak site", "http://someonion.onion") is True
    # Weapons keyword
    assert darkweb_module.is_hard_blocked("market selling glock and ammunition", "http://someonion.onion") is True
    # Illicit fentanyl / cocaine
    assert darkweb_module.is_hard_blocked("vendor offering pure fentanyl", "http://someonion.onion") is True
    # Hitman for hire
    assert darkweb_module.is_hard_blocked("anonymous contract killer service", "http://someonion.onion") is True
    # Clean brand mention
    assert darkweb_module.is_hard_blocked("BrandName company leak pastebin discussion", "http://cleanonion.onion") is False

def test_script_stripping_and_sanitization(darkweb_module):
    dirty_html = '<h3>Leak <script>alert("xss")</script><style>body{color:red}</style><b>Alert</b></h3>'
    cleaned = darkweb_module.sanitize_snippet(dirty_html)
    assert "<script>" not in cleaned
    assert "alert" not in cleaned
    assert "<style>" not in cleaned
    assert "Leak Alert" in cleaned
