from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from app.schemas import Finding
from app.models import User
from app.auth import get_current_user
from app.ai.copilot import TrinetraAICopilot

router = APIRouter(prefix="/ai", tags=["AI Intelligence Copilot"])
copilot = TrinetraAICopilot()

class AIDraftRequest(BaseModel):
    findings: List[Finding]
    case_info: Dict[str, Any]
    template_type: str = "technical_report"

class AICorrelateRequest(BaseModel):
    findings: List[Finding]

@router.post("/draft-narrative")
async def draft_narrative(
    req: AIDraftRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Synthesizes a citation-compliant executive summary where every assertion
    strictly cites stored Finding IDs [fnd_...].
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
