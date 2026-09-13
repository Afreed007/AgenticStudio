---
name: maintain-documentations
description: |
  Ensures that whenever development or modifications occur in the "Agentic dev" multi-agent project,
  the 4 core files in the `documentations/` directory (README.md, architecture.md, prd.md, tdd.md)
  are reviewed, synchronized, and kept current with all new features and updates.
---

# Documentation Maintenance Skill for Agentic Studio

Whenever developing in this project, this skill enforces that the 4 documentation files in `documentations/` are actively maintained.

## Core Documents to Maintain in `documentations/`:

1. `documentations/README.md`
   * Platform user manual, usage instructions, CLI flags, setup steps, and project verification guide.
2. `documentations/architecture.md`
   * System topology, A2A message contracts, event bus, blackboard state machine, agent personas, and circuit breakers.
3. `documentations/prd.md`
   * Product requirements document, user stories, epics, functional and non-functional requirements.
4. `documentations/tdd.md`
   * Technical design document & test-driven development guide, data models, test suites, and regression baselines.

## Maintenance Checklist on Every Task:
* [ ] Were any CLI flags or runtime options added or modified? -> Update `documentations/README.md`.
* [ ] Were any new agents, tools, message types, or workflows created? -> Update `documentations/architecture.md`.
* [ ] Were any requirements, user stories, or acceptance criteria changed? -> Update `documentations/prd.md`.
* [ ] Were any test files, schemas, or verification procedures added or changed? -> Update `documentations/tdd.md`.
