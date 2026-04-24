"""
LangGraph StateGraph: 4-node pipeline per conversation turn.

Flow: classify_intent → retrieve_memory → generate_response → save_memory → END

MemoryState carries all context through the graph; each node returns
a partial dict that is merged into the running state.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph
from openai import OpenAI

from .context_manager import ContextWindowManager
from .memory_backends import (
    EpisodicMemory,
    LongTermProfileMemory,
    SemanticMemory,
    ShortTermMemory,
)
from .memory_router import MemoryRouter
from .prompt_builder import PromptBuilder


# ── State ─────────────────────────────────────────────────────────────────────

class MemoryState(TypedDict):
    messages: List[Dict[str, str]]   # current conversation window
    user_profile: Dict[str, Any]     # retrieved from LongTermProfileMemory
    episodes: List[Dict]             # retrieved from EpisodicMemory
    semantic_hits: List[Dict]        # retrieved from SemanticMemory
    memory_budget: int               # token budget for context
    intent: str                      # classified intent
    response: str                    # LLM-generated response
    session_id: str
    was_trimmed: bool


# ── Agent ─────────────────────────────────────────────────────────────────────

class MemoryAgent:
    """Multi-memory agent backed by a LangGraph state machine."""

    def __init__(
        self,
        session_id: str = "default",
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        data_dir: str = "data",
    ):
        self.session_id = session_id
        self.model = model

        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

        # 4 memory backends
        self.short_term = ShortTermMemory(max_turns=10)
        self.profile_mem = LongTermProfileMemory(
            filepath=os.path.join(data_dir, "user_profile.json")
        )
        self.episodic_mem = EpisodicMemory(
            filepath=os.path.join(data_dir, "episodic_log.json")
        )
        self.semantic_mem = SemanticMemory(
            persist_dir=os.path.join(data_dir, "chroma_db"),
            openai_api_key=api_key,
        )

        self.router = MemoryRouter()
        self.prompt_builder = PromptBuilder()
        self.ctx_manager = ContextWindowManager(model=model)

        self.graph = self._build_graph()

    # ── public ────────────────────────────────────────────────────────────────

    def chat(self, user_message: str) -> str:
        self.short_term.add("user", user_message)

        state: MemoryState = {
            "messages": self.short_term.get(),
            "user_profile": {},
            "episodes": [],
            "semantic_hits": [],
            "memory_budget": 2_400,
            "intent": "general",
            "response": "",
            "session_id": self.session_id,
            "was_trimmed": False,
        }

        result = self.graph.invoke(state)
        response = result["response"]
        self.short_term.add("assistant", response)
        return response

    def seed_knowledge_base(self, documents: List[Dict[str, str]]) -> None:
        for doc in documents:
            self.semantic_mem.add(
                doc_id=doc["id"],
                content=doc["content"],
                metadata=doc.get("metadata", {}),
            )

    def reset_short_term(self) -> None:
        self.short_term.clear()

    def get_memory_stats(self) -> Dict:
        return {
            "short_term_turns": len(self.short_term.messages) // 2,
            "profile_facts": len(self.profile_mem.get_all()),
            "episodic_count": len(self.episodic_mem._episodes),
            "semantic_docs": self.semantic_mem.count(),
        }

    # ── graph construction ────────────────────────────────────────────────────

    def _build_graph(self):
        g = StateGraph(MemoryState)

        g.add_node("classify_intent", self._classify_intent_node)
        g.add_node("retrieve_memory", self._retrieve_memory_node)
        g.add_node("generate_response", self._generate_response_node)
        g.add_node("save_memory", self._save_memory_node)

        g.set_entry_point("classify_intent")
        g.add_edge("classify_intent", "retrieve_memory")
        g.add_edge("retrieve_memory", "generate_response")
        g.add_edge("generate_response", "save_memory")
        g.add_edge("save_memory", END)

        return g.compile()

    # ── nodes ─────────────────────────────────────────────────────────────────

    def _classify_intent_node(self, state: MemoryState) -> Dict:
        last_user = self._last_user_msg(state["messages"])
        intent_obj = self.router.classify(last_user)
        return {"intent": intent_obj.intent}

    def _retrieve_memory_node(self, state: MemoryState) -> Dict:
        last_user = self._last_user_msg(state["messages"])
        intent_obj = self.router.classify(last_user)
        backends = self.router.should_retrieve(intent_obj)

        profile: Dict = {}
        episodes: List = []
        semantic_hits: List = []

        if backends.get("profile"):
            profile = self.profile_mem.get_all()

        if backends.get("episodic"):
            episodes = self.episodic_mem.search(last_user, n=3)
            if not episodes:
                episodes = self.episodic_mem.get_recent(3)

        if backends.get("semantic"):
            semantic_hits = self.semantic_mem.search(last_user, n_results=3)

        # always load profile basics
        if not profile:
            profile = self.profile_mem.get_all()

        # apply token budget with priority eviction
        p, ep, sem, msgs, trimmed = self.ctx_manager.trim(
            user_profile=profile,
            episodes=episodes,
            semantic_hits=semantic_hits,
            messages=list(state["messages"]),
            budget=state["memory_budget"],
        )

        return {
            "user_profile": p,
            "episodes": ep,
            "semantic_hits": sem,
            "messages": msgs,
            "was_trimmed": trimmed,
        }

    def _generate_response_node(self, state: MemoryState) -> Dict:
        system_prompt = self.prompt_builder.build(
            user_profile=state["user_profile"],
            episodes=state["episodes"],
            semantic_hits=state["semantic_hits"],
            trimmed=state["was_trimmed"],
        )

        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend(state["messages"])

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=api_messages,
            max_tokens=512,
            temperature=0.7,
        )
        return {"response": resp.choices[0].message.content}

    def _save_memory_node(self, state: MemoryState) -> Dict:
        last_user = self._last_user_msg(state["messages"])
        self._extract_profile_facts(last_user)
        self._maybe_save_episode(last_user, state["response"])
        return {}

    # ── helpers ───────────────────────────────────────────────────────────────

    def _last_user_msg(self, messages: List[Dict]) -> str:
        for msg in reversed(messages):
            if msg["role"] == "user":
                return msg["content"]
        return ""

    def _extract_profile_facts(self, user_message: str) -> None:
        """Use LLM to extract personal facts and update profile (conflict-resolving)."""
        prompt = (
            'Extract personal facts from this user message as JSON {"key": "value"}. '
            'Valid keys: name, age, job, current_location, destination, allergy, preference, dislike, language, experience, goal. '
            'IMPORTANT: "current_location" = where user CURRENTLY lives/works. '
            '"destination" = where user WANTS to move or go in the future. '
            'Never put a future/desired city in "current_location". '
            f'Return {{}} if none found.\n\nMessage: "{user_message}"\n\nJSON:'
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0,
            )
            raw = resp.choices[0].message.content.strip()
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                facts: Dict = json.loads(match.group())
                for key, value in facts.items():
                    if key and value and str(value) not in ("null", "None", ""):
                        self.profile_mem.set(key, value)
        except Exception:
            pass

    def _maybe_save_episode(self, user_message: str, assistant_response: str) -> None:
        """Save an episodic log entry for notable interactions."""
        significance_signals = [
            "xong", "hoàn thành", "fix", "solved", "học", "learn", "hiểu",
            "done", "completed", "figured out", "remember", "quan trọng",
        ]
        if any(sig in user_message.lower() for sig in significance_signals):
            summary = f"{user_message[:120].strip()}".replace("\n", " ")
            self.episodic_mem.add(
                event_type="task_interaction",
                summary=summary,
                context={"preview": user_message[:200]},
            )
