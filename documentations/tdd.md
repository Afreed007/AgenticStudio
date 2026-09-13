# Agentic Studio - Technical Design & TDD Specification

**Document Version:** 1.0.0  
**Test Framework:** Pytest 9.1+  
**Target Runtime:** Python 3.13.15  

---

## 1. Technical Design Overview

Agentic Studio is engineered using a modular, decoupled architecture driven by **Test-Driven Development (TDD)** principles. Every subsystem—protocol message validation, state management, sandboxed execution, and agent decision logic—is backed by isolated unit and integration tests.

```
                           [ Test Harness (pytest) ]
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
[ test_protocol.py ]        [ test_blackboard.py ]       [ test_orchestrator.py ]
 - Pydantic validation       - TaskBoard state machine    - Full 11-step SDLC cycle
 - Bus routing & history     - Dependency DAG resolver    - QA bug & fix loop
 - Dead-letter fallback      - Sandbox path security      - Target code execution
```

---

## 2. Core Data Models & Schemas

### 2.1 A2A Protocol Envelope (`agentic_studio.protocol.models.A2AMessage`)
```python
class A2AMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    timestamp: float = Field(default_factory=time.time)
    sender: str
    recipient: str
    action: ActionType
    ticket_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
```

### 2.2 TaskBoard State Models (`agentic_studio.blackboard.state`)
```python
class Ticket(BaseModel):
    ticket_id: str
    title: str
    description: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    target_files: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.TODO
    assigned_to: Optional[str] = None
    retry_count: int = 0
    qa_approved: bool = False
    review_approved: bool = False
```

### 2.3 Sandbox Path Validation (`agentic_studio.blackboard.workspace.WorkspaceManager`)
```python
def _resolve_safe(self, rel_path: str) -> Path:
    clean_rel = os.path.normpath(rel_path.strip().lstrip("/\\"))
    target = (self.root_dir / clean_rel).resolve()
    if not str(target).startswith(str(self.root_dir)):
        raise ValueError(f"Security violation: Attempted path traversal: '{rel_path}'")
    return target
```

---

## 3. Testing Strategy & Test Suites

The test suite is located in `tests/` and structured into three primary tiers:

### Tier 1: Protocol & Bus Validation (`tests/test_protocol.py`)
* **`test_a2a_message_creation`**: Verifies envelope instantiation, default UUID message IDs, UNIX timestamp generation, and summary formatting.
* **`test_a2a_bus_dispatch_and_history`**: Registers a mock recipient on `A2ABus`, dispatches a message, verifies synchronous callback execution, and validates that message history preserves chronological ordering.
* **`test_a2a_bus_dead_letter`**: Sends a message to a non-existent agent name, confirming it does not throw an unhandled exception and is recorded in the audit history.

### Tier 2: Blackboard State & Sandbox Security (`tests/test_blackboard.py`)
* **`test_taskboard_dependency_ordering`**:
  * Configures Ticket `TICK-002` to depend on `TICK-001`.
  * Verifies `get_next_actionable_ticket()` returns `TICK-001` first.
  * Verifies `TICK-002` cannot be scheduled while `TICK-001` is `IN_PROGRESS`.
  * Verifies `TICK-002` is immediately scheduled once `TICK-001` is marked `DONE`.
* **`test_workspace_safe_paths`**:
  * Tests clean file creation, existence checks, and content reading.
  * Tests malicious path traversal attempts: `../../../evil.txt` and `../../outside.txt`, asserting that a `ValueError` with `"Security violation"` is raised.

### Tier 3: End-to-End Orchestrator Integration (`tests/test_orchestrator.py`)
* **`test_full_agency_workflow`**:
  * Initializes an isolated target workspace in `tmp_path`.
  * Runs the complete SDLC agency from initial client prompt to delivery.
  * Asserts final status is `SUCCESS`.
  * Verifies the A2A conversation trace contains:
    `SCOPING_REQUEST` $\rightarrow$ `PRD_GENERATED` $\rightarrow$ `ARCH_SPEC_GENERATED` $\rightarrow$ `TASK_ASSIGNMENT` $\rightarrow$ `TASK_SUBMISSION` $\rightarrow$ `BUG_REPORT` $\rightarrow$ `TASK_SUBMISSION` $\rightarrow$ `TASK_APPROVED` $\rightarrow$ `DELIVERY_COMPLETE`.
  * Verifies that the QA Engineer catches an edge-case bug on attempt #1, Developer fixes it on attempt #2, and subsequent `pytest` run returns 100% pass rate.

---

## 4. How to Execute Tests

```powershell
# Run all tests with standard output
.venv\Scripts\pytest

# Run tests with verbose output and short tracebacks
.venv\Scripts\pytest -v --tb=short

# Run a specific test suite
.venv\Scripts\pytest tests/test_orchestrator.py -v
```

---

## 5. Guidelines for Adding New Features (TDD Workflow)

When extending the platform (e.g. adding new agent personas, new A2A message types, or external tool integrations):

1. **Write the Test First**: Add a test in `tests/` asserting the expected behavior, payload structure, or agent response.
2. **Implement Minimal Code**: Update the models, bus, or agent implementation to satisfy the test.
3. **Verify Pass**: Ensure `pytest` passes with 0 failures.
4. **Update Documentation**: Update `documentations/README.md`, `documentations/architecture.md`, `documentations/prd.md`, and this `documentations/tdd.md` file in accordance with the project rules.
