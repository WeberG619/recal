# NeverOnce — Reddit Launch Posts

---

## r/Python

**Title:** NeverOnce v0.2.0 — a safety layer for AI agents: guard decorator, audit trail, framework integrations (~800 lines, zero deps)

**Body:**

I built a safety layer for AI agents that I've been running in production for 4 months. Sharing it because the design decisions might be interesting to this community.

**What it is:**

A pre-flight check system for AI agents. You store corrections (things the agent got wrong), then use a `@guard` decorator or `check()` call to catch those mistakes before the agent acts. SQLite-backed, full-text search, importance-based decay. Zero dependencies. ~800 lines. MCP server bundled.

```bash
pip install neveronce
```

**The `@guard` decorator:**

This is the v0.2.0 addition that changed how I use the library. Instead of manually checking corrections before every action, you decorate agent functions:

```python
from neveronce import Memory, guard

mem = Memory("my_agent")
mem.correct("never mass-email without approval", context="email")
mem.correct("never deploy on Fridays", context="deployment")

@guard(mem, mode="block")
def send_campaign(recipients: list, body: str):
    email_service.blast(recipients, body)

@guard(mem, mode="warn")
def deploy(version: str):
    push_to_prod(version)

send_campaign(all_clients, promo)  # → CorrectionWarning, blocked
deploy("v2.1")                     # → logs warning, proceeds
```

Three modes: `warn` (log + continue), `block` (raise exception), `review` (queue for human approval). Every invocation is logged to the `ActionLog` audit trail.

**Why FTS5 instead of embeddings:**

Embeddings are great for semantic similarity but overkill for retrieving things like "what did the user tell me about deployment rules?" — that's a keyword retrieval problem. SQLite FTS5 is fast, zero-dep, and accurate for exact-match recall. No vector DB to spin up, no embedding API to call, no latency.

**The `GuardedAgent` class:**

For agent framework integration, there's a `GuardedAgent` wrapper:

```python
from neveronce import Memory, GuardedAgent

mem = Memory("my_agent")
agent = GuardedAgent(mem, mode="block")

# Wraps any callable with guard logic
safe_deploy = agent.wrap(deploy_function)
safe_deploy("v2.1")  # checked against all corrections
```

Built-in integrations for OpenAI, Anthropic, LangChain, CrewAI, and AutoGen.

**Production numbers:** 87 corrections stored, most-used one surfaced 491 times. Zero repeats.

**Repo:** https://github.com/WeberG619/neveronce
**PyPI:** https://pypi.org/project/neveronce/

~800 lines. 74 tests. Zero dependencies beyond Python's standard library.

Happy to discuss the design — especially the guard-as-decorator pattern and the FTS5 vs embeddings tradeoff.

---

## r/MachineLearning

**Title:** Corrections as constraints + guard system for AI agents — design notes from 4 months production

**Body:**

I've been running a persistent correction system for AI agents in production for 4 months (1,421 memories, 87 corrections). I want to share the two architectural decisions that made the biggest difference: treating corrections differently from memories, and enforcing them as pre-flight guards.

**The problem with uniform memory:**

Most retrieval-augmented memory systems treat all stored facts equally and apply a uniform decay or recency-weighting scheme. This works fine until a model makes an error. If you correct it — "don't do X, do Y" — that correction gets stored as a regular memory and competes with hundreds of others during retrieval. The model repeats the mistake.

**Fix 1 — corrections as constraints, not memories:**

NeverOnce ([GitHub](https://github.com/WeberG619/neveronce)) introduces corrections as a separate primitive:

- Stored at maximum importance (1.0)
- Exempt from importance decay
- Always retrieved first, regardless of query relevance score
- Marked with `memory_type = 'correction'`

**Fix 2 — the guard system (v0.2.0):**

Corrections as constraints is necessary but not sufficient. You also need enforcement. The `@guard` decorator checks corrections before any function executes:

```python
from neveronce import Memory, guard

mem = Memory("my_agent")
mem.correct("never call external API without rate limiting", context="api")

@guard(mem, mode="block")
def call_api(endpoint: str, payload: dict):
    return requests.post(endpoint, json=payload)

call_api("/users", data)  # → Blocked: correction applies
```

Three enforcement modes:
- `warn` — log the correction, proceed anyway
- `block` — raise `CorrectionWarning`, halt execution
- `review` — queue for human approval before proceeding

Every guard invocation (pass or fail) is logged to an `ActionLog` for audit.

**Production result:** 87 corrections stored. Most-used correction surfaced 491 times across sessions. Zero instances of that mistake repeating.

**Why FTS5 over embeddings for this use case:**

The retrieval problem here is: "given the action about to be taken, what corrections apply?" That's not a semantic similarity problem — it's a keyword matching problem. FTS5 gives deterministic retrieval, zero external dependencies, no API calls, no latency, works offline. The tradeoff (no semantic generalization) is acceptable for corrections, which should be explicit and specific.

**The feedback loop:**

```
mark_helpful(memory_id) → importance += 0.1 (capped at 1.0)
time passes → importance *= decay_factor
corrections → exempt from decay, importance locked at 1.0
```

**Implementation:** ~800 lines Python, zero deps, SQLite+FTS5, 74 tests. MCP server included. Framework integrations for OpenAI, Anthropic, LangChain, CrewAI, AutoGen.

```bash
pip install neveronce
```

Curious what approaches others have taken for pre-execution safety checks in agent systems. Is "corrections as constraints + guard enforcement" a pattern used elsewhere?

---

## r/ClaudeAI

**Title:** NeverOnce v0.2.0 — a safety layer for Claude Code agents. Guard decorator blocks mistakes before they happen.

**Body:**

If you're running Claude Code agents and worried about them repeating mistakes — especially on consequential actions — I built something that fixes it.

**NeverOnce** — the pre-flight check for AI agents. It's an MCP server you add to your Claude config in about 2 minutes. v0.2.0 adds the `@guard` decorator and `GuardedAgent` class.

**Install:**

```bash
pip install neveronce
```

**Add to your Claude MCP config** (`claude_desktop_config.json` or `settings.local.json`):

```json
{
  "mcpServers": {
    "neveronce": {
      "command": "python",
      "args": ["-m", "neveronce.mcp_server"],
      "env": {
        "NEVERONCE_DB_PATH": "/path/to/your/memories.db"
      }
    }
  }
}
```

That's it. Claude now has persistent memory and a correction safety net across all sessions.

**What's new in v0.2.0 — the guard system:**

The headline feature is the `@guard` decorator. Instead of just hoping Claude remembers your corrections, you can enforce them programmatically:

```python
from neveronce import Memory, guard

mem = Memory("my_agent")
mem.correct("never push to main without tests passing", context="git")

@guard(mem, mode="block")
def git_push(branch: str):
    subprocess.run(["git", "push", "origin", branch])

git_push("main")  # → Blocked: correction applies
```

Three modes: `warn` (log it), `block` (stop it), `review` (queue for human).

**What it does:**

- Claude can store memories: "Weber prefers named pipes over HTTP for Revit"
- Claude can store *corrections*: "Never call the user Rick, his name is Weber"
- Corrections always surface first, never decay, never get buried
- The `@guard` decorator enforces corrections as pre-flight checks
- `ActionLog` gives you a full audit trail of every guarded action
- `GuardedAgent` wraps any agent function with correction checks

**The correction feature is the part I'm most proud of:**

If Claude makes a mistake and you correct it, that correction is stored at maximum importance and checked before every guarded action. It's not just another memory — it's a permanent safety constraint.

I've been running this for 4 months: 1,421 memories, 87 corrections, most-used correction surfaced 491 times. Zero repeats on corrected mistakes.

**MCP tools exposed:**

- `store_memory` — save something for later
- `retrieve_memories` — search by query
- `store_correction` — permanent, max-importance constraint
- `check_before_action` — pre-flight check against corrections
- `mark_helpful` — feedback signal to boost importance
- `get_stats` — see what's in your memory store

**GitHub:** https://github.com/WeberG619/neveronce
**PyPI:** https://pypi.org/project/neveronce/

~800 lines. 74 tests. Zero dependencies. Integrations for OpenAI, Anthropic, LangChain, CrewAI, AutoGen.

---

## r/LocalLLaMA

**Title:** NeverOnce v0.2.0 — AI agent safety layer. Guard decorator, audit trail, fully offline. No embeddings, no API keys.

**Body:**

Built a safety layer for AI agents that's completely local and works with any model. Thought this community would appreciate it.

**What it is:**

A pre-flight check system for AI agents. You store corrections (things your agent got wrong), then use the `@guard` decorator to catch those mistakes before the agent acts. SQLite + FTS5 under the hood. Zero external dependencies. No embedding models, no vector DB, no API keys required. Runs fully offline.

```bash
pip install neveronce
```

**Why it fits the local stack:**

- No embedding API calls (uses SQLite FTS5 for search)
- No cloud sync, no telemetry
- Database is a single `.db` file you own
- Works with Ollama, llama.cpp, LM Studio, anything — model-agnostic
- MCP server included for Claude Code, but the Python library works standalone

**The guard system (v0.2.0):**

```python
from neveronce import Memory, guard

mem = Memory("/home/user/.local/agent_safety.db")

# Store what went wrong
mem.correct("never run inference on the M4000 — it overheats at 78C", context="gpu")
mem.correct("always quantize to Q4_K_M, not Q8 — OOM on 8GB VRAM", context="model")

# Guard your agent functions
@guard(mem, mode="block")
def load_model(model_path: str, quantization: str):
    return llm.load(model_path, quant=quantization)

@guard(mem, mode="warn")
def run_inference(prompt: str):
    return llm.generate(prompt)

load_model("mistral-7b", "Q8")  # → Blocked: "always quantize to Q4_K_M"
run_inference("hello")           # → Warning logged, proceeds
```

Three modes: `warn`, `block`, `review`. Full `ActionLog` audit trail.

**Production numbers from my own setup:**

- 4 months running
- 1,421 memories stored
- 87 corrections
- Most-used correction: surfaced 491 times, zero repeats

**No GPU required, no model required, just Python and SQLite.**

~800 lines. 74 tests. Zero dependencies.

GitHub: https://github.com/WeberG619/neveronce
PyPI: https://pypi.org/project/neveronce/

---

## r/artificial

**Title:** The missing safety net in the AI agent stack: pre-flight checks that learn from corrections

**Body:**

We talk a lot about MCP (tool use), and we talk a lot about agents (autonomous loops). But there's a critical layer that nobody ships: **a safety net that prevents agents from repeating mistakes you've already caught.**

They gave us MCP for free. They gave us agents for free. But nobody gave us the safety net. Here it is.

---

**The problem:**

AI agents are getting more autonomous. They can call tools, make decisions, execute multi-step workflows. But they have no memory of what went wrong last time. No pre-flight check. No guard rails built from your own correction history.

If an agent makes a mistake and you correct it, that correction goes into... nowhere. It might land in a chat transcript that gets truncated. It might go into a RAG index where it competes with thousands of other facts. The agent repeats the mistake. You correct it again. The loop never closes.

---

**What I built:**

[NeverOnce](https://github.com/WeberG619/neveronce) — a safety layer for AI agents built around two ideas:

1. **Corrections are constraints, not memories.** They're stored at maximum importance, exempt from decay, and always surface first.
2. **The `@guard` decorator enforces constraints before execution.** Your agent functions get a pre-flight check against every relevant correction.

```python
from neveronce import Memory, guard

mem = Memory("my_agent")
mem.correct("never deploy on Fridays", context="deployment")

@guard(mem, mode="block")
def deploy(version: str):
    push_to_prod(version)

deploy("v2.1")  # → CorrectionWarning: "never deploy on Fridays"
```

Three enforcement modes: `warn` (log + continue), `block` (halt), `review` (queue for human approval). Every invocation logged to an `ActionLog` audit trail.

Four months in production. 87 corrections stored. Most-used one surfaced 491 times. Zero repeats.

---

**Why this matters at a systems level:**

The emerging agent stack looks something like:

1. **Tools** — what the AI can do (MCP solved this)
2. **Agency** — how the AI decides what to do (agents, reasoning models)
3. **Safety** — what the AI must never do again, and how we enforce it

The third pillar is underdeveloped. We have good infrastructure for (1) and improving infrastructure for (2), but (3) is mostly an afterthought — no standard for "here's what went wrong last time, and here's how we prevent it from happening again."

The hard problem isn't storage. SQLite is fine. The hard problem is **enforcement** — making sure the constraint is checked before the action, not after.

---

**The philosophical bit:**

There's something interesting about corrections as a category. When you correct an AI agent, you're not adding information — you're adding a constraint on future behavior. It has a different epistemic status than a fact. It's closer to a rule.

An agent system that doesn't distinguish between "the client is in EST" (fact, can decay) and "never mass-email without approval" (constraint, must persist and be enforced) is going to fail in production. The first one being wrong is a minor inconvenience. The second one being ignored is a fired employee.

---

**Practical:**

```bash
pip install neveronce
```

~800 lines Python, 74 tests, zero deps, MCP server included, SQLite under the hood. Framework integrations for OpenAI, Anthropic, LangChain, CrewAI, AutoGen.

[GitHub](https://github.com/WeberG619/neveronce) | [PyPI](https://pypi.org/project/neveronce/)

Curious what this community thinks about the safety layer problem — especially whether guard-as-decorator with correction-based constraints should be standardized across agent frameworks.
