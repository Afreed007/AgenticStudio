"""Project Manager Agent: Breaks specs into tickets, manages sprint, and tracks velocity."""

import logging
from typing import Optional
from agentic_studio.agents.base import BaseAgent
from agentic_studio.blackboard.state import Ticket
from agentic_studio.protocol.models import (
    A2AMessage,
    ActionType,
    TaskStatus,
)

logger = logging.getLogger("ProjectManager")


class ProjectManagerAgent(BaseAgent):
    """Scrum Master and Sprint Coordinator managing tasks, assignments, and milestones."""

    def __init__(self, bus, llm, blackboard, workspace):
        super().__init__(
            name="ProjectManager",
            role="Lead Technical Project Manager",
            bus=bus,
            llm=llm,
            blackboard=blackboard,
            workspace=workspace,
        )

    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        if message.action == ActionType.ARCH_SPEC_GENERATED:
            return self.plan_sprint(message.payload)

        elif message.action == ActionType.TASK_APPROVED:
            return self.handle_task_completion(message)

        elif message.action == ActionType.ESCALATE:
            logger.error(
                f"[{self.name}] ESCALATION received for ticket '{message.ticket_id}': "
                f"{message.payload.get('reason')}"
            )
            self.blackboard.mark_blocked(message.ticket_id)
            return None

        return None

    def plan_sprint(self, arch_spec: dict) -> Optional[A2AMessage]:
        """Convert architecture spec into tickets on the TaskBoard."""
        project_name = arch_spec.get("project_name", "application")

        # Ticket 1: Core Service & Data Layer
        t1 = Ticket(
            ticket_id="TICK-001",
            title=f"Core Storage & Logic for {project_name}",
            description="Implement SQLite database models, initialization, and core business functions.",
            acceptance_criteria=[
                "Database tables initialize automatically if not present",
                "Core CRUD/shortening and resolution logic implemented",
                "Proper parameterization to prevent SQL injection",
                "Clean exception handling for edge cases"
            ],
            target_files=["url_shortener/service.py"],
            dependencies=[],
        )
        self.blackboard.add_ticket(t1)

        logger.info(f"[{self.name}] Sprint planned with {len(self.blackboard.tickets)} tickets.")

        # Dispatch the first actionable ticket to Developer
        return self.dispatch_next_ticket()

    def dispatch_next_ticket(self) -> Optional[A2AMessage]:
        """Find the next actionable ticket and send TASK_ASSIGNMENT to Developer."""
        ticket = self.blackboard.get_next_actionable_ticket()
        if not ticket:
            if self.blackboard.is_complete():
                logger.info(f"[{self.name}] All sprint tickets are DONE! Triggering DevOps delivery.")
                return self.send_a2a(
                    recipient="DevOpsEngineer",
                    action=ActionType.TASK_ASSIGNMENT,
                    payload={"sprint_complete": True},
                )
            return None

        self.blackboard.mark_in_progress(ticket.ticket_id, "DeveloperAgent")
        logger.info(f"[{self.name}] Assigning {ticket.ticket_id}: '{ticket.title}' to Developer.")

        return self.send_a2a(
            recipient="DeveloperAgent",
            action=ActionType.TASK_ASSIGNMENT,
            ticket_id=ticket.ticket_id,
            payload={
                "ticket_id": ticket.ticket_id,
                "title": ticket.title,
                "description": ticket.description,
                "acceptance_criteria": ticket.acceptance_criteria,
                "target_files": ticket.target_files,
            },
        )

    def handle_task_completion(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Mark ticket as DONE and assign the next one."""
        ticket_id = message.ticket_id
        if ticket_id:
            self.blackboard.mark_done(ticket_id)
            logger.info(f"[{self.name}] Ticket {ticket_id} verified and marked as DONE! ✅")

        return self.dispatch_next_ticket()
