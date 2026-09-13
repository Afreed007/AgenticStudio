"""Business Analyst Agent: Gathers requirements and defines the Product Requirements Document (PRD)."""

import logging
from typing import Optional
from agentic_studio.agents.base import BaseAgent
from agentic_studio.protocol.models import (
    A2AMessage,
    ActionType,
    PRDPayload,
)

logger = logging.getLogger("BusinessAnalyst")


class BusinessAnalystAgent(BaseAgent):
    """Translates vague client ideas into formal user stories and acceptance criteria."""

    def __init__(self, bus, llm, blackboard, workspace):
        super().__init__(
            name="BusinessAnalyst",
            role="Lead Product & Business Analyst",
            bus=bus,
            llm=llm,
            blackboard=blackboard,
            workspace=workspace,
        )

    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        if message.action == ActionType.SCOPING_REQUEST:
            client_prompt = message.payload.get("client_prompt", "")
            return self.scope_requirements(client_prompt)
        return None

    def scope_requirements(self, client_prompt: str) -> A2AMessage:
        """Scope client prompt into a structured PRD."""
        system_prompt = (
            "You are an expert Lead Business Analyst in a software agency. "
            "Analyze the client's request and output a structured Product Requirements Document (PRD) "
            "including project_name, summary, target_audience, user_stories (with acceptance criteria), "
            "and tech_stack_recommendation."
        )

        prd_data = self.llm.generate_json(
            system_instruction=system_prompt,
            user_prompt=f"Client Request: {client_prompt}",
            response_schema=PRDPayload,
        )

        logger.info(f"[{self.name}] PRD generated: '{prd_data.get('project_name', 'project')}'")

        # Send A2A message to SolutionsArchitect
        return self.send_a2a(
            recipient="SolutionsArchitect",
            action=ActionType.PRD_GENERATED,
            payload=prd_data,
        )
