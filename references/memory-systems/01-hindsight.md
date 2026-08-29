# Hindsight mapping

Use this mapping when the active memory backend is **Hindsight** (Vectorize) or Hermes exposes Hindsight memory tools.

Hindsight's core operations are:

- **Recall** — retrieves ranked memories using semantic, keyword/BM25, graph/entity, and temporal strategies.
- **Reflect** — reasons over memories and synthesizes an answer; slower and more expensive than direct recall.
- **Retain** — writes memory. **MemHooks does not call this merely because a hook was loaded.**

Hindsight classifies facts as `world`, `experience`, and `observation`; observations are consolidated, evidence-grounded knowledge. Hindsight also has entities and mental models.

## Field mapping

### `recall_queries`
Run each relevant query through Hindsight `recall` / Hermes `hindsight_recall` first. Use natural-language questions. Do not collapse several precise questions into one vague query.

If fact-type filtering is available, infer it only when clear:
- external/project facts → `world`
- past interactions/incidents/actions → `experience`
- consolidated settled knowledge → `observation`

### `entities`
Use entity constraints when exposed; otherwise mention relevant entities explicitly in the natural-language query so graph retrieval can help.

### `tags`
Use tag/metadata filters when available. Otherwise incorporate meaningful tag concepts into the query.

### `knowledge_pages`
If the local integration has curated Knowledge Pages or an equivalent mental-model layer, retrieve them as stable context first. Do not create or update them here.

### `exclude`
Use filtering metadata where possible. Otherwise remove excluded/obsolete results before they enter working context and sharpen queries to distinguish current from obsolete approaches.

## Recall vs reflect

```text
specific fact / event / decision
    -> recall

multiple memories must be reconciled
or the hook asks for synthesis
    -> reflect
```

Use `reflect` deliberately. Routine folder entry should not trigger expensive reflection when direct recall already supplies the context.

## Hermes-native names

Depending on version, tools may be exposed as names similar to `hindsight_recall`, `hindsight_reflect`, and `hindsight_retain`. Use the actual tools present rather than assuming exact names.

## Sources

- Hindsight developer docs: https://github.com/vectorize-io/hindsight/tree/main/skills/hindsight-docs
- Hindsight docs: https://docs.hindsight.vectorize.io/
- Hermes native Hindsight integration: https://github.com/vectorize-io/hindsight
