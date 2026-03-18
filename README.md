<p align="center">
  <img src="assets/logo.png" alt="Recal" width="400">
</p>

<p align="center">
  <a href="https://github.com/WeberG619/recal/actions"><img src="https://github.com/WeberG619/recal/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
  <a href="https://pypi.org/project/recal/"><img src="https://img.shields.io/pypi/v/recal" alt="PyPI"></a>
  <a href="https://pypi.org/project/recal/"><img src="https://img.shields.io/pypi/pyversions/recal" alt="Python"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <br>
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue" alt="Platform">
</p>

<p align="center"><strong>Persistent, correctable memory for AI. The memory layer that learns from mistakes.</strong></p>

**Free. Open source. Zero dependencies. Works with any LLM. Runs on Linux, macOS, and Windows.**

They gave us MCP for free. They gave us agents for free. Now here's the missing piece — **memory that actually learns** — for free too.

Every AI agent forgets everything when the session ends. Recal gives them a brain that persists — and more importantly, a brain that **learns from corrections** so the same mistake never happens twice.

## Why Recal?

| Without Recal | With Recal |
|---|---|
| AI forgets everything each session | Memories persist forever |
| Same mistakes repeated daily | Corrections prevent repeat errors |
| No learning from feedback | Helpful memories strengthen, bad ones decay |
| Each session starts from zero | Context builds over time |

## Proven in Production

Recal's correction system was battle-tested for 4 months before open-sourcing:

| Metric | Value |
|---|---|
| Total memories stored | 1,421 |
| Corrections | 87 |
| Running since | November 2025 |
| Most-surfaced correction | 491 times |
| Avg correction surfaced | 78 times each |
| Memory types used | 11 |

The most-used correction was surfaced 491 times — and the AI never repeated that mistake once after it was stored. That's the power of corrections over plain memory.

## Install

```bash
pip install recal
```

**Zero dependencies.** Just Python's built-in SQLite. That's it.

## Quickstart — 5 lines

```python
from recal import Memory

mem = Memory("my_app")
mem.store("user prefers dark mode", tags=["preference"])
mem.correct("never use imperial units", context="unit conversion")
results = mem.recall("what units should I use?")
# → Returns the correction first, always
```

## The Killer Feature: Corrections

Most memory systems just store and retrieve. Recal has **corrections** — a special memory type that:

- Always stored at **maximum importance** (10/10)
- Always **surfaces first** in recall results
- **Never decays**, even if not used frequently
- Represents "I was wrong, here's the fix"

```python
# Store a correction when the AI makes a mistake
mem.correct(
    "use metric units, never imperial",
    context="unit conversion in engineering calculations"
)

# Later, before taking action, check for applicable corrections
warnings = mem.check("converting measurements to feet and inches")
# → Returns: "use metric units, never imperial"
```

This is the difference between an AI that's smart and an AI that **gets smarter**.

## Full API

### `Memory(name, db_dir=None, namespace="default")`

Create a memory store. Each name gets its own SQLite database at `~/.recal/<name>.db`.

### `.store(content, *, tags=None, context="", importance=5)`

Store a general memory. Returns the memory ID.

### `.correct(content, *, context="", tags=None)`

Store a correction. Always importance 10. Always surfaces first.

### `.recall(query, *, limit=10, min_importance=1)`

Search memories by relevance (FTS5/BM25). Corrections always float to top.

### `.check(planned_action)`

Pre-flight check. Returns only matching corrections for the planned action. Call this before doing something to catch mistakes early.

### `.helped(memory_id, did_help)`

Feedback loop. Mark whether a surfaced memory was actually useful. Helpful memories get stronger. Unhelpful ones can be decayed.

### `.decay(surfaced_threshold=5, decay_amount=1)`

Lower importance of memories surfaced many times but never marked helpful. Corrections are immune to decay.

### `.forget(memory_id)`

Delete a memory.

### `.stats()`

Returns `{total, corrections, avg_importance, avg_effectiveness}`.

## MCP Server

Recal includes an MCP server so any MCP-compatible AI client can use it:

```bash
# Install with MCP support
pip install recal[mcp]

# Run the server
python -m recal
```

Add to your MCP config (Claude Code, Cursor, etc.):

```json
{
    "mcpServers": {
        "recal": {
            "command": "python",
            "args": ["-m", "recal"]
        }
    }
}
```

The server exposes all Recal operations as MCP tools: `store`, `correct`, `recall`, `check`, `helped`, `forget`, `stats`.

## Multi-Agent Support

Namespaces let multiple agents share a memory store without stepping on each other:

```python
from recal import Memory

mem = Memory("team")

# Agent 1: research agent
mem.store("found 3 relevant papers on transformer memory", namespace="researcher")
mem.correct("ignore papers before 2024, methodology changed", namespace="researcher")

# Agent 2: coding agent
mem.store("user prefers async/await over callbacks", namespace="coder")
mem.correct("always use Python 3.12+ syntax", namespace="coder")

# Each agent recalls only its own context
research_context = mem.recall("relevant papers", namespace="researcher")
coding_context = mem.recall("coding style", namespace="coder")
```

One database, multiple agents, isolated context. Cross-namespace search is also possible by omitting the namespace parameter.

## Why FTS5 Instead of Embeddings?

Most memory systems use vector embeddings for search. Recal uses SQLite FTS5 (full-text search with BM25 ranking) instead. This is a deliberate choice, not a limitation:

1. **Corrections are short, high-signal text.** "Never use HTTP for internal services" doesn't need semantic similarity — it needs exact keyword matching. BM25 excels at this.
2. **Zero dependencies.** Embeddings require numpy, sentence-transformers, or an API call. FTS5 is built into Python's sqlite3. Nothing to install, nothing to break.
3. **Speed.** FTS5 queries are sub-millisecond. No model loading, no inference, no API latency.
4. **Deterministic.** Same query, same results. No embedding model drift or version mismatches.
5. **Offline.** Works without internet. No API keys, no cloud services.

For most correction and preference storage, keyword matching is actually *more* reliable than semantic search. When you store "never use tabs, always use spaces," you want the word "tabs" to trigger that correction — not a semantically similar but different concept.

If your use case needs semantic search, Recal's architecture is simple enough to extend. But for the core use case — corrections that prevent mistakes — FTS5 is the right tool.

## How It Works

- **Storage:** SQLite with FTS5 full-text search. Zero external dependencies.
- **Search:** BM25 ranking via FTS5. Fast, proven, built into Python.
- **Corrections:** Stored at importance 10, tagged as corrections, always surface first in results.
- **Feedback loop:** `helped()` tracks effectiveness. Memories that help get stronger. Memories that don't can be decayed.
- **Decay:** Unhelpful memories lose importance over time. Corrections never decay.

## Design Philosophy

1. **Zero dependencies** — Just sqlite3 (built into Python). No numpy, no embeddings, no vector DBs.
2. **Corrections > memories** — The ability to say "I was wrong" is more important than total recall.
3. **Feedback-driven** — Memories that help survive. Memories that don't fade away.
4. **One file, one store** — Each Memory instance is a single `.db` file. Copy it, back it up, share it.
5. **Model-agnostic** — Works with any LLM. Recal is the memory, not the brain.

## License

MIT
