---
name: memhooks
description: Directory-scoped memory retrieval routing. Use MEMHOOKS.md files from the workspace root to the active directory to recall the specific past decisions, events, entities, constraints, failures, and context needed before substantive work. Adapts itself to Hindsight, OpenViking, Honcho, or another available memory system without changing the memory backend.
version: 0.1.1
author: Aron Bijl
license: MIT
compatibility: Agent Skills / agentskills.io; Hermes Agent and Hermes Desktop; other skill-capable agents with filesystem access and optional memory tools.
metadata:
  hermes:
    tags: [memory, context, retrieval, continuity, coding, agent-memory]
    category: productivity
---

# MemHooks

MemHooks is a **retrieval-routing convention**, not a memory system.

Core rule:

> Before substantive work, locate every `MEMHOOKS.md` from the workspace root to the active directory, merge them from broadest to most local, then execute the prescribed bounded retrieval using the memory system currently available to the agent.

A MemHooks file tells you **what to recall here**. The attached memory backend determines **how to retrieve it**.

## Deterministic loader mode

When the bundled Hermes `pre_llm_call` shell hook is installed, do not rely on remembering to search for `MEMHOOKS.md` yourself. The hook has already walked the actual working directory root → leaf and injected the applicable files into the current user turn before this model call. Treat the injected `[MemHooks — deterministic pre-LLM retrieval routing]` block as authoritative routing input and execute its requested memory retrieval before substantive work.

The loader is in `hooks/hermes/memhooks_pre_llm.py`. It reads files locally and performs no model call of its own.

## When to use

Use this skill when:

- the current workspace or any parent directory contains `MEMHOOKS.md`;
- the user asks to initialize or update MemHooks for a project;
- you are about to edit, debug, redesign, delete, or substantially reason about files in a MemHooks-enabled tree;
- a task refers to previous project decisions, failures, constraints, events, or entities that may live in long-term memory.

Do not repeatedly re-run identical retrieval during the same local task unless the working directory, task, or relevant hook changed.

## Procedure

### 1. Locate the hook chain

Determine the workspace/repository root and active working directory.

Find `MEMHOOKS.md` at each directory level from root to the active directory. Read them root to leaf.

### 2. Merge root to leaf

Follow `references/memhooks-format.md`.

Default behavior:

- parent hooks are inherited;
- deeper hooks add specificity;
- exact duplicate list entries are de-duplicated;
- a local `inherits: false` cuts off inheritance above that file;
- the most local scalar value wins when scalars conflict.

Do not turn merged hooks into a giant context dump. They are instructions for **targeted retrieval**.

### 3. Identify the available memory system

Inspect the tools, configured memory provider, or environment already available to the agent.

If it matches one of the bundled references, read that reference before retrieval:

1. `references/memory-systems/01-hindsight.md`
2. `references/memory-systems/02-openviking.md`
3. `references/memory-systems/03-honcho.md`

If the backend is different, read `references/memory-systems/99-generic-or-unknown.md` and use the included systems as examples. A capable LLM should infer the closest native operations rather than refusing because the backend is not listed.

### 4. Execute the retrieval intent

Interpret the merged fields as follows:

- `recall_queries`: run these as specific memory searches/questions.
- `entities`: use them as entity filters when available; otherwise use them to sharpen or expand the recall queries.
- `tags`: use native tag/metadata filtering where available; otherwise treat them as relevance hints.
- `knowledge_pages`: retrieve named established summaries/pages/mental-model-like artifacts **if the current memory setup has an equivalent**. Do not create or update them here.
- `exclude`: prevent obsolete or unwanted memories from entering working context. Use native negative filters if available; otherwise post-filter results.
- `bank`: use the requested memory namespace only if that concept exists and the agent is authorized to access it.
- free-form Markdown below the frontmatter: treat as retrieval guidance, especially instructions about when to use shallow recall versus deeper synthesis.

Prefer direct retrieval first. Use a more expensive reasoning/reflection operation only when the hook requests it or when retrieved memories need synthesis to answer the stated question.

### 5. Keep retrieval bounded

Fetch enough context to satisfy the hooks, not the whole memory store. Stop when required queries have useful results and further retrieval is redundant or unrelated.

If a required query returns nothing, note that internally and continue. Do not fabricate continuity.

### 6. Do the actual task

Use the recalled context as ordinary task context. Preserve provenance when the memory system exposes it.

MemHooks should disappear into the workflow: it is successful when the agent simply remembers the right things before acting.

## Creating or updating `MEMHOOKS.md`

When asked to add MemHooks to a directory:

1. Inspect what that folder/subsystem is responsible for.
2. Identify the past context that would materially change future work there.
3. Write **specific recall questions**, not broad topic labels.
4. Add important named entities and useful backend-independent tags.
5. Add known obsolete approaches to `exclude` when they are likely retrieval traps.
6. Keep the file small. A hook file is a routing index, not memory content.

Good:

```yaml
recall_queries:
  - "Why did we choose a two-stage token refresh flow, and what alternatives were rejected?"
  - "What production failures have involved refresh-token rotation?"
```

Weak:

```yaml
recall_queries:
  - "authentication"
  - "project memory"
```

## Adapting to an unlisted memory backend

Do **not** require a bespoke MemHooks plugin.

Use the bundled backend references as worked examples and determine the new system's closest equivalents for direct recall, deeper synthesis, entity-aware retrieval, metadata filters, temporal filters, hierarchical summaries, and namespaces.

Then execute the hooks using those native operations.

If you have permission to improve this skill and the mapping is reusable, create a concise new file under `references/memory-systems/` following the style of the existing examples. Do not block the user's task merely because such a file does not yet exist.

## Hard boundary: retrieval only

`MEMHOOKS.md` must **not** itself trigger memory creation, retention, consolidation, deletion, or Knowledge Page generation.

Those belong to the memory system's normal lifecycle or a separate explicitly invoked dreaming/consolidation process.

MemHooks may point at existing summaries or memories. It does not manufacture them.

## Failure behavior

- No `MEMHOOKS.md`: continue normally.
- No memory backend/tools: continue normally; do not pretend retrieval occurred.
- Unknown backend: infer the mapping from available tools/docs and the reference examples.
- Search returns nothing: continue without invented context.
- Conflicting memories: use the backend's synthesis/reasoning operation if available, or surface the conflict rather than silently choosing.
- `exclude` conflicts with a parent include: the more local hook wins for the active subtree.

## Verification

Before acting on a MemHooks-enabled subtree, confirm that:

- the complete applicable hook chain was read;
- root-to-leaf inheritance was respected;
- the current memory backend was identified;
- listed queries were translated into native retrieval operations;
- excluded/obsolete material was not injected as current context;
- no memory was created or rewritten merely because MemHooks was loaded.
