"""
Context window management with 4-level priority-based eviction.

Priority hierarchy (highest → lowest):
  1. User Profile        — never evict
  2. Short-term messages — trim from oldest
  3. Episodic memories   — trim from oldest
  4. Semantic hits       — evict first, all at once

Total budget: 4 000 tokens
  - System prompt:  ~600  (fixed)
  - LLM response:  ~1 000 (reserved)
  - Context budget: 2 400  (managed here)
"""

from typing import Dict, List, Tuple

import tiktoken


CONTEXT_BUDGET = 2_400


class ContextWindowManager:

    def __init__(self, model: str = "gpt-4o-mini"):
        try:
            self.enc = tiktoken.encoding_for_model(model)
        except Exception:
            self.enc = tiktoken.get_encoding("cl100k_base")

    # ── public API ─────────────────────────────────────────────────────────

    def trim(
        self,
        user_profile: Dict,
        episodes: List[Dict],
        semantic_hits: List[Dict],
        messages: List[Dict],
        budget: int = CONTEXT_BUDGET,
    ) -> Tuple[Dict, List, List, List, bool]:
        """
        Return (profile, episodes, semantic_hits, messages, was_trimmed).
        Evicts in priority order: semantic → episodic → short-term → (profile never).
        """
        profile = dict(user_profile)
        episodes = list(episodes)
        semantic_hits = list(semantic_hits)
        messages = list(messages)

        if self._total(profile, episodes, semantic_hits, messages) <= budget:
            return profile, episodes, semantic_hits, messages, False

        # Level 4: drop semantic hits one by one
        while semantic_hits and self._total(profile, episodes, semantic_hits, messages) > budget:
            semantic_hits.pop()

        # Level 3: drop oldest episodic entries (keep min 1)
        while len(episodes) > 1 and self._total(profile, episodes, semantic_hits, messages) > budget:
            episodes.pop(0)

        # Level 2: drop oldest message pairs (keep min 2 messages = 1 pair)
        while len(messages) > 2 and self._total(profile, episodes, semantic_hits, messages) > budget:
            messages = messages[2:]

        # Level 1: profile is never trimmed
        return profile, episodes, semantic_hits, messages, True

    def count(self, text: str) -> int:
        return len(self.enc.encode(text))

    def count_messages(self, messages: List[Dict]) -> int:
        return sum(self.count(m.get("content", "")) + 4 for m in messages)

    def budget_breakdown(
        self,
        profile: Dict,
        episodes: List,
        semantic_hits: List,
        messages: List,
    ) -> Dict:
        return {
            "profile_tokens": self._est_dict(profile),
            "short_term_tokens": self.count_messages(messages),
            "episodic_tokens": self._est_list(episodes),
            "semantic_tokens": self._est_list(semantic_hits),
            "context_budget": CONTEXT_BUDGET,
            "total_used": self._total(profile, episodes, semantic_hits, messages),
        }

    # ── helpers ────────────────────────────────────────────────────────────

    def _total(self, profile: Dict, episodes: List, semantic_hits: List, messages: List) -> int:
        return (
            self._est_dict(profile)
            + self._est_list(episodes)
            + self._est_list(semantic_hits)
            + self.count_messages(messages)
        )

    def _est_dict(self, d: Dict) -> int:
        return len(str(d).split()) * 4 // 3 + 20 if d else 0

    def _est_list(self, lst: List) -> int:
        return len(str(lst).split()) * 4 // 3 + 20 if lst else 0
