"""
Build the system prompt with structured memory sections injected per turn.

4 sections map to the 4 memory backends:
  [Profile]   → LongTermProfileMemory
  [Episodes]  → EpisodicMemory
  [Knowledge] → SemanticMemory
  (Recent conversation is passed as the messages list, not in system prompt)
"""

from typing import Dict, List, Optional


_BASE = """Bạn là một AI assistant thông minh với hệ thống trí nhớ đa tầng.
Bạn sử dụng thông tin từ bộ nhớ để cá nhân hóa và cải thiện câu trả lời.
Luôn ưu tiên thông tin mới nhất nếu có mâu thuẫn.
Trả lời bằng ngôn ngữ người dùng đang dùng (tiếng Việt hoặc tiếng Anh)."""

_PROFILE_SECTION = """
## [Profile] Thông tin người dùng:
{content}"""

_EPISODIC_SECTION = """
## [Episodes] Sự kiện / kinh nghiệm gần đây:
{content}"""

_SEMANTIC_SECTION = """
## [Knowledge] Thông tin tham khảo liên quan:
{content}"""

_TRIM_NOTICE = """
[Context đã được tối ưu theo token budget — một số thông tin cũ bị lược bỏ.]"""


class PromptBuilder:

    def build(
        self,
        user_profile: Optional[Dict] = None,
        episodes: Optional[List[Dict]] = None,
        semantic_hits: Optional[List[Dict]] = None,
        trimmed: bool = False,
    ) -> str:
        parts = [_BASE]

        if user_profile:
            parts.append(_PROFILE_SECTION.format(content=self._fmt_profile(user_profile)))

        if episodes:
            parts.append(_EPISODIC_SECTION.format(content=self._fmt_episodes(episodes)))

        if semantic_hits:
            parts.append(_SEMANTIC_SECTION.format(content=self._fmt_semantic(semantic_hits)))

        if trimmed:
            parts.append(_TRIM_NOTICE)

        return "\n".join(parts)

    # ── formatters ────────────────────────────────────────────────────────────

    def _fmt_profile(self, profile: Dict) -> str:
        if not profile:
            return "(chưa có thông tin)"
        return "\n".join(f"- {k}: {v}" for k, v in profile.items())

    def _fmt_episodes(self, episodes: List[Dict]) -> str:
        if not episodes:
            return "(chưa có sự kiện)"
        lines = []
        for ep in episodes:
            ts = ep.get("timestamp", "")[:10]
            etype = ep.get("event_type", "event")
            summary = ep.get("summary", "")
            lines.append(f"- [{ts}][{etype}] {summary}")
        return "\n".join(lines)

    def _fmt_semantic(self, hits: List[Dict]) -> str:
        if not hits:
            return "(không tìm thấy thông tin liên quan)"
        lines = []
        for i, h in enumerate(hits, 1):
            score = h.get("relevance_score", 0)
            content = h.get("content", "")
            lines.append(f"{i}. (score={score:.2f}) {content}")
        return "\n".join(lines)
