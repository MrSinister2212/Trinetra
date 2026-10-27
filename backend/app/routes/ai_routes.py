from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import base64

from app.schemas import Finding, AIChatRequest, AIConfigRequest, AIAnalyzeImageRequest
from app.models import User
from app.auth import get_current_user
from app.ai.copilot import TrinetraAICopilot
from app.ai.llm_engine import ai_engine

router = APIRouter(prefix="/ai", tags=["AI Intelligence Copilot"])
copilot = TrinetraAICopilot()

class AIDraftRequest(BaseModel):
    findings: List[Finding]
    case_info: Dict[str, Any]
    template_type: str = "technical_report"

class AICorrelateRequest(BaseModel):
    findings: List[Finding]

@router.get("/status")
async def get_ai_status(current_user: User = Depends(get_current_user)):
    """
    Returns the status of connected Artificial Intelligence engines:
    Google Gemini, OpenAI GPT-4, and Local Ollama.
    """
    return await ai_engine.get_status()

@router.post("/configure")
async def configure_ai(
    req: AIConfigRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Configures API keys and preferred models dynamically for the session.
    """
    ai_engine.update_keys(
        gemini_key=req.gemini_api_key,
        openai_key=req.openai_api_key,
        ollama_url=req.ollama_url
    )
    if req.preferred_model:
        ai_engine.preferred_model = req.preferred_model.strip()
    return await ai_engine.get_status()

@router.post("/chat")
async def copilot_chat(
    req: AIChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Interactive OSINT Copilot Chat:
    Provides real-time conversational analysis, hypothesis formulation,
    and investigation guidance grounded in collected case evidence.
    """
    res = await ai_engine.chat_with_copilot(
        user_query=req.query,
        findings=req.findings or [],
        case_info=req.case_info,
        history=req.history
    )
    return res

@router.post("/analyze-image")
async def analyze_image_ai(
    req: AIAnalyzeImageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Executes multimodal Vision AI analysis to geolocate images, transcribe text (OCR),
    and detect signs of digital manipulation or AI generation.
    """
    image_bytes = None
    mime_type = "image/jpeg"

    if req.image_base64 and "base64," in req.image_base64:
        header, b64_data = req.image_base64.split("base64,", 1)
        image_bytes = base64.b64decode(b64_data)
        if "image/png" in header:
            mime_type = "image/png"
        elif "image/webp" in header:
            mime_type = "image/webp"
    elif req.image_url:
        import httpx
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            resp = await client.get(req.image_url)
            if resp.status_code == 200:
                image_bytes = resp.content

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Could not obtain image bytes for AI vision analysis.")

    analysis = await ai_engine.analyze_image_vision(
        image_bytes=image_bytes,
        mime_type=mime_type,
        target_name=req.filename or "Uploaded Target"
    )
    return analysis

@router.post("/draft-narrative")
async def draft_narrative(
    req: AIDraftRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Synthesizes a citation-compliant executive summary where every assertion
    strictly cites stored Finding IDs [fnd_...]. Powered by real Artificial Intelligence.
    """
    summary = await copilot.draft_executive_summary(
        findings=req.findings,
        case_info=req.case_info,
        template_type=req.template_type
    )
    return {"executive_summary": summary}

@router.post("/correlate-leads")
async def correlate_leads(
    req: AICorrelateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Performs cross-platform lead correlation, infrastructure bridging,
    and threat severity calculation.
    """
    analysis = await copilot.correlate_leads(req.findings)
    return analysis
