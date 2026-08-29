---
schema: memhooks/v1
inherits: true

# Optional: memory namespace/bank/peer/session hint when the backend has one.
# bank: project-name

# Optional descriptive scope.
# scope: backend/auth

# Existing stable summaries/pages/mental models worth retrieving first.
knowledge_pages: []

# Specific questions whose answers matter when working in this directory.
recall_queries:
  - "What architectural decisions govern this subsystem, and why were they made?"
  - "What previous failures, rejected approaches, or important gotchas should be remembered before changing it?"

# Named concepts that should sharpen retrieval.
entities: []

# Backend-independent relevance hints; use native metadata filters when supported.
tags: []

# Obsolete or misleading memories that should not enter current context.
exclude: []

# Advisory only: public | internal | private
sensitivity: private
---

# Retrieval guidance

Use direct recall for concrete decisions, events, and implementation facts.
Use deeper memory reasoning only when synthesis is actually required.
