# Agentic Studio - System Architecture Specification

## 1. Architectural Overview

Agentic Studio is structured around a **Hybrid Hierarchical + Peer-Review** multi-agent topology. Rather than relying on rigid, linear prompt chains, the platform models a real-world software development agency where independent, specialized agents collaborate, negotiate, challenge, and review each other's work over a typed **Agent-to-Agent (A2A)** protocol.

```
                                  [ Client / Sponsor ]
                                           │
                                  (SCOPING_REQUEST)
                                           │
                                           ▼
                                 [ BusinessAnalyst ]
                                           │
                                    (PRD_GENERATED)
                                           │
                                           ▼
                                [ SolutionsArchitect ]
                                           │
                                 (ARCH_SPEC_GENERATED)
                                           │
                                           ▼
                                  [ ProjectManager ]
                                           │
                                   (TASK_ASSIGNMENT)
                                           │
                                           ▼
                                   [ DeveloperAgent ]
                                           │
                                   (TASK_SUBMISSION)
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
                [ QAEngineer ]                         [ CodeReviewer ]
                 - Pytest sandbox runner                - Security & AST audit
                 - Fails: A2A BUG_REPORT                - Fails: A2A CODE_REVIEW_REJECTED
                 - Passes: A2A APPROVAL                 - Passes: A2A CODE_REVIEW_APPROVED
                        └──────────────────┬──────────────────┘
                                           │
                                    (TASK_APPROVED)
                                           │
                                           ▼
                                  [ ProjectManager ]
                                  (Check Remaining)
                                           │
                                   (All Tasks Done)
                                           │
                                           ▼
                                  [ DevOpsEngineer ]
                                           │
                                  (DELIVERY_COMPLETE)
                                           │
                                           ▼
                                  [ Client / Handover ]
```

---

## 2. Core Architectural Pillars

### Pillar 1: Typed Agent-to-Agent (A2A) Protocol (`agentic_studio/protocol/`)
* **Typed Envelopes (`A2AMessage`)**: Agents do not send unconstrained natural language to each other. Every communication is wrapped in a structured Pydantic model containing `message_id`, `timestamp`, `sender`, `recipient`, `action`, `ticket_id`, and a validated typed `payload`.
* **Action Types (`ActionType`)**:
  * `SCOPING_REQUEST`: Client prompt -> Business Analyst.
  * `PRD_GENERATED`: Product requirements specification.
  * `ARCH_SPEC_GENERATED`: Technical design, OpenAPI specs, and DB schema.
  * `TASK_ASSIGNMENT`: PM dispatches a ticket to Developer.
  * `TASK_SUBMISSION`: Developer submits code for review.
  * `BUG_REPORT`: QA sends test failure details, stdout/stderr, and stack traces.
  * `CODE_REVIEW_REJECTED`: Security auditor flags vulnerabilities or anti-patterns.
  * `CODE_REVIEW_APPROVED` & `TASK_APPROVED`: Quality gates cleared.
  * `DELIVERY_COMPLETE`: DevOps delivers packaged release.
  * `ESCALATE`: Circuit breaker triggers when retries exceed thresholds.

### Pillar 2: In-Memory Message Bus (`A2ABus`)
* **Decoupled Delivery**: Agents register their incoming mailbox callbacks. The bus routes messages to the intended recipient and logs every exchange to `message_history` for full auditability.
* **Observer Pattern**: External systems (such as the Rich terminal CLI or potential web dashboards) subscribe to the bus to stream real-time events without modifying agent logic.
* **Dead-Letter Handling**: If a message targets an unregistered recipient, it is safely recorded in the audit log without crashing the system.

### Pillar 3: State Blackboard (`agentic_studio/blackboard/`)
* **`TaskBoard`**: Maintains the global list of project tickets. Tickets transition through an explicit state machine:
  $$\text{TODO} \longrightarrow \text{IN\_PROGRESS} \longrightarrow \text{IN\_REVIEW} \longrightarrow \text{DONE} \quad (\text{or } \text{BLOCKED})$$
* **Dependency Resolution**: `TaskBoard.get_next_actionable_ticket()` ensures tickets are only dispatched when all their prerequisite dependencies (`dependencies: List[str]`) have reached the `DONE` state.

### Pillar 4: Sandboxed Workspace Security (`WorkspaceManager`)
* **Isolation**: All target software files (source code, tests, configs, documentation) are written to an isolated directory (`./target_project` or user-specified).
* **Path Traversal Protection**: `_resolve_safe()` canonicalizes paths and validates that all file reads and writes remain strictly within the workspace boundary, throwing security exceptions on `../` traversal attacks.

### Pillar 5: Dual LLM Provider Engine (`agentic_studio/llm/`)
* **Google Gemini Integration**: Uses `google-genai` SDK (`gemini-2.5-flash` or `gemini-2.0-flash`) with structured JSON schema enforcement.
* **Deterministic Mock Fallback**: When running offline, in CI/CD, or during automated test suites, `MockLLMProvider` generates realistic, deterministic responses for all 7 agent personas without requiring network access or API credentials.

---

## 3. Specialized Agent Personas & Boundaries

| Agent Persona | Role in Agency | Inbound Action | Outbound Action | Tools Utilized |
| :--- | :--- | :--- | :--- | :--- |
| **BusinessAnalyst** | Product Discovery | `SCOPING_REQUEST` | `PRD_GENERATED` | LLM JSON Generator |
| **SolutionsArchitect** | System Architecture | `PRD_GENERATED` | `ARCH_SPEC_GENERATED` | Schema & Spec Writer |
| **ProjectManager** | Scrum Master | `ARCH_SPEC_GENERATED`, `TASK_APPROVED` | `TASK_ASSIGNMENT` | TaskBoard Blackboard |
| **DeveloperAgent** | Software Engineer | `TASK_ASSIGNMENT`, `BUG_REPORT` | `TASK_SUBMISSION` | Workspace File Tools |
| **QAEngineer** | Quality Automation | `TASK_SUBMISSION` | `BUG_REPORT`, `TASK_SUBMISSION` | Sandboxed Subprocess Pytest Runner |
| **CodeReviewer** | Security Auditor | `TASK_SUBMISSION` | `CODE_REVIEW_REJECTED`, `TASK_APPROVED` | AST & Static Analysis Auditor |
| **DevOpsEngineer** | Release Packaging | `TASK_ASSIGNMENT` (`sprint_complete`) | `DELIVERY_COMPLETE` | Dockerfile & README Generator |

---

## 4. Fault Tolerance & Circuit Breakers

* **Loop Prevention**: To prevent infinite rebuttals between Developer and QA/Security Reviewer, each ticket tracks `retry_count`. If `retry_count >= max_review_retries` (default: 3), the agent emits an `ESCALATE` action.
* **Subprocess Timeouts**: QA test runs enforce a strict execution timeout (default: 30 seconds) to prevent hanging test suites or infinite loops in generated code.
* **Safe Encoding on Windows**: The CLI dynamically reconfigures console outputs to UTF-8 and uses ASCII-safe fallback badges to prevent `charmap` / `cp1252` encoding crashes.
