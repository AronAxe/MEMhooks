<p align="center"><img src="assets/memhooks-logo-original.jpg" alt="MemHooks logo" width="210" /></p>

<h1 align="center">MemHooks</h1>
<p align="center"><strong>Mnemonic devices for agents.</strong></p>
<p align="center">Filesystem-scoped memory recall · <em>Hook the right memories into the right context.</em> 🎣</p>

<p align="center"><img alt="Agent Skills" src="https://img.shields.io/badge/Agent%20Skills-compatible-7c4dff" /> <img alt="Hermes" src="https://img.shields.io/badge/Hermes-compatible-00bcd4" /> <img alt="Memory agnostic" src="https://img.shields.io/badge/memory-backend%20agnostic-2ea44f" /> <img alt="Version" src="https://img.shields.io/badge/version-0.2.0-orange" /> <img alt="License" src="https://img.shields.io/badge/license-MIT-blue" /></p>

<p align="center"><img src="assets/memhooks-hero.svg" alt="How MemHooks works" width="100%" /></p>

## The idea

> **You can't recall what you don't know you know.**

An agent can have the right memory stored perfectly and still fail to use it, because retrieval begins with a cue. If the agent no longer remembers that an old decision, failure, workaround, constraint, or insight even exists, it may never formulate the search that would bring that memory back.

That is the gap MemHooks is meant to fill. It stores the **cue to remember**, close to the code or folder where that cue matters.

Your agent may already **have** the right memory. The failure is often simpler: it never realizes that *this folder* is where that memory matters.

MemHooks fixes that with tiny, directory-scoped `MEMHOOKS.md` files.

> **Memory systems know how to remember. MemHooks tells the agent what to recall here.**

A MemHook contains retrieval routing — specific recall questions, entities, tags, useful stable summaries, and even things that should **not** be recalled. Before substantive work, the agent walks from the workspace root to the active directory, merges the applicable hooks, adapts them to whatever memory system is available, performs bounded recall, and then gets on with the job.

## Why it exists

Long-term memory does not automatically imply good recall. Semantic similarity alone can miss old architectural decisions, rejected approaches, weird platform gotchas, or the reason some apparently ridiculous line of code exists.

A folder is already a strong contextual cue. MemHooks makes that cue explicit.

- **Filesystem-scoped** — context follows the part of the project being touched.
- **Inherited** — broad project knowledge at the root, increasingly specific hooks deeper down.
- **Agent-agnostic** — the skill describes the behavior, not one specific harness.
- **Memory-agnostic** — examples are provided for Hindsight, OpenViking and Honcho; an LLM can infer the equivalent operations for another backend.
- **Retrieval-only** — MemHooks does not create, rewrite, consolidate or delete memories.
- **Anti-recall too** — `exclude` lets you keep obsolete but semantically tempting memories out of working context.
- **Cheap by design** — small files, bounded retrieval, no database or daemon of its own.

## A minimal hook

```md
---
schema: memhooks/v1
inherits: true
recall_queries:
  - "Why is this authentication subsystem designed this way?"
  - "What previous failures or rejected fixes involved refresh-token rotation?"
entities:
  - authentication
  - refresh token
exclude:
  - obsolete OAuth prototype
---
```

That file contains **no memory itself**. It tells the agent which memories are worth retrieving before it touches this subtree.

## Who fills `MEMHOOKS.md`?

A hook that never changes would eventually become useless, so MemHooks includes a **zero-LLM maintainer**. The default design deliberately does **not** run a second model after every session.

There are two maintenance paths:

1. **Deterministic auto-anchors — zero model tokens.** `scripts/memhooks_update.py` can run on `post_tool_call`, inspect files touched, and create/refresh small machine-managed recall anchors.
2. **Same-turn semantic cues — no extra LLM call.** If the current agent discovers a non-obvious decision, failure mode, constraint, or rejected approach, it can call the script's `note` command while already reasoning, adding one concise future retrieval question rather than the answer.

> **The memory backend stores what happened. MemHooks stores the cue that tells a future agent there is something worth recalling.**

## Runtime hook support

The **MemHooks convention, maintainer, and `SKILL.md` are agent-agnostic**. The current executable lifecycle integration is Hermes-specific because runtimes expose hooks differently.

- **Hermes / Hermes Desktop:** working `pre_llm_call` loading and `post_tool_call` maintenance under [`hooks/hermes/`](hooks/hermes/).
- **Other agents:** can use the skill/spec and generic maintainer immediately; a thin adapter only needs to fire before the model call, determine the active directory, load/merge `MEMHOOKS.md`, inject it into context, and pass tool events to the maintainer.

## Related: Token Terminator

If MemHooks is about **retrieving the right context**, [**Token Terminator**](https://github.com/AronAxe/Token-Terminator) is about **not wasting tokens on the wrong context**.

## Status

**v0.2.0 — experimental convention / agent skill + deterministic load-and-maintain runtime.**

## License

MIT © 2026 Aron Bijl
