"""
4 memory backends:
  1. ShortTermMemory      — sliding-window conversation buffer
  2. LongTermProfileMemory — JSON-backed KV store (simulates Redis)
  3. EpisodicMemory        — append-only JSON event log
  4. SemanticMemory        — ChromaDB vector search
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.utils import embedding_functions


class ShortTermMemory:
    """Sliding-window conversation buffer. Keeps the N most-recent turn pairs."""

    PRIORITY = 2

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.messages: List[Dict[str, str]] = []

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        cap = self.max_turns * 2
        if len(self.messages) > cap:
            self.messages = self.messages[-cap:]

    def get(self, n_turns: Optional[int] = None) -> List[Dict[str, str]]:
        if n_turns is None:
            return list(self.messages)
        return self.messages[-(n_turns * 2):]

    def trim_to_token_budget(self, budget: int) -> List[Dict[str, str]]:
        """Return messages fitting within token budget, starting from most recent."""
        result: List[Dict[str, str]] = []
        used = 0
        for msg in reversed(self.messages):
            cost = len(msg["content"].split()) * 4 // 3 + 10
            if used + cost > budget:
                break
            result.insert(0, msg)
            used += cost
        return result

    def clear(self) -> None:
        self.messages = []

    def token_estimate(self) -> int:
        return sum(len(m["content"].split()) * 4 // 3 + 10 for m in self.messages)


class LongTermProfileMemory:
    """
    JSON-backed key-value profile store that simulates Redis.

    Conflict resolution: newer value always overwrites old (last-write-wins).
    Previous value is preserved in 'previous' field for audit purposes.
    """

    PRIORITY = 1  # never evict

    def __init__(self, filepath: str = "data/user_profile.json"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        self._data: Dict[str, Dict] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                self._data = json.load(f)

    def _persist(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def set(self, key: str, value: Any) -> None:
        """Set a profile fact. New value always overwrites (conflict resolution)."""
        old = self._data.get(key, {}).get("value")
        self._data[key] = {
            "value": value,
            "previous": old,
            "updated_at": datetime.now().isoformat(),
        }
        self._persist()

    def get(self, key: str) -> Optional[Any]:
        entry = self._data.get(key)
        return entry["value"] if entry else None

    def get_all(self) -> Dict[str, Any]:
        return {k: v["value"] for k, v in self._data.items()}

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
            self._persist()

    def delete_all(self) -> None:
        """GDPR right-to-erasure: wipe entire profile."""
        self._data = {}
        self._persist()

    def token_estimate(self) -> int:
        content = json.dumps(self.get_all(), ensure_ascii=False)
        return len(content.split()) * 4 // 3 + 20


class EpisodicMemory:
    """Append-only JSON log of significant events and task completions."""

    PRIORITY = 3

    def __init__(self, filepath: str = "data/episodic_log.json"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        self._episodes: List[Dict] = []
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                self._episodes = json.load(f)

    def _persist(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._episodes, f, ensure_ascii=False, indent=2)

    def add(
        self,
        event_type: str,
        summary: str,
        context: Optional[Dict] = None,
    ) -> Dict:
        episode = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "summary": summary,
            "context": context or {},
        }
        self._episodes.append(episode)
        self._persist()
        return episode

    def get_recent(self, n: int = 5) -> List[Dict]:
        return self._episodes[-n:]

    def search(self, query: str, n: int = 3) -> List[Dict]:
        """Keyword-scored search over episode summaries."""
        query_lower = query.lower()
        keywords = [w for w in query_lower.split() if len(w) > 2]

        scored: List[tuple] = []
        for ep in self._episodes:
            text = (ep["summary"] + " " + ep["event_type"]).lower()
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scored.append((score, ep))

        scored.sort(key=lambda x: (-x[0], x[1]["timestamp"]))
        return [ep for _, ep in scored[:n]]

    def clear(self) -> None:
        self._episodes = []
        self._persist()

    def token_estimate(self, n: int = 5) -> int:
        content = json.dumps(self.get_recent(n), ensure_ascii=False)
        return len(content.split()) * 4 // 3 + 20


class SemanticMemory:
    """ChromaDB-backed semantic/vector memory with cosine similarity search."""

    PRIORITY = 4  # evict first when over budget

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        persist_dir: str = "data/chroma_db",
        openai_api_key: Optional[str] = None,
    ):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)

        if openai_api_key:
            ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name="text-embedding-3-small",
            )
        else:
            ef = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

    def add(
        self, doc_id: str, content: str, metadata: Optional[Dict] = None
    ) -> None:
        self.collection.upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata or {}],
        )

    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        count = self.collection.count()
        if count == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, count),
        )

        hits: List[Dict] = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            hits.append(
                {
                    "content": doc,
                    "metadata": meta,
                    "relevance_score": round(1 - dist, 3),
                }
            )
        return hits

    def count(self) -> int:
        return self.collection.count()

    def token_estimate(self, hits: List[Dict]) -> int:
        content = " ".join(h["content"] for h in hits)
        return len(content.split()) * 4 // 3 + 20
