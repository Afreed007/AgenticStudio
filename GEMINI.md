# Project Rules for "Agentic dev"

## 🚨 MANDATORY DOCUMENTATION MAINTENANCE RULE

In **every conversation and development task** within this project (`Agentic dev`), whenever you build, modify, extend, refactor, or test features, tools, agents, protocols, or configurations, you **MUST inspect and keep the following documentation files in the `documentations/` folder strictly synchronized and up-to-date**:

1. **`documentations/README.md`**:
   * Must explain how to use the multi-agent platform, CLI commands, options, runtime modes (Mock vs. Gemini), environment setup, and how to verify generated projects.
   * Whenever new CLI options, execution modes, or workflows are added, update this guide immediately.

2. **`documentations/architecture.md`**:
   * Must detail the complete structural blueprint of the multi-agent platform: A2A protocols, message bus routing, blackboard state machine, sandboxed workspace security, dual LLM engine, and all agent personas with their inbound/outbound contracts and tool boundaries.
   * Whenever new agents, tools, message types, or system topologies are altered, update this document and its diagrams.

3. **`documentations/prd.md`**:
   * Must reflect the product requirements, vision, user personas, functional requirements (epics), non-functional requirements (security, timeouts, circuit breakers), and acceptance criteria.
   * Whenever new features, user journeys, or quality gates are added or changed, update this document.

4. **`documentations/tdd.md`**:
   * Must document the Technical Design Document & Test-Driven Development (TDD) strategy: core data models/schemas, test suites (`tests/`), test execution instructions, and regression verification baselines.
   * Whenever new tests, schemas, or verification steps are created, update this document.

---

### Strict Execution Workflow
* **Documentation is not optional**: Do not complete a task or declare development finished without verifying that changes are reflected across all four documents in `documentations/`.
* **Accuracy Guarantee**: Ensure file paths, code snippets, command line flags, and test outputs documented in `documentations/` match the real codebase.
