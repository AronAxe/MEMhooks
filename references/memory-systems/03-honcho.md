# Honcho mapping

Use this mapping when the active memory backend is **Honcho** or Hermes exposes Honcho memory-provider tools.

In current Hermes integrations, Honcho provides tools similar to:

- `honcho_search` — semantic search over remembered context/conclusions
- `honcho_context` — session summary, representation, card, recent messages
- `honcho_reasoning` — synthesized/dialectic reasoning over memory
- `honcho_profile` — peer card read/update
- `honcho_conclude` — create/delete conclusions

MemHooks is retrieval-only, so it should ordinarily use **search, context, and reasoning**, not profile updates or conclusion writes.

## Field mapping

### `recall_queries`
Use `honcho_search` for concrete past context, decisions, events, excerpts, or conclusions. Use `honcho_reasoning` only when the hook calls for synthesis across remembered material or direct search returns conflicting fragments.

### `entities`
Include important names/components explicitly in the search or reasoning query. If the current Honcho version exposes metadata filters, use them where helpful.

### `tags`
Use native filtering when available; otherwise treat tags as query hints.

### `knowledge_pages`
Map stable-context requests to the nearest existing Honcho representation: session context, peer/user representation, or searchable conclusions. Retrieve only; do not call `honcho_conclude` merely to satisfy a MemHooks file.

### `bank`
Respect the already configured Hermes/Honcho peer/session/project mapping. Do not remap or create a new session solely because a MemHooks `bank` value exists.

### `exclude`
Filter obsolete results before use and, where needed, phrase queries to distinguish current conclusions from rejected/old approaches.

## Search vs reasoning

```text
"what happened / what did we decide / find context"
    -> honcho_search

"why / what pattern / reconcile memories"
    -> honcho_reasoning
```

`honcho_context` is useful when the hook concerns the current mapped session/project as a whole and that context already contains the required information.

## Sources

- Honcho docs: https://docs.honcho.dev/
- Hermes Honcho integration: https://hermes-agent.nousresearch.com/docs/user-guide/features/honcho/
- Honcho GitHub: https://github.com/plastic-labs/honcho
