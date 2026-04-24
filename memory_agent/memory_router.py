"""
Memory router: classify query intent and decide which backends to activate.

Intent categories:
  profile   — user facts, preferences, demographics
  episodic  — past events, previous tasks, experience recall
  semantic  — knowledge-base / FAQ lookups
  general   — chitchat with no specific memory need
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MemoryIntent:
    intent: str
    confidence: float
    signals: List[str] = field(default_factory=list)


_PROFILE_PATTERNS = [
    r"\btên\b", r"\btuổi\b", r"\bnghề\b", r"\bsở thích\b", r"\bthích\b",
    r"\bghét\b", r"\bdị ứng\b", r"\bnhà\b", r"\bở đâu\b", r"\blàm gì\b",
    r"\bcủa tôi\b", r"\btôi là\b", r"\btôi đang\b", r"\bkinh nghiệm\b",
    r"\bname\b", r"\bprefer", r"\ballerg", r"\bmy name\b", r"\bi am\b",
    r"\bi like\b", r"\bi hate\b", r"\bi work\b", r"\bi live\b",
    r"\bnhớ tên\b", r"\bnhớ tôi\b",
]

_EPISODIC_PATTERNS = [
    r"\blần trước\b", r"\bhôm qua\b", r"\btrước đây\b", r"\bnhớ không\b",
    r"\bhồi nãy\b", r"\bhồi đó\b", r"\bvừa rồi\b", r"\bkỳ trước\b",
    r"\bprevious\b", r"\blast time\b", r"\byesterday\b", r"\bbefore\b",
    r"\bremember when\b", r"\bwhat did\b", r"\bwe talked\b",
    r"\bhôm nay.*học\b", r"\bvừa.*fix\b", r"\bvừa.*xong\b",
    r"\bnhắc lại\b", r"\bnhớ lại\b",
]

_SEMANTIC_PATTERNS = [
    r"\bcách\b", r"\blàm thế nào\b", r"\blà gì\b", r"\bgiải thích\b",
    r"\bhướng dẫn\b", r"\btài liệu\b", r"\bdoc\b", r"\bfaq\b",
    r"\bhow to\b", r"\bwhat is\b", r"\bexplain\b", r"\bdocumentation\b",
    r"\bguide\b", r"\btutorial\b", r"\bbest practice",
    r"\bkhái niệm\b", r"\bkhuyến nghị\b", r"\bnên dùng\b",
]


def _score(text: str, patterns: List[str]) -> int:
    return sum(1 for p in patterns if re.search(p, text))


def _matched(text: str, patterns: List[str]) -> List[str]:
    return [p for p in patterns if re.search(p, text)]


class MemoryRouter:
    """Classify query intent and return which backends should be queried."""

    def classify(self, query: str) -> MemoryIntent:
        q = query.lower()

        scores = {
            "profile": _score(q, _PROFILE_PATTERNS),
            "episodic": _score(q, _EPISODIC_PATTERNS),
            "semantic": _score(q, _SEMANTIC_PATTERNS),
        }

        max_score = max(scores.values())
        if max_score == 0:
            return MemoryIntent(intent="general", confidence=1.0)

        primary = max(scores, key=lambda k: scores[k])
        total = sum(scores.values()) or 1
        confidence = round(scores[primary] / total, 2)
        signals = _matched(q, {
            "profile": _PROFILE_PATTERNS,
            "episodic": _EPISODIC_PATTERNS,
            "semantic": _SEMANTIC_PATTERNS,
        }[primary])

        return MemoryIntent(intent=primary, confidence=confidence, signals=signals)

    def should_retrieve(self, intent: MemoryIntent) -> Dict[str, bool]:
        """Return a dict of which backends to activate."""
        backends = {
            "short_term": True,
            "profile": False,
            "episodic": False,
            "semantic": False,
        }

        if intent.intent == "profile":
            backends["profile"] = True
        elif intent.intent == "episodic":
            backends["episodic"] = True
            backends["profile"] = True
        elif intent.intent == "semantic":
            backends["semantic"] = True
        else:
            backends["profile"] = True

        return backends
