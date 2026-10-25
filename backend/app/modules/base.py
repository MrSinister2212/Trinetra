import abc
import hashlib
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.schemas import Finding

class BaseModule(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Module identifier string, e.g. 'username', 'email_domain'"""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Human-readable module description"""
        pass

    @abc.abstractmethod
    async def run(self, target: str, options: Optional[Dict[str, Any]] = None) -> List[Finding]:
        """Execute the module logic and return standardized Finding objects"""
        pass

    def create_finding(
        self,
        source: str,
        exact_url: str,
        evidence_snippet: str,
        confidence: float,
        target: str,
        confidence_reasoning: str = "",
        category: str = "general",
        verified: bool = False,
        raw_metadata: Optional[Dict[str, Any]] = None,
        finding_id: Optional[str] = None
    ) -> Finding:
        """
        Creates a strictly typed Finding object adhering to TRINETRA standard schema.
        """
        if not finding_id:
            # Deterministic or unique finding ID
            seed = f"{self.name}:{source}:{exact_url}:{target}"
            finding_id = "fnd_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]

        now_iso = datetime.now(timezone.utc).isoformat()
        
        # Calculate SHA256 of the evidence snippet
        snippet_hash = hashlib.sha256(evidence_snippet.encode("utf-8")).hexdigest()
        
        metadata = raw_metadata or {}
        metadata.setdefault("evidence_sha256", snippet_hash)
        metadata.setdefault("captured_at", now_iso)
        metadata.setdefault("module_version", "1.0.0")

        return Finding(
            id=finding_id,
            source=source,
            exact_url=exact_url,
            evidence_snippet=evidence_snippet,
            confidence=max(0.0, min(1.0, round(confidence, 2))),
            confidence_reasoning=confidence_reasoning or f"Detected via {source} validation check.",
            timestamp=now_iso,
            module=self.name,
            target=target,
            category=category,
            verified=verified,
            raw_metadata=metadata
        )
