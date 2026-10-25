from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AuditLog, User

async def record_audit_log(
    db: AsyncSession,
    user: User,
    action: str,
    target: str,
    module: str,
    purpose: str,
    details: Dict[str, Any] = None,
    ip_address: str = "127.0.0.1"
) -> AuditLog:
    """
    Creates an immutable audit log entry for every query, investigation action,
    or report export.
    """
    if details is None:
        details = {}
    
    log_entry = AuditLog(
        user_id=user.id,
        username=user.username,
        action=action,
        target=target,
        module=module,
        purpose=purpose,
        ip_address=ip_address,
        details=details
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    return log_entry
