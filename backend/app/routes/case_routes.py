from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, Case, FindingRecord
from app.schemas import CaseCreate, CaseUpdate, CaseResponse, FindingCreate, Finding
from app.auth import get_current_user
from app.audit import record_audit_log

router = APIRouter(prefix="/cases", tags=["Case Management"])

@router.get("", response_model=List[CaseResponse])
async def list_cases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Case).options(selectinload(Case.findings)).order_by(Case.created_at.desc())
    result = await db.execute(query)
    cases = result.scalars().all()
    return cases

@router.post("", response_model=CaseResponse)
async def create_case(
    case_in: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_case = Case(
        title=case_in.title,
        description=case_in.description or "",
        investigator=case_in.investigator or current_user.username,
        classification=case_in.classification or "Confidential",
        tags=case_in.tags or [],
        notes=[]
    )
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)

    await record_audit_log(
        db=db,
        user=current_user,
        action="create_case",
        target=new_case.id,
        module="cases",
        purpose="Case Dossier Initialization",
        details={"title": new_case.title, "classification": new_case.classification}
    )

    return new_case

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Case).where(Case.id == case_id).options(selectinload(Case.findings))
    result = await db.execute(query)
    case = result.scalars().first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    update_in: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Case).where(Case.id == case_id).options(selectinload(Case.findings))
    result = await db.execute(query)
    case = result.scalars().first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if update_in.title is not None:
        case.title = update_in.title
    if update_in.description is not None:
        case.description = update_in.description
    if update_in.classification is not None:
        case.classification = update_in.classification
    if update_in.status is not None:
        case.status = update_in.status
    if update_in.tags is not None:
        case.tags = update_in.tags
    if update_in.notes is not None:
        case.notes = update_in.notes

    await db.commit()
    await db.refresh(case)
    return case

@router.post("/{case_id}/findings", response_model=Finding)
async def add_finding_to_case(
    case_id: str,
    finding_in: FindingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify case exists
    query = select(Case).where(Case.id == case_id)
    result = await db.execute(query)
    case = result.scalars().first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    finding_record = FindingRecord(
        case_id=case_id,
        source=finding_in.source,
        exact_url=finding_in.exact_url,
        evidence_snippet=finding_in.evidence_snippet,
        confidence=finding_in.confidence,
        confidence_reasoning=finding_in.confidence_reasoning or "",
        timestamp=finding_in.timestamp or "now",
        module=finding_in.module,
        target=finding_in.target,
        category=finding_in.category or "general",
        verified=finding_in.verified or False,
        raw_metadata=finding_in.raw_metadata or {}
    )
    db.add(finding_record)
    await db.commit()
    await db.refresh(finding_record)

    await record_audit_log(
        db=db,
        user=current_user,
        action="add_finding_to_case",
        target=finding_record.id,
        module="cases",
        purpose="Evidence Attached to Case",
        details={"case_id": case_id, "exact_url": finding_record.exact_url}
    )

    return finding_record
