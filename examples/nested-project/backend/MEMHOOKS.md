---
schema: memhooks/v1
scope: backend
inherits: true

recall_queries:
  - "What backend-specific design decisions, dependencies, and operational constraints have already been settled?"
  - "What backend incidents or failed implementation approaches should not be repeated?"

entities:
  - API
  - database

tags:
  - subsystem:backend
---

# Retrieval guidance

Direct recall is normally sufficient. Escalate to memory synthesis only if previous decisions conflict.
