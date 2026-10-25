import os
from jinja2 import Environment, FileSystemLoader
from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, Case, FindingRecord, ReportRecord
from app.schemas import ReportCreate, ReportUpdate, ReportResponse, Finding, RedactionRules
from app.auth import get_current_user
from app.audit import record_audit_log
from app.reporting.engine import ReportEngine
from app.reporting.exporters import ReportExporter
from app.reporting.integrity import UncitedClaimError

router = APIRouter(prefix="/reports", tags=["Report Generation & Export"])

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reporting", "templates")
jinja_env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
report_engine = ReportEngine()

@router.post("", response_model=ReportResponse)
async def create_report(
    report_in: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify case exists
    query = select(Case).where(Case.id == report_in.case_id).options(selectinload(Case.findings))
    result = await db.execute(query)
    case = result.scalars().first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Get findings to include (either explicitly requested or all findings in case)
    if report_in.finding_ids:
        findings_to_use = [f for f in case.findings if f.id in report_in.finding_ids]
    else:
        findings_to_use = case.findings

    finding_objs = [
        Finding(
            id=f.id,
            source=f.source,
            exact_url=f.exact_url,
            evidence_snippet=f.evidence_snippet,
            confidence=f.confidence,
            confidence_reasoning=f.confidence_reasoning or "",
            timestamp=f.timestamp,
            module=f.module,
            target=f.target,
            category=f.category,
            verified=f.verified,
            raw_metadata=f.raw_metadata or {}
        )
        for f in findings_to_use
    ]

    # Run ReportEngine to prepare context and validate citations & sensitive exclusions
    try:
        context = report_engine.prepare_report_context(
            case_data={
                "id": case.id,
                "title": case.title,
                "classification": case.classification,
                "purpose": report_in.purpose
            },
            findings=finding_objs,
            executive_summary=report_in.executive_summary or "",
            analyst_narrative=report_in.analyst_narrative or "",
            template_type=report_in.template_type,
            redaction_rules=report_in.redaction_rules,
            analyst_name=current_user.username
        )
    except UncitedClaimError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Integrity Rejection: Uncited claim(s) detected. Every assertion must cite stored Finding IDs. Violations: {e.uncited_sentences}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Save ReportRecord
    new_report = ReportRecord(
        case_id=case.id,
        title=report_in.title,
        template_type=report_in.template_type,
        version=1,
        is_locked=report_in.lock_report,
        executive_summary=report_in.executive_summary or "",
        analyst_narrative=report_in.analyst_narrative or "",
        finding_ids=[f.id for f in finding_objs],
        redaction_rules=report_in.redaction_rules.model_dump() if report_in.redaction_rules else {},
        hash_manifest=context["hash_manifest"],
        chain_of_custody=context["chain_of_custody"],
        purpose=report_in.purpose,
        integrity_status="valid"
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)

    # Audited action
    await record_audit_log(
        db=db,
        user=current_user,
        action="generate_report",
        target=new_report.id,
        module="reporting",
        purpose=report_in.purpose,
        details={
            "case_id": case.id,
            "template": report_in.template_type,
            "version": 1,
            "included_findings_count": len(finding_objs),
            "redacted": context["redaction_applied"]
        }
    )

    return new_report

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(ReportRecord).where(ReportRecord.id == report_id)
    result = await db.execute(query)
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    update_in: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(ReportRecord).where(ReportRecord.id == report_id)
    result = await db.execute(query)
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Version Locking Rule: If locked, changes automatically create a new version!
    if report.is_locked:
        # Clone report as version + 1
        new_version = ReportRecord(
            case_id=report.case_id,
            title=update_in.title or report.title,
            template_type=report.template_type,
            version=report.version + 1,
            is_locked=update_in.lock_report if update_in.lock_report is not None else False,
            executive_summary=update_in.executive_summary if update_in.executive_summary is not None else report.executive_summary,
            analyst_narrative=update_in.analyst_narrative if update_in.analyst_narrative is not None else report.analyst_narrative,
            finding_ids=update_in.finding_ids if update_in.finding_ids is not None else report.finding_ids,
            redaction_rules=update_in.redaction_rules.model_dump() if update_in.redaction_rules else report.redaction_rules,
            hash_manifest=report.hash_manifest,
            chain_of_custody=report.chain_of_custody,
            purpose=report.purpose,
            integrity_status="valid"
        )
        db.add(new_version)
        await db.commit()
        await db.refresh(new_version)
        return new_version

    # Report is not locked, can be modified directly
    if update_in.title is not None:
        report.title = update_in.title
    if update_in.executive_summary is not None:
        report.executive_summary = update_in.executive_summary
    if update_in.analyst_narrative is not None:
        report.analyst_narrative = update_in.analyst_narrative
    if update_in.finding_ids is not None:
        report.finding_ids = update_in.finding_ids
    if update_in.redaction_rules is not None:
        report.redaction_rules = update_in.redaction_rules.model_dump()
    if update_in.lock_report is not None:
        report.is_locked = update_in.lock_report

    await db.commit()
    await db.refresh(report)
    return report

@router.get("/{report_id}/export/{export_format}")
async def export_report(
    report_id: str,
    export_format: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exports report in requested format: html, pdf, docx, md, json, csv, sha256.
    """
    export_format = export_format.lower()
    valid_formats = ["html", "pdf", "docx", "md", "markdown", "json", "csv", "sha256"]
    if export_format not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Invalid format '{export_format}'. Allowed: {valid_formats}")

    query = select(ReportRecord).where(ReportRecord.id == report_id).options(selectinload(ReportRecord.case).selectinload(Case.findings))
    result = await db.execute(query)
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    case = report.case
    included_ids = set(report.finding_ids)
    selected_findings = [
        Finding(
            id=f.id,
            source=f.source,
            exact_url=f.exact_url,
            evidence_snippet=f.evidence_snippet,
            confidence=f.confidence,
            confidence_reasoning=f.confidence_reasoning or "",
            timestamp=f.timestamp,
            module=f.module,
            target=f.target,
            category=f.category,
            verified=f.verified,
            raw_metadata=f.raw_metadata or {}
        )
        for f in case.findings
        if (f.id in included_ids or not included_ids)
    ]

    redaction_rules = RedactionRules(**report.redaction_rules) if report.redaction_rules else None

    # Prepare context
    context = report_engine.prepare_report_context(
        case_data={
            "id": case.id,
            "title": case.title,
            "classification": case.classification,
            "purpose": report.purpose
        },
        findings=selected_findings,
        executive_summary=report.executive_summary,
        analyst_narrative=report.analyst_narrative,
        template_type=report.template_type,
        redaction_rules=redaction_rules,
        analyst_name=case.investigator or current_user.username
    )

    template_file = f"{report.template_type}.html"
    if not os.path.exists(os.path.join(templates_dir, template_file)):
        template_file = "technical_report.html"

    rendered_html = jinja_env.get_template(template_file).render(context)

    # Audit export
    await record_audit_log(
        db=db,
        user=current_user,
        action="export_report",
        target=report.id,
        module="reporting",
        purpose=report.purpose,
        details={"format": export_format, "report_title": report.title}
    )

    filename_base = f"TRINETRA_Report_{case.id}_v{report.version}"

    if export_format == "html":
        return Response(
            content=ReportExporter.export_html(rendered_html),
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.html"'}
        )
    elif export_format == "pdf":
        pdf_bytes = ReportExporter.export_pdf(rendered_html)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.pdf"'}
        )
    elif export_format == "docx":
        docx_bytes = ReportExporter.export_docx(context)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.docx"'}
        )
    elif export_format in ["md", "markdown"]:
        md_text = ReportExporter.export_markdown(context)
        return Response(
            content=md_text.encode("utf-8"),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.md"'}
        )
    elif export_format == "json":
        json_text = ReportExporter.export_json(context)
        return Response(
            content=json_text.encode("utf-8"),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.json"'}
        )
    elif export_format == "csv":
        csv_text = ReportExporter.export_csv(context)
        return Response(
            content=csv_text.encode("utf-8"),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.csv"'}
        )
    elif export_format == "sha256":
        checksum_text = ReportExporter.generate_tamper_checksum(rendered_html.encode("utf-8"))
        return Response(
            content=checksum_text.encode("utf-8"),
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.sha256"'}
        )
