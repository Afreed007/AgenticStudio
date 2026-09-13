# Agentic Studio 🤖🏢

> **Autonomous Freelance Software Development Agency** powered by **Agent Development Kit (ADK)** concepts and an **Agent-to-Agent (A2A)** communication protocol.

Agentic Studio simulates a full-service software boutique where autonomous AI agents collaborate over typed contracts to take a client idea and deliver production-ready, tested, and reviewed code.

---

## 🏛️ Multi-Agent Architecture

```
[Client / Sponsor]
       │ (Scoping Request)
       ▼
[1. Business Analyst] ──(A2A: PRD_GENERATED)──► [2. Solutions Architect]
                                                         │
                                               (A2A: ARCH_SPEC_GENERATED)
                                                         │
                                                         ▼
                                               [3. Project Manager]
                                                         │
                                              (A2A: TASK_ASSIGNMENT)
                                                         │
                                                         ▼
                                               [4. Developer Agent]
                                                         │
                                               (A2A: TASK_SUBMISSION)
                                                         │
                                        ┌────────────────┴────────────────┐
                                        ▼                                 ▼
                             [5. QA Engineer Agent]            [6. Code Reviewer]
                              - Automated Pytest runner         - Security & Style audit
                              - Bugs ──► A2A: BUG_REPORT        - Rejections ──► A2A: REJECTED
                              - Passes ──► A2A: APPROVED        - Passes ──► A2A: APPROVED
                                        └────────────────┬────────────────┘
                                                         │
                                               (A2A: TASK_APPROVED)
                                                         │
                                                         ▼
                                               [7. DevOps Engineer]
                                               - Dockerfile & Packaging
                                               - Handover README
```

---

## 🚀 Key Features

- **Typed A2A Protocol (`agentic_studio/protocol/`)**: Agents communicate using structured Pydantic message envelopes (`A2AMessage`) rather than unconstrained raw chat.
- **Autonomous QA Feedback Loop**: Developer code is immediately run against a pytest suite in an isolated sandbox. If an edge case fails, QA creates a structured `BUG_REPORT` that triggers a developer fix attempt.
- **Circuit Breaker Protection**: Prevents infinite critique loops by escalating to human lead review if retries exceed threshold.
- **Dual Engine (Gemini & Mock Fallback)**: Runs with Google Gemini (`gemini-2.5-flash` / `gemini-2.0-flash`) via `google-genai` SDK or deterministic offline mock for fast automated testing.
- **Rich Terminal UI**: Live color-coded streaming of inter-agent messages and ticket progression.

---

## 📦 Installation & Setup

Ensure Python 3.13+ is installed:

```bash
# Clone or navigate to the repository
cd "C:\Users\Afreed007\Projects\Agentic dev"

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration (Optional for Live Gemini Mode)
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
*(If no API key is provided, the studio automatically runs in offline mock mode).*

---

## 💻 Usage

### 1. Run the Interactive Multi-Agent Studio CLI

```bash
# Run with default prompt
.venv\Scripts\python -m agentic_studio.cli

# Or specify a custom project prompt and target workspace
.venv\Scripts\python -m agentic_studio.cli --prompt "Build a FastAPI URL shortener with rate limiting and SQLite" --workspace "./my_project"
```

### 2. Run Automated Test Suite

```bash
.venv\Scripts\pytest -v
```

---

## 📂 Project Structure

```
agentic-studio/
├── .venv/                      # Python 3.13 virtual environment
├── pyproject.toml              # Packaging & dependencies
├── requirements.txt            # Dependency list
├── README.md                   # This documentation
├── agentic_studio/
│   ├── config.py               # Studio configuration
│   ├── protocol/               # A2A models & message bus
│   │   ├── models.py
│   │   └── bus.py
│   ├── blackboard/             # Shared TaskBoard & Sandboxed Workspace
│   │   ├── state.py
│   │   └── workspace.py
│   ├── tools/                  # ADK Tooling
│   │   ├── file_tools.py
│   │   └── execution_tools.py
│   ├── llm/                    # Gemini API client & Mock provider
│   │   ├── client.py
│   │   └── mock.py
│   ├── agents/                 # Specialized Agent Personas
│   │   ├── base.py
│   │   ├── business_analyst.py
│   │   ├── architect.py
│   │   ├── project_manager.py
│   │   ├── developer.py
│   │   ├── qa_engineer.py
│   │   ├── code_reviewer.py
│   │   └── devops.py
│   ├── orchestrator.py         # End-to-end SDLC pipeline runner
│   └── cli.py                  # Rich interactive terminal interface
└── tests/
    ├── test_protocol.py
    ├── test_blackboard.py
    └── test_orchestrator.py
```
