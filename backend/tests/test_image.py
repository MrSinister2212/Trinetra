import io
import pytest
from PIL import Image
from app.modules.image import ImageModule

@pytest.fixture
def image_module():
    return ImageModule()

@pytest.fixture
def sample_test_image_bytes():
    # Create an in-memory JPEG test image with clean pixels
    img = Image.new("RGB", (200, 200), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

@pytest.mark.asyncio
async def test_image_ela_and_provenance(image_module, sample_test_image_bytes):
    import base64
    b64_str = "data:image/jpeg;base64," + base64.b64encode(sample_test_image_bytes).decode("utf-8")
    findings = await image_module.run(b64_str)

    assert len(findings) >= 2
    sources = [f.source for f in findings]
    assert "EXIF Metadata Extractor" in sources
    assert "Error Level Analysis (ELA)" in sources
    assert "Image Provenance Engine" in sources

    # Check ELA finding
    ela_finding = next(f for f in findings if f.source == "Error Level Analysis (ELA)")
    assert "ela_score" in ela_finding.raw_metadata
    assert 0.0 <= ela_finding.raw_metadata["ela_score"] <= 1.0

    # Ensure no facial recognition keys exist
    for f in findings:
        assert "face_id" not in f.raw_metadata
        assert "facial_landmarks" not in f.raw_metadata
