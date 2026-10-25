import time
import re
from typing import Dict, Tuple
from fastapi import HTTPException, status
from app.config import settings

# In-memory target cooldown and rate-limiter caches
# (For multi-worker deployment, Redis keys can be used; in-memory fallback is active)
_LAST_SEARCH_TIMESTAMP: Dict[Tuple[str, str], float] = {} # (user_id, target) -> timestamp
_USER_REQUEST_COUNTS: Dict[str, list] = {} # user_id -> list of timestamps

def check_rate_limit(user_id: str, target: str):
    """
    Enforces per-user request limits and target cooldowns to prevent abuse.
    """
    now = time.time()
    
    # 1. Target cooldown (prevent rapid repeated automated hammering of the same individual/target)
    last_target_time = _LAST_SEARCH_TIMESTAMP.get((user_id, target.lower()))
    if last_target_time and (now - last_target_time) < settings.RATE_LIMIT_COOLDOWN_SECONDS:
        remaining = int(settings.RATE_LIMIT_COOLDOWN_SECONDS - (now - last_target_time))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit cooldown active on target '{target}'. Please wait {remaining} seconds before repeating."
        )
    
    # 2. Per-user requests per minute
    timestamps = _USER_REQUEST_COUNTS.get(user_id, [])
    # Keep only timestamps in last 60 seconds
    timestamps = [t for t in timestamps if now - t < 60]
    if len(timestamps) >= settings.MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="User rate limit exceeded (maximum 60 searches per minute)."
        )
    
    timestamps.append(now)
    _USER_REQUEST_COUNTS[user_id] = timestamps
    _LAST_SEARCH_TIMESTAMP[(user_id, target.lower())] = now

def assess_individual_target_risk(target: str, module: str) -> Dict[str, Any]:
    """
    Warns the user on any query that appears to target a private individual,
    requiring lawful purpose and consent confirmation (GDPR/DPDP Act/CCPA awareness).
    """
    is_individual = False
    warning_reason = None

    if module == "phone":
        is_individual = True
        warning_reason = "Phone numbers can be personal identifiers under GDPR/DPDP/CCPA. Ensure you hold lawful basis or investigating corporate/public entity."
    elif module == "email_domain":
        if "@" in target:
            domain = target.split("@")[-1].lower()
            free_mail_providers = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "proton.me", "protonmail.com"]
            if domain in free_mail_providers:
                is_individual = True
                warning_reason = f"Target '{target}' uses a consumer email provider. Heightened privacy regulations apply to private individuals."
    elif module == "username":
        # Check if username looks like a real person's full name (e.g. john_doe, first.last)
        if re.match(r"^[a-zA-Z]+[._-][a-zA-Z]+$", target):
            is_individual = True
            warning_reason = f"Target '{target}' resembles a person's first and last name. Ensure search aligns with journalistic, security, or self-audit exemption."

    return {
        "is_individual": is_individual,
        "warning_reason": warning_reason,
        "requires_lawful_affirmation": is_individual
    }
