---
schema: memhooks/v1
scope: backend/auth
inherits: true

recall_queries:
  - "Why was the current token refresh architecture chosen, and what alternatives were rejected?"
  - "What previous bugs or production failures involved token rotation, session expiry, or authentication state?"

entities:
  - authentication
  - refresh token
  - session expiry

tags:
  - subsystem:auth

exclude:
  - deprecated cookie-only prototype
---

# Retrieval guidance

Before changing authentication behavior, recall the design rationale and incident history. If the evidence disagrees, use the current memory backend's deeper reasoning/synthesis operation rather than guessing.
