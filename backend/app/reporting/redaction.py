import re
from typing import Dict, Any, List
from app.schemas import Finding, RedactionRules

class RedactionEngine:
    EMAIL_PATTERN = re.compile(r"\b([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]*([a-zA-Z0-9_.+-])@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b")
    PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b")
    GPS_PATTERN = re.compile(r"[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)")
    URL_PATTERN = re.compile(r"https?://(?:www\.)?([a-zA-Z0-9.-]+)(/[^\s]*)?")

    @classmethod
    def mask_email(cls, text: str) -> str:
        return cls.EMAIL_PATTERN.sub(r"\1***\2@\3", text)

    @classmethod
    def mask_phone(cls, text: str) -> str:
        def repl(match):
            m_text = match.group(0)
            digits = re.findall(r"\d", m_text)
            if len(digits) >= 4:
                last4 = "".join(digits[-4:])
                prefix = "+1 " if "+1" in m_text else ""
                return f"{prefix}***-***-{last4}"
            return "[REDACTED_PHONE]"
        return cls.PHONE_PATTERN.sub(repl, text)

    @classmethod
    def mask_gps(cls, text: str) -> str:
        return cls.GPS_PATTERN.sub(r"[REDACTED_GPS_COORDINATES]", text)

    @classmethod
    def mask_url(cls, text: str) -> str:
        return cls.URL_PATTERN.sub(r"https://[REDACTED_HOST]\2", text)

    @classmethod
    def mask_username(cls, text: str, usernames: List[str]) -> str:
        for u in usernames:
            if len(u) > 2:
                masked = u[0] + ("*" * (len(u) - 2)) + u[-1]
                text = re.sub(re.escape(u), masked, text, flags=re.IGNORECASE)
        return text

    @classmethod
    def redact_text(cls, text: str, rules: RedactionRules, targets: List[str] = None) -> str:
        if not text:
            return ""
        
        redacted = text
        if rules.mask_gps:
            redacted = cls.mask_gps(redacted)
        if rules.mask_emails:
            redacted = cls.mask_email(redacted)
        if rules.mask_phones:
            redacted = cls.mask_phone(redacted)
        if rules.mask_urls:
            redacted = cls.mask_url(redacted)
        if rules.mask_usernames and targets:
            redacted = cls.mask_username(redacted, targets)

        # Custom terms
        if rules.custom_terms:
            for term in rules.custom_terms:
                if term and len(term.strip()) > 0:
                    redacted = re.sub(re.escape(term.strip()), "[REDACTED]", redacted, flags=re.IGNORECASE)

        return redacted

    @classmethod
    def redact_finding(cls, finding: Finding, rules: RedactionRules) -> Finding:
        """
        Creates a new redacted Finding object according to active rules.
        """
        if not rules:
            return finding

        targets = [finding.target]
        redacted_target = cls.redact_text(finding.target, rules, targets)
        redacted_snippet = cls.redact_text(finding.evidence_snippet, rules, targets)
        redacted_reasoning = cls.redact_text(finding.confidence_reasoning, rules, targets)
        redacted_url = cls.mask_url(finding.exact_url) if rules.mask_urls else finding.exact_url

        metadata_copy = dict(finding.raw_metadata or {})
        # Mask metadata GPS if present
        if rules.mask_gps and "gps" in metadata_copy:
            metadata_copy["gps"] = "[REDACTED]"

        return Finding(
            id=finding.id,
            source=finding.source,
            exact_url=redacted_url,
            evidence_snippet=redacted_snippet,
            confidence=finding.confidence,
            confidence_reasoning=redacted_reasoning,
            timestamp=finding.timestamp,
            module=finding.module,
            target=redacted_target,
            category=finding.category,
            verified=finding.verified,
            raw_metadata=metadata_copy
        )
