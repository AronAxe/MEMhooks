# Generic / unknown memory backend

MemHooks must not become an adapter framework. If the current backend is not listed, **infer the mapping from the tools or documentation already available to you**.

Use Hindsight, OpenViking, and Honcho as examples of the pattern, not as required dependencies.

## Step 1 — inspect capabilities

Identify the backend's native equivalents, if present, for:

- direct memory search / recall;
- deeper synthesis / reasoning over memory;
- entity-aware lookup;
- tags / metadata filters;
- temporal filters;
- hierarchical pages, summaries, or curated models;
- namespace / bank / peer / session selection.

Do not invent capabilities the backend does not expose.

## Step 2 — map MemHooks fields

- `recall_queries`: map to the backend's most direct retrieval/search primitive first.
- `entities`: use native entity filtering when available; otherwise put names into the natural-language query.
- `tags`: use metadata filters when available; otherwise use as query hints.
- `knowledge_pages`: map to an existing summary/page/mental-model construct if one exists. If there is no equivalent, ignore rather than manufacturing one.
- `exclude`: use negative filtering if supported; otherwise post-filter results before placing them in working context.

If the backend has a `reflect`, `reason`, `synthesize`, `ask memory`, or similar operation, reserve it for hooks requiring synthesis or conflict resolution rather than routine lookup.

## Step 3 — execute, don't overbuild

Do not stop the user's task to write integration code. A competent LLM can usually translate a question like `What did we decide about X?` into whatever search primitive the current memory system exposes.

If the mapping proves reusable **and** you have permission to edit this skill, add a concise new reference file under `references/memory-systems/` modeled on the existing three. Keep it descriptive rather than executable unless the backend genuinely requires code.

## If there is no memory backend

Fail open. Continue the task without claiming recall occurred.
