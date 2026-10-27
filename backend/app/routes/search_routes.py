from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.audit import record_audit_log
from app.security import check_rate_limit, assess_individual_target_risk
from app.schemas import (
    Finding,
    UsernameSearchRequest,
    EmailDomainSearchRequest,
    PhoneSearchRequest,
    ImageSearchRequest,
    LocationSearchRequest,
    DarkWebSearchRequest
)

from app.modules.username import UsernameModule
from app.modules.email_domain import EmailDomainModule
from app.modules.phone import PhoneModule
from app.modules.image import ImageModule
from app.modules.location import LocationModule
from app.modules.darkweb import DarkWebModule

router = APIRouter(prefix="/search", tags=["OSINT Search Modules"])

# Instantiate singletons of modules
username_mod = UsernameModule()
email_domain_mod = EmailDomainModule()
phone_mod = PhoneModule()
image_mod = ImageModule()
location_mod = LocationModule()
darkweb_mod = DarkWebModule()

@router.get("/assess-risk")
async def assess_target_risk(
    target: str,
    module: str,
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates whether target query triggers privacy awareness under GDPR/DPDP/CCPA.
    """
    return assess_individual_target_risk(target, module)

@router.post("/username", response_model=List[Finding])
async def search_username(
    req: UsernameSearchRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Enforce purpose & affirmation
    if not req.purpose or len(req.purpose.strip()) < 5:
        raise HTTPException(status_code=400, detail="Mandatory investigation purpose required.")
    if not req.lawful_confirmation:
        raise HTTPException(status_code=400, detail="Lawful confirmation must be affirmed.")

    # Rate limiting & cooldown
    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(current_user.id, req.username)

    # Execute search
    findings = await username_mod.run(
        target=req.username,
        options={
            "generate_variants": req.generate_variants,
            "check_web_mentions": req.check_web_mentions,
            "max_sites": req.max_sites
        }
    )

    # Audit log
    await record_audit_log(
        db=db,
        user=current_user,
        action="search_username",
        target=req.username,
        module="username",
        purpose=req.purpose,
        ip_address=client_ip,
        details={"findings_count": len(findings), "variants_generated": req.generate_variants}
    )

    return findings

@router.post("/email-domain", response_model=List[Finding])
async def search_email_domain(
    req: EmailDomainSearchRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not req.purpose or len(req.purpose.strip()) < 5:
        raise HTTPException(status_code=400, detail="Mandatory investigation purpose required.")
    if not req.lawful_confirmation:
        raise HTTPException(status_code=400, detail="Lawful confirmation must be affirmed.")

    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(current_user.id, req.query)

    findings = await email_domain_mod.run(
        target=req.query,
        options={
            "check_breaches": req.check_breaches,
            "check_subdomains": req.check_subdomains,
            "check_ct_logs": req.check_ct_logs
        }
    )

    await record_audit_log(
        db=db,
        user=current_user,
        action="search_email_domain",
        target=req.query,
        module="email_domain",
        purpose=req.purpose,
        ip_address=client_ip,
        details={"findings_count": len(findings)}
    )

    return findings

@router.post("/phone", response_model=List[Finding])
async def search_phone(
    req: PhoneSearchRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not req.purpose or len(req.purpose.strip()) < 5:
        raise HTTPException(status_code=400, detail="Mandatory investigation purpose required.")
    if not req.lawful_confirmation:
        raise HTTPException(status_code=400, detail="Lawful confirmation must be affirmed.")

    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(current_user.id, req.phone_number)

    findings = await phone_mod.run(
        target=req.phone_number,
        options={"default_region": req.default_region}
    )

    await record_audit_log(
        db=db,
        user=current_user,
        action="search_phone",
        target=req.phone_number,
        module="phone",
        purpose=req.purpose,
        ip_address=client_ip,
        details={"findings_count": len(findings)}
    )

    return findings

@router.post("/image", response_model=List[Finding])
async def search_image(
    req: ImageSearchRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not req.purpose or len(req.purpose.strip()) < 5:
        raise HTTPException(status_code=400, detail="Mandatory investigation purpose required.")
    if not req.lawful_confirmation:
        raise HTTPException(status_code=400, detail="Lawful confirmation must be affirmed.")

    target = req.image_url or req.image_base64
    if not target:
        raise HTTPException(status_code=400, detail="Either image_url or image_base64 must be provided.")

    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(current_user.id, req.filename or "image_upload")

    findings = await image_mod.run(target=target, options={"filename": req.filename or "image_upload"})

    await record_audit_log(
        db=db,
        user=current_user,
        action="search_image",
        target=req.filename or "image_investigation",
        module="image",
        purpose=req.purpose,
        ip_address=client_ip,
        details={"findings_count": len(findings)}
    )

    return findings

@router.post("/location", response_model=List[Finding])
async def search_location(
    req: LocationSearchRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not req.purpose or len(req.purpose.strip()) < 5:
        raise HTTPException(status_code=400, detail="Mandatory investigation purpose required.")
    if not req.lawful_confirmation:
        raise HTTPException(status_code=400, detail="Lawful confirmation must be affirmed.")

    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(current_user.id, req.query)

    findings = await location_mod.run(target=req.query)

    await record_audit_log(
        db=db,
        user=current_user,
        action="search_location",
        target=req.query,
        module="location",
        purpose=req.purpose,
        ip_address=client_ip,
        details={"findings_count": len(findings)}
    )

    return findings

@router.post("/darkweb", response_model=List[Finding])
async def search_darkweb(
    req: DarkWebSearchRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not req.purpose or len(req.purpose.strip()) < 5:
        raise HTTPException(status_code=400, detail="Mandatory investigation purpose required.")
    if not req.lawful_confirmation:
        raise HTTPException(status_code=400, detail="Lawful confirmation must be affirmed.")

    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(current_user.id, req.query)

    # Server-side safety gate verification occurs inside DarkWebModule.run
    findings = await darkweb_mod.run(
        target=req.query,
        options={"safety_gate": req.safety_gate.model_dump()}
    )

    await record_audit_log(
        db=db,
        user=current_user,
        action="search_darkweb",
        target=req.query,
        module="darkweb",
        purpose=req.purpose,
        ip_address=client_ip,
        details={"findings_count": len(findings), "safety_gate_passed": True}
    )

    return findings
