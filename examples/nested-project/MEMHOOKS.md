---
schema: memhooks/v1
bank: example-project
scope: project-root
inherits: true

knowledge_pages:
  - "Architecture/System overview"
  - "Decisions/Current architecture"

recall_queries:
  - "What are the current architectural boundaries and non-negotiable project constraints?"
  - "Which major approaches were previously rejected, and why?"

entities:
  - Example Project

tags:
  - project:example

exclude:
  - abandoned v0 prototype

sensitivity: private
---

# Retrieval guidance

Prefer established project context and concrete past decisions. Do not resurrect abandoned v0 assumptions merely because they are semantically similar.
