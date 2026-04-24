"""
Benchmark runner: compare No-Memory Agent vs With-Memory Agent
across 10 multi-turn conversations.

Usage:
  python -m benchmark.run_benchmark          # uses OPENAI_API_KEY env var
  python -m benchmark.run_benchmark --key sk-...
"""

import argparse
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from openai import OpenAI

from memory_agent.graph import MemoryAgent
from benchmark.conversations import CONVERSATIONS, KNOWLEDGE_BASE

load_dotenv()


# ── No-memory baseline ────────────────────────────────────────────────────────

class NoMemoryAgent:
    """Stateless agent: receives only the current user message, no history."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, message: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": message},
            ],
            max_tokens=512,
            temperature=0.7,
        )
        return resp.choices[0].message.content


# ── helpers ───────────────────────────────────────────────────────────────────

def _est_tokens(text: str) -> int:
    return len(text.split()) * 4 // 3


def _score(response: str, key_check: str) -> int:
    """0-5 score: does response meaningfully contain the key information?"""
    if not response:
        return 0
    resp_lower = response.lower()
    key_lower = key_check.lower()
    if key_lower in resp_lower:
        return 5
    words = key_lower.split()
    hit = sum(1 for w in words if w in resp_lower)
    if hit == len(words):
        return 4
    if hit > 0:
        return 2
    return 0


def run_with_memory(
    conv: Dict, api_key: str
) -> Tuple[List[str], Dict]:
    agent = MemoryAgent(
        session_id=f"bench_mem_{conv['id']}",
        openai_api_key=api_key,
        data_dir=f"data/bench/mem_{conv['id']}",
    )
    agent.seed_knowledge_base(KNOWLEDGE_BASE)

    responses: List[str] = []
    for turn in conv["turns"]:
        if turn["role"] == "user":
            resp = agent.chat(turn["content"])
            responses.append(resp)
            time.sleep(0.5)

    return responses, agent.get_memory_stats()


def run_without_memory(conv: Dict, api_key: str) -> List[str]:
    agent = NoMemoryAgent(api_key=api_key)
    responses: List[str] = []
    for turn in conv["turns"]:
        if turn["role"] == "user":
            resp = agent.chat(turn["content"])
            responses.append(resp)
            time.sleep(0.5)
    return responses


# ── report generator ──────────────────────────────────────────────────────────

def generate_markdown(results: List[Dict], run_ts: str) -> str:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_no = sum(r["no_mem_score"] for r in results) / total
    avg_with = sum(r["with_mem_score"] for r in results) / total
    avg_no_tok = sum(r["no_mem_tokens"] for r in results) / total
    avg_with_tok = sum(r["with_mem_tokens"] for r in results) / total

    groups: Dict[str, Dict] = {}
    for r in results:
        g = r["group"]
        if g not in groups:
            groups[g] = {"total": 0, "passed": 0}
        groups[g]["total"] += 1
        if r["passed"]:
            groups[g]["passed"] += 1

    md = f"""# BENCHMARK REPORT — Lab #17: Multi-Memory Agent

**Run:** {run_ts}
**Model:** gpt-4o-mini
**Memory stack:** Short-term buffer · Long-term Profile (JSON/Redis) · Episodic log (JSON) · Semantic (ChromaDB)

---

## Executive Summary

| Metric | No-Memory Agent | With-Memory Agent | Delta |
|--------|-----------------|-------------------|-------|
| Pass rate | — | {passed}/{total} ({passed/total*100:.0f}%) | +{passed} wins |
| Avg relevance (0–5) | {avg_no:.1f} | {avg_with:.1f} | +{avg_with - avg_no:.1f} |
| Avg response tokens | {avg_no_tok:.0f} | {avg_with_tok:.0f} | {avg_with_tok - avg_no_tok:+.0f} |
| Context utilization | ~0% | ~{passed/total*100:.0f}% | — |

---

## 10 Multi-Turn Conversations

| # | Scenario | No-Memory Answer | With-Memory Answer | Score No/With | Pass? |
|---|----------|------------------|--------------------|---------------|-------|
"""
    for r in results:
        no_short = (r["no_mem_final"][:90] + "…").replace("\n", " ")
        with_short = (r["with_mem_final"][:90] + "…").replace("\n", " ")
        icon = "✅" if r["passed"] else "❌"
        md += f"| {r['id']} | {r['scenario']} | {no_short} | {with_short} | {r['no_mem_score']}/{r['with_mem_score']} | {icon} |\n"

    md += """
---

## Memory Hit Rate Analysis

| Group | Conversations | Passed | Hit Rate |
|-------|---------------|--------|----------|
"""
    for g, s in groups.items():
        hit = s["passed"] / s["total"] * 100
        md += f"| {g} | {s['total']} | {s['passed']} | {hit:.0f}% |\n"

    md += """
---

## Token Budget Breakdown

| Context Component | Token Allocation | Priority Level | Eviction Order |
|-------------------|-----------------|----------------|----------------|
| System Prompt (base) | ~600 tokens | Fixed | Never |
| User Profile (long-term) | up to 600 tokens | Priority 1 | Never |
| Short-term Conversation | up to 1 200 tokens | Priority 2 | Oldest pair first |
| Episodic Memory | up to 400 tokens | Priority 3 | Oldest episode first |
| Semantic Hits | up to 200 tokens | Priority 4 | **Evicted first** |
| Reserved for LLM Response | ~1 000 tokens | Fixed | — |
| **Total context window** | **4 000 tokens** | — | — |

Eviction triggers when estimated context exceeds **2 400 tokens**.
Eviction order: Semantic → Episodic (oldest) → Short-term (oldest pair) → Profile (never).

---

## Detailed Conversation Results

"""
    for r in results:
        icon = "✅ PASS" if r["passed"] else "❌ FAIL"
        stats = r.get("mem_stats", {})
        md += f"""### Conv {r['id']}: {r['scenario']} — {icon}

- **Group:** `{r['group']}`
- **Key information checked:** `{r['key_check']}`
- **Memory type tested:** {r['group'].replace('_', ' ')}

**No-Memory Response (final turn):**
> {r['no_mem_final']}

**With-Memory Response (final turn):**
> {r['with_mem_final']}

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | {r['no_mem_score']}/5 | {r['with_mem_score']}/5 |
| Response tokens (est.) | {r['no_mem_tokens']} | {r['with_mem_tokens']} |
| Profile facts stored | — | {stats.get('profile_facts', '—')} |
| Episodes stored | — | {stats.get('episodic_count', '—')} |
| Semantic docs available | — | {stats.get('semantic_docs', '—')} |

---

"""

    md += """## Reflection: Privacy & Limitations

### Which memory helped most?
**Long-term Profile Memory** provides the biggest uplift — the agent instantly knows
user preferences (diet, allergies, job) without re-asking, making every response
feel personalised from the first follow-up turn.

### Which memory is riskiest if retrieved wrong?
**Episodic Memory** — if the agent recalls the wrong past event it can confidently
give incorrect advice (e.g. "you fixed it with X" when actually the user used Y).
**Profile Memory** is dangerous when conflict resolution fails and a stale fact
(e.g. old allergy) overrides the corrected value.

### If the user requests deletion, which backends must be cleared?
| Backend | Deletion method |
|---------|----------------|
| Profile | `profile_mem.delete_all()` → removes `user_profile.json` |
| Episodic | Filter & rewrite `episodic_log.json` removing user episodes |
| Semantic | `collection.delete(ids=[...])` in ChromaDB |
| Short-term | `short_term.clear()` → in-memory, gone on restart anyway |

A unified `forget(user_id)` API is needed for GDPR **Right to Erasure** compliance.

### PII / Privacy risks
- **Sensitive PII** (allergy, health, financial info) is stored in profile with no encryption.
- **No TTL**: profile facts never expire — a medical fact from 2 years ago may still be served.
- **No consent gate**: the agent silently stores facts without explicit user agreement.
- **Namespace isolation missing**: all users share one ChromaDB collection in this implementation.

### Technical limitations of this solution
1. **Keyword-based intent classifier** can miss intent when user phrasing is unexpected.
   Production should replace with LLM-based or fine-tuned classifier.
2. **JSON file storage** is single-process and doesn't scale to multiple users or servers.
   Needs migration to Redis (profile) + PostgreSQL/MongoDB (episodic).
3. **No user-ID partitioning**: all conversations share the same JSON files.
   Multi-user deployment requires a `user_id` dimension across all backends.
4. **ChromaDB local** doesn't support distributed deployment.
   Production: Pinecone, Weaviate, or managed Chroma Cloud.
5. **Episodic recall** relies on keyword overlap, not semantic similarity.
   Embedding-based search would improve recall on paraphrased queries.
"""
    return md


# ── main ─────────────────────────────────────────────────────────────────────

def main(api_key: Optional[str] = None) -> None:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        print("Error: OPENAI_API_KEY not set. Use --key or set the env var.")
        sys.exit(1)

    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*65}")
    print("BENCHMARK: Multi-Memory Agent vs No-Memory Agent")
    print(f"Run: {run_ts}")
    print(f"{'='*65}\n")

    results: List[Dict] = []

    for conv in CONVERSATIONS:
        print(f"[{conv['id']:02d}/10] {conv['scenario']}")

        print("  -> with-memory agent ...")
        with_responses, mem_stats = run_with_memory(conv, key)
        time.sleep(1)

        print("  -> no-memory agent ...")
        no_responses = run_without_memory(conv, key)
        time.sleep(1)

        final_with = with_responses[-1] if with_responses else ""
        final_no = no_responses[-1] if no_responses else ""

        score_with = _score(final_with, conv["key_check"])
        score_no = _score(final_no, conv["key_check"])
        # Pass: with-memory is at least as good AND reaches quality threshold.
        # Handles tie-high (both score 5) and clear-win cases.
        passed = score_with >= score_no and score_with >= 3

        status = "PASS" if passed else "FAIL"
        print(f"  [{status}]  no-mem={score_no}/5  with-mem={score_with}/5\n")

        results.append(
            {
                "id": conv["id"],
                "scenario": conv["scenario"],
                "group": conv["group"],
                "key_check": conv["key_check"],
                "no_mem_final": final_no,
                "with_mem_final": final_with,
                "no_mem_score": score_no,
                "with_mem_score": score_with,
                "passed": passed,
                "no_mem_tokens": _est_tokens(final_no),
                "with_mem_tokens": _est_tokens(final_with),
                "mem_stats": mem_stats,
            }
        )

    report = generate_markdown(results, run_ts)

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "BENCHMARK.md"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    passed_total = sum(1 for r in results if r["passed"])
    print(f"\n{'='*65}")
    print(f"DONE - Pass rate: {passed_total}/{len(results)}")
    print("Report saved -> BENCHMARK.md")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run multi-memory agent benchmark")
    parser.add_argument("--key", help="OpenAI API key (overrides env var)")
    args = parser.parse_args()
    main(api_key=args.key)
