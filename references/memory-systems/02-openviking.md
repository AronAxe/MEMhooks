# OpenViking mapping

Use this mapping when the active memory/context backend is **OpenViking** or Hermes exposes OpenViking memory tools.

OpenViking organizes context through a filesystem-style `viking://` hierarchy and supports hierarchical retrieval. In current Hermes integrations, tools may include operations similar to:

- `viking_search` — semantic/context search
- `viking_read` — progressively read selected context
- `viking_browse` — navigate the hierarchy
- `viking_remember` — write memory (**not used merely because MemHooks loaded**)
- `viking_forget` — delete memory (**not used by MemHooks**)

## Field mapping

### `recall_queries`
Use `viking_search` or the closest current search operation. Prefer context search for broad questions and exact/find operations when the hook identifies a known URI or target. Once relevant material is located, progressively read/browse rather than dumping an entire subtree into context.

### `entities`
Use the entity memory hierarchy where appropriate or include entity names in the search query.

### `tags`
Use metadata filters if exposed; otherwise treat tags as query/path hints.

### `knowledge_pages`
If a hook names a stable page/resource that exists in the OpenViking hierarchy, locate it and read only the required detail. Do not create or refresh it because of MemHooks.

### `exclude`
Avoid excluded URIs/subtrees when possible. Otherwise filter returned candidates before loading their content.

## Progressive retrieval

```text
search
  -> abstract / overview
      -> full detail only if needed
```

Use the actual OpenViking tools exposed by the current Hermes version rather than assuming exact names.

## Sources

- OpenViking docs: https://docs.openviking.ai/
- OpenViking memory docs: https://docs.openviking.ai/en/api/16-memory
- Hermes memory providers: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers/
