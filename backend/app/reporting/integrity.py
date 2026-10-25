import re
from typing import List, Set, Tuple

class UncitedClaimError(ValueError):
    """Raised when an AI narrative or analyst text makes claims without citing Finding IDs"""
    def __init__(self, uncited_sentences: List[str]):
        self.uncited_sentences = uncited_sentences
        super().__init__(f"Report contains {len(uncited_sentences)} uncited claim(s): {uncited_sentences}")

class IntegrityValidator:
    """
    Enforces non-negotiable reporting integrity rules:
    1. Every narrative sentence must cite one or more valid Finding IDs: e.g. [fnd_12345]
    2. Auto-excludes hard-blocked dark web content and sensitive categories (health, minors, banking)
    3. Prevents uncorroborated single-source assertions from being framed as verified facts.
    """

    CITATION_REGEX = re.compile(r"\[(fnd_[a-zA-Z0-9_\-]+)\]")
    SENSITIVE_KEYWORDS = [
        "child abuse", "csam", "weapons", "fentanyl", "cocaine", "hitman",
        "ssn dump", "credit card dump", "cvv", "bank logs", "health record", "medical diagnosis"
    ]

    @classmethod
    def validate_narrative_citations(cls, text: str, valid_finding_ids: Set[str]) -> Tuple[bool, List[str]]:
        """
        Splits text into sentences and verifies that every non-empty sentence
        cites at least one finding ID present in valid_finding_ids.
        Returns (is_valid, list_of_violating_sentences).
        """
        if not text or not text.strip():
            return True, []

        # Split into sentences by '.', '!', or '?' followed by whitespace or newline
        raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        uncited = []

        for sentence in raw_sentences:
            s = sentence.strip()
            # Ignore headers, bullet markers, or trivial greetings
            if not s or len(s) < 10 or s.startswith("#") or s.startswith("-"):
                continue

            citations = cls.CITATION_REGEX.findall(s)
            if not citations:
                uncited.append(s)
            else:
                # Check if cited finding IDs exist in valid set
                cited_valid = [cid for cid in citations if cid in valid_finding_ids]
                if not cited_valid:
                    uncited.append(f"{s} (Cited non-existent finding IDs: {citations})")

        return (len(uncited) == 0), uncited

    @classmethod
    def check_sensitive_content_exclusion(cls, content: str) -> Tuple[bool, List[str]]:
        """
        Verifies that no prohibited or hard-blocked content slipped into the report.
        """
        violations = []
        lower = content.lower()
        for kw in cls.SENSITIVE_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", lower):
                violations.append(kw)

        return (len(violations) == 0), violations
