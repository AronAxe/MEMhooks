# `MEMHOOKS.md` format — memhooks/v1

A `MEMHOOKS.md` file is Markdown with YAML frontmatter. The frontmatter is retrieval-routing metadata. The body is optional human/agent-readable retrieval guidance.

## Canonical shape

```md
---
schema: memhooks/v1
bank: optional-memory-namespace
scope: optional/human-readable/subsystem
inherits: true

knowledge_pages:
  - "Architecture/Authentication"

recall_queries:
  - "Why was the current authentication architecture selected?"
  - "What previous failures or rejected fixes involved token refresh?"

entities:
  - Authentication
  - Refresh Token

tags:
  - project:example
  - subsystem:auth

exclude:
  - obsolete OAuth prototype
  - deprecated session-store experiment

sensitivity: private
---

# Retrieval guidance

Use direct recall for concrete decisions and incidents.
Use deeper synthesis only when the retrieved memories conflict or the rationale remains unclear.
```

## Fields

### `schema`
Required. For this version use `schema: memhooks/v1`.

### `inherits`
Optional; default `true`. With `false`, this file starts a new hook scope and ancestors above it are ignored for the current subtree.

### `scope`
Optional descriptive path/subsystem label. It is a hint, not authoritative filesystem state.

### `bank`
Optional memory namespace/bank/peer/session hint. Use it only when the current backend has an equivalent and access is appropriate.

### `recall_queries`
The heart of MemHooks. Each entry should be a specific natural-language retrieval question whose answer would materially improve work in this directory.

Prefer `What architectural decisions govern this subsystem, and why were they made?` over a vague keyword such as `architecture`.

### `entities`
Named people, projects, services, components, concepts, or other entities likely to improve recall precision. Backends with entity-aware retrieval may use them directly. Others can incorporate them into natural-language queries.

### `tags`
Optional tag/metadata hints. Use native filters when available; otherwise treat them as context for query construction.

### `knowledge_pages`
Optional references to existing curated summaries, mental models, project pages, or equivalent stable context.

**Retrieval only.** Loading a MemHooks file never authorizes the agent to create, ensure, rewrite, refresh, or delete such pages.

### `exclude`
Memories, approaches, entities, branches, or topics that should not be returned as current context for this subtree. This is intentionally first-class because obsolete but semantically similar memories can poison an otherwise good retrieval.

Use native negative filtering where available; otherwise filter returned results before adding them to working context.

### `sensitivity`
Optional advisory classification such as `public`, `internal`, or `private`. Respect the privacy boundary of the already configured memory system.

## Machine-maintained body blocks

A runtime may maintain bounded retrieval cues in the Markdown body without rewriting hand-authored frontmatter. The reference maintainer uses two reserved blocks:

```md
<!-- memhooks:auto:start -->
## Auto-maintained recall anchors
...
<!-- memhooks:auto:end -->

<!-- memhooks:notes:start -->
## In-session retrieval cues
...
<!-- memhooks:notes:end -->
```

`auto` contains deterministic path-scoped anchors generated from tool activity. `notes` contains concise future-retrieval questions recorded during the same turn in which a non-obvious decision/failure/constraint was discovered.

These blocks are still **retrieval metadata, not memory content**. Implementations should preserve everything outside their own managed markers and keep the blocks bounded.

## Merge semantics

For the active directory:

1. Find all `MEMHOOKS.md` files from workspace root to leaf.
2. If a leafward file sets `inherits: false`, discard ancestors above that file.
3. Merge remaining files root → leaf.
4. Append list fields (`recall_queries`, `entities`, `tags`, `knowledge_pages`, `exclude`) and de-duplicate exact duplicates.
5. For scalar fields (`bank`, `scope`, `sensitivity`), the most local value wins.
6. Append free-form guidance root → leaf; local guidance has priority when instructions conflict.
7. Treat machine-maintained body blocks exactly as local retrieval guidance; do not interpret them as durable memory facts.

## Maintenance principle

The memory backend stores the actual event/decision/fact. `MEMHOOKS.md` stores only enough information to make a future agent realize **what it should ask memory about**.

Prefer deterministic maintenance where possible. A separate LLM summarization pass should not be required merely to keep the routing file alive.

## Non-goals

`MEMHOOKS.md` is not a memory database, hidden prompt dump, README replacement, memory-retention policy, dreaming/consolidation trigger, or reason to retrieve everything remotely related to the task.
