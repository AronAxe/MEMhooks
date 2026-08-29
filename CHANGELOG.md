# Changelog

## 0.1.1 — 2026-08-29

- Added a real Hermes `pre_llm_call` shell hook that deterministically loads applicable `MEMHOOKS.md` files before every user-turn LLM call.
- Added root detection, root-to-leaf loading, `inherits: false`, and bounded context injection without an extra model call.
- Added Hermes hook installation/config documentation.
- Clarified the split between deterministic hook loading and memory-backend-specific retrieval.

## 0.1.0 — 2026-08-29

- Initial public skill/spec package.
- Root-to-leaf `MEMHOOKS.md` inheritance.
- Retrieval-only boundary.
- Hindsight, OpenViking, and Honcho mappings.
- Generic self-adaptation guidance for unlisted memory systems.
- Hermes / Agent Skills compatible `SKILL.md` layout.
