"""Studio Orchestrator: Wires agents, initializes the A2A bus, and coordinates the SDLC."""

import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional
from agentic_studio.config import config, StudioConfig
from agentic_studio.protocol.models import A2AMessage, ActionType
from agentic_studio.protocol.bus import A2ABus
from agentic_studio.blackboard.state import TaskBoard
from agentic_studio.blackboard.workspace import WorkspaceManager
from agentic_studio.llm.client import LLMClient
from agentic_studio.agents import (
    BusinessAnalystAgent,
    SolutionsArchitectAgent,
    ProjectManagerAgent,
    DeveloperAgent,
    QAEngineerAgent,
    CodeReviewerAgent,
    DevOpsAgent,
)

logger = logging.getLogger("StudioOrchestrator")


class StudioOrchestrator:
    """Coordinates the entire multi-agent freelance software agency."""

    def __init__(
        self,
        custom_config: Optional[StudioConfig] = None,
        observer: Optional[Callable[[A2AMessage], None]] = None,
    ):
        self.cfg = custom_config or config
        self.bus = A2ABus()
        if observer:
            self.bus.add_observer(observer)

        self.workspace = WorkspaceManager(self.cfg.workspace_root)
        self.blackboard = TaskBoard()
        self.llm = LLMClient(api_key=self.cfg.gemini_api_key, model=self.cfg.default_model)

        # Initialize and register the agency's roster of specialized agents
        self.ba = BusinessAnalystAgent(self.bus, self.llm, self.blackboard, self.workspace)
        self.architect = SolutionsArchitectAgent(self.bus, self.llm, self.blackboard, self.workspace)
        self.pm = ProjectManagerAgent(self.bus, self.llm, self.blackboard, self.workspace)
        self.dev = DeveloperAgent(self.bus, self.llm, self.blackboard, self.workspace)
        self.qa = QAEngineerAgent(self.bus, self.llm, self.blackboard, self.workspace)
        self.reviewer = CodeReviewerAgent(self.bus, self.llm, self.blackboard, self.workspace)
        self.devops = DevOpsAgent(self.bus, self.llm, self.blackboard, self.workspace)
        # Register ClientIntake mailbox for receiving final delivery handover
        self.bus.register_agent("ClientIntake", lambda msg: None)

    def run(self, client_prompt: str, clean_workspace: bool = True) -> Dict:
        """Run the full software development lifecycle from client prompt to delivery."""
        if clean_workspace:
            self.workspace.clean()

        logger.info(f"=== INITIATING CLIENT PROJECT: '{client_prompt}' ===")

        # Send initial scoping message to Business Analyst
        initial_msg = A2AMessage(
            sender="ClientIntake",
            recipient="BusinessAnalyst",
            action=ActionType.SCOPING_REQUEST,
            payload={"client_prompt": client_prompt},
        )

        self.bus.dispatch(initial_msg)

        # Collect summary metrics
        delivery_msg = next(
            (m for m in self.bus.message_history if m.action == ActionType.DELIVERY_COMPLETE),
            None
        )
        escalation_msg = next(
            (m for m in self.bus.message_history if m.action == ActionType.ESCALATE),
            None
        )

        return {
            "status": "SUCCESS" if delivery_msg else ("ESCALATED" if escalation_msg else "PARTIAL"),
            "total_messages": len(self.bus.message_history),
            "files_generated": self.workspace.list_files(),
            "tickets_stats": self.blackboard.get_stats(),
            "delivery": delivery_msg.payload if delivery_msg else None,
            "escalation": escalation_msg.payload if escalation_msg else None,
        }
