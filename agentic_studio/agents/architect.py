"""Solutions Architect Agent: Translates PRD into system design, API contracts, and schema."""

import json
import logging
from typing import Optional
from agentic_studio.agents.base import BaseAgent
from agentic_studio.protocol.models import (
    A2AMessage,
    ActionType,
    ArchitectureSpecPayload,
)

logger = logging.getLogger("SolutionsArchitect")


class SolutionsArchitectAgent(BaseAgent):
    """Designs the technical architecture, data models, and API specifications."""

    def __init__(self, bus, llm, blackboard, workspace):
        super().__init__(
            name="SolutionsArchitect",
            role="Principal Solutions Architect",
            bus=bus,
            llm=llm,
            blackboard=blackboard,
            workspace=workspace,
        )

    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        if message.action == ActionType.PRD_GENERATED:
            return self.design_architecture(message.payload)
        return None

    def design_architecture(self, prd_data: dict) -> A2AMessage:
        """Create architecture blueprint from PRD."""
        system_prompt = (
            "You are a Principal Software Architect. Given a Product Requirements Document (PRD), "
            "design the technical architecture, choose the tech stack, define the project file tree, "
            "API endpoints/contracts, and SQLite/SQL database schema."
        )

        user_prompt = f"PRD Document:\n{json.dumps(prd_data, indent=2)}"

        arch_data = self.llm.generate_json(
            system_instruction=system_prompt,
            user_prompt=user_prompt,
            response_schema=ArchitectureSpecPayload,
        )

        logger.info(f"[{self.name}] Architecture designed with {len(arch_data.get('file_tree', []))} files.")

        # Save architecture design document into workspace docs/
        self.workspace.write_file(
            "docs/architecture.json", json.dumps(arch_data, indent=2)
        )

        # Dispatch A2A message to ProjectManager
        return self.send_a2a(
            recipient="ProjectManager",
            action=ActionType.ARCH_SPEC_GENERATED,
            payload=arch_data,
        )
