# Hacker News — Show HN Post

## Title
Show HN: NeverOnce v0.2.0 – Pre-flight checks for AI agents. Guard decorator + corrections as constraints (~800 lines, zero deps)

## Body

AI agents don't have pre-flight checks. You correct a mistake, the correction dies with the session, the agent repeats it. NeverOnce is a safety layer that fixes this.

The core idea: corrections are stored as constraints (max importance, immune to decay, always surface first). The `@guard` decorator enforces them before any function executes.

```python
from neveronce import Memory, guard

mem = Memory("my_agent")
mem.correct("never deploy on Fridays", context="deployment")
mem.correct("never call external API without rate limiting", context="api")

@guard(mem, mode="block")
def deploy(version: str):
    push_to_prod(version)

deploy("v2.1")  # → CorrectionWarning: "never deploy on Fridays"
```

Three modes: `warn` (log + proceed), `block` (raise exception), `review` (queue for human). Every invocation logged to `ActionLog`.

4 months production use. 1,421 memories, 87 corrections, most-used surfaced 491 times, zero repeats.

**What's in v0.2.0:**

- `@guard(mem, mode="warn|block|review")` decorator
- `GuardedAgent` class for wrapping agent framework callables
- `ActionLog` audit trail
- Framework integrations: OpenAI, Anthropic, LangChain, CrewAI, AutoGen
- 74 tests

**Architecture:** SQLite + FTS5 (BM25 ranking). No embeddings, no vector DB, no API calls. Corrections always rank above regular memories in retrieval. The `@guard` decorator queries corrections matching the function name + args before execution.

**What it's not:** It's not a RAG system. It's not a vector store. It's a correction-enforcement layer. Think of it as assertions for agent behavior, built from your own mistake history.

- ~800 lines Python, zero deps
- MIT licensed
- MCP server included

GitHub: https://github.com/WeberG619/neveronce
