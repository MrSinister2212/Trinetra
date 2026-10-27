import pytest
from app.modules.location import LocationModule

@pytest.fixture
def location_module():
    return LocationModule()

@pytest.mark.asyncio
async def test_detect_target_types(location_module):
    assert location_module._detect_target_type("37.7749, -122.4194") == "coordinates"
    assert location_module._detect_target_type("8.8.8.8") == "ip"
    assert location_module._detect_target_type("2001:4860:4860::8888") == "ip"
    assert location_module._detect_target_type("github.com") == "domain"
    assert location_module._detect_target_type("1600 Pennsylvania Ave, Washington, DC") == "address"

@pytest.mark.asyncio
async def test_location_run_ip(location_module):
    findings = await location_module.run("8.8.8.8")
    assert len(findings) >= 1
    f = findings[0]
    assert f.module == "location"
    assert f.category == "Geolocation"
    assert "latitude" in f.raw_metadata
    assert "longitude" in f.raw_metadata
    assert "country" in f.raw_metadata

@pytest.mark.asyncio
async def test_location_run_coordinates(location_module):
    findings = await location_module.run("48.8584, 2.2945")
    assert len(findings) >= 1
    f = findings[0]
    assert f.category == "Geolocation"
    assert "latitude" in f.raw_metadata
    assert "osm_url" in f.raw_metadata
