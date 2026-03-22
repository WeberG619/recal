---
title: "NeverOnce: The Pre-Flight Check for AI Agents"
published: false
description: Your AI agent doesn't need more memory. It needs a safety net. 87 corrections, 491 surfaces, zero repeats — and a @guard decorator that stops mistakes before they happen.
tags: ai, python, opensource, machinelearning
cover_image:
---

Your AI agent just mass-emailed every client with last quarter's pricing. Again.

You corrected it last Thursday. But corrections don't survive between sessions. There's no pre-flight check. No guard rails. The agent just... goes.

That's why I built [NeverOnce](https://github.com/WeberG619/neveronce) — a safety layer for AI agents. v0.2.0 ships the `@guard` decorator, `GuardedAgent` class, `ActionLog` audit trail, and framework integrations for OpenAI, Anthropic, LangChain, CrewAI, and AutoGen.

~800 lines of Python. 74 tests. Zero dependencies. The pre-flight check for AI agents.

---

## The Guard System

This is the headline feature. Instead of hoping your agent remembers what went wrong last time, you enforce it:

```python
from neveronce import Memory, guard

mem = Memory("my_agent")
mem.correct("never deploy on Fridays", context="deployment")
mem.correct("never mass-email without approval", context="email")

@guard(mem, mode="block")
def deploy(version: str):
    push_to_prod(version)

@guard(mem, mode="review")
def send_campaign(recipients: list, body: str):
    email_service.blast(recipients, body)

deploy("v2.1")  # → CorrectionWarning: "never deploy on Fridays"
send_campaign(all_clients, promo)  # → queued for human review
```

Three modes:

- **`warn`** — log the matching correction, proceed anyway
- **`block`** — raise `CorrectionWarning`, halt execution
- **`review`** — queue the action for human approval before proceeding

Every invocation — pass or fail — is logged to the `ActionLog`. Full audit trail of what your agent tried to do and what got caught.

---

## The `GuardedAgent` Class

For agent frameworks, there's a wrapper that adds guard logic to any callable:

```python
from neveronce import Memory, GuardedAgent

mem = Memory("my_agent")
mem.correct("never call external API without rate limiting", context="api")

agent = GuardedAgent(mem, mode="block")

safe_api_call = agent.wrap(call_external_api)
safe_api_call("/users", payload)  # checked against all corrections
```

Built-in integrations for OpenAI, Anthropic, LangChain, CrewAI, and AutoGen. Drop NeverOnce into your existing agent stack without rewriting anything.

---

## The Amnesia Tax

I'm a BIM specialist. I run AI-assisted workflows all day — Revit automation, construction document processing, client deliverables. Claude, Cursor, custom agents. AI is core to how I work.

And every single session, I was paying what I started calling the **amnesia tax**.

You know the feeling. You spend 15 minutes telling your AI assistant how you work. "I use named pipes, not HTTP." "Always format dates like this." "Never do X — I told you last week, we tried it, it broke everything." The AI nods along, does it right for the rest of the session. Then the session ends. Next morning, you start over.

The 1M context window isn't memory. It's short-term recall that dies when the tab closes.

I got tired of it. So I built the fix.

---

## Corrections as Constraints

Most AI memory systems treat all memories equally. The problem: if an AI makes a mistake and you correct it, that correction competes with 1,000 other memories in retrieval. It'll resurface again.

NeverOnce treats corrections differently from memories:

- A **memory** is something I want the AI to know: "client prefers PDF deliverables"
- A **correction** is something the AI got wrong and must never get wrong again: "do NOT use the HTTP endpoint — it's deprecated and breaks silently"

These are architecturally different things. A correction isn't just a high-importance memory. It's a **behavioral constraint** — it should surface first, stay at full strength, and never fade. It's the difference between a sticky note and a stop sign.

```python
mem.correct("NEVER use HTTP for the Revit API — always use named pipes.")
```

Corrections are stored with:

- **Max importance score** (1.0) — they always rank first
- **Decay immunity** — they don't fade over time, ever
- **Type flag** — queryable separately from regular memories
- **Always-first surfacing** — corrections matching the query come back before any regular memory

And now with v0.2.0, the `@guard` decorator **enforces** them automatically. Corrections aren't just suggestions — they're pre-flight checks.

---

## The Five-Step Loop

NeverOnce is built around: **Store, Recall, Correct, Feedback, Decay**.

### Store

```python
from neveronce import Memory

mem = Memory("my_workflow")
mem.store("client prefers detailed cost breakdowns in proposals")
```

Under the hood: SQLite + FTS5, BM25 ranking. No external dependencies.

### Recall

```python
results = mem.recall("how does the client want proposals formatted?")
```

Corrections always surface before regular memories.

### Correct

```python
mem.correct("NEVER use HTTP for the Revit API — always use named pipes.")
```

### Guard (new in v0.2.0)

```python
@guard(mem, mode="block")
def connect_to_revit(method: str):
    return revit_api.connect(method)

connect_to_revit("http")  # → Blocked
```

### Feedback

```python
mem.feedback(memory_id, helpful=True)   # strengthens importance
mem.feedback(memory_id, helpful=False)  # weakens importance
```

### Decay

```python
mem.decay()  # regular memories fade; corrections never do
```

---

## Production Numbers (4 Months In)

I've been running this on my actual daily workflows since November:

| Metric | Value |
|--------|-------|
| Total memories | 1,421 |
| Corrections | 87 |
| Most-surfaced correction | 491 times |
| Repeated mistakes after correction | 0 |

That most-surfaced correction? It's about a specific API behavior in my Revit bridge that bit me once in a spectacular way. I stored the correction, the guard system has caught it 491 times across dozens of sessions, and I have not made that mistake again.

---

## Why SQLite + FTS5 (And Not a Vector DB)

NeverOnce uses SQLite with FTS5 full-text search. No embeddings. No API calls. No external dependencies.

The choice is intentional:

**Corrections are behavioral overrides, not similarity queries.** When I store "never use HTTP — use named pipes," I need that to surface when the agent tries to set up an HTTP connection. BM25 with FTS5 handles this well.

**Zero dependencies is a feature.** The library is ~800 lines. You can read the whole thing. There's nothing magic. No vector DB to operate, no embedding API latency, no rate limits.

**SQLite is everywhere.** Python ships with sqlite3. No setup, no daemon. The database is a single file. Backup is `cp`.

---

## The MCP Server

NeverOnce ships with an MCP server out of the box:

```bash
pip install neveronce

# Add to your MCP config
{
  "mcpServers": {
    "neveronce": {
      "command": "python",
      "args": ["-m", "neveronce.mcp_server"]
    }
  }
}
```

Your AI client gets access to `store_memory`, `recall_memory`, `store_correction`, `check_before_action`, and `memory_feedback` as tools.

---

## The Stack: MCP + Agents + NeverOnce

They gave us MCP for free. They gave us agents for free. But nobody gave us the safety net.

- **MCP** solves the tool connectivity problem
- **Agents** solve the multi-step reasoning problem
- **NeverOnce** solves the safety problem — your agent can't repeat mistakes you've already caught

The first two are largely solved. The third is not. There are production-grade agent frameworks. There are MCP servers for everything. There is no standard for "here's what went wrong last time, and here's how we enforce that it never happens again."

That's the gap. Not a better vector database. Not a smarter embedding model. A `@guard` decorator that checks corrections before your agent acts.

---

## Getting Started

```bash
pip install neveronce
```

```python
from neveronce import Memory, guard

mem = Memory("my_project")

# Store what matters
mem.store("client is in EST timezone — all meetings before 3pm PST")

# Correct what was wrong
mem.correct("NEVER send draft documents directly — always export to PDF first")

# Guard your agent functions
@guard(mem, mode="block")
def send_document(client: str, doc_path: str):
    email_client.send(client, attachment=doc_path)

# Check manually when needed
warnings = mem.check("sending the document to client")
```

The full source is at [github.com/WeberG619/neveronce](https://github.com/WeberG619/neveronce). MIT licensed. ~800 lines. 74 tests. Zero dependencies beyond Python's standard library.

Framework integrations: OpenAI, Anthropic, LangChain, CrewAI, AutoGen.

---

*Weber Gouin is a BIM specialist and principal at [BIM Ops Studio](https://bimopsstudio.com), building AI-assisted workflows for the AEC industry. NeverOnce is at [github.com/WeberG619/neveronce](https://github.com/WeberG619/neveronce).*
