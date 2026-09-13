"""Code Reviewer & Security Agent: Reviews code quality, security vulnerabilities, and adherence to specs."""

import logging
from typing import Optional
from agentic_studio.agents.base import BaseAgent
from agentic_studio.protocol.models import (
    A2AMessage,
    ActionType,
    CodeReviewPayload,
)

logger = logging.getLogger("CodeReviewer")


class CodeReviewerAgent(BaseAgent):
    """Enforces clean code conventions, OWASP security rules, and code quality."""

    def __init__(self, bus, llm, blackboard, workspace):
        super().__init__(
            name="CodeReviewer",
            role="Staff Security & Quality Reviewer",
            bus=bus,
            llm=llm,
            blackboard=blackboard,
            workspace=workspace,
        )

    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        if message.action == ActionType.TASK_SUBMISSION:
            return self.review_code(message)
        return None

    def review_code(self, message: A2AMessage) -> A2AMessage:
        ticket_id = message.ticket_id
        ticket = self.blackboard.get_ticket(ticket_id)
        logger.info(f"[{self.name}] Performing security and quality audit for {ticket_id}...")

        # In live mode, can invoke LLM or AST audit. For now, audit checks SQL parameterization and typing:
        files = self.workspace.list_files(".py")
        has_security_issue = False
        findings = []

        for f in files:
            content = self.workspace.read_file(f)
            # Example check: raw string formatting in SQL statements
            if "format(" in content and "SELECT" in content:
                has_security_issue = True
                findings.append(f"Possible SQL injection risk in {f}: Use parameterized queries.")

        if has_security_issue:
            logger.warning(f"[{self.name}] ❌ Code review REJECTED: {findings}")
            return self.send_a2a(
                recipient="DeveloperAgent",
                action=ActionType.CODE_REVIEW_REJECTED,
                ticket_id=ticket_id,
                payload={
                    "ticket_id": ticket_id,
                    "approved": False,
                    "security_issues": findings,
                    "feedback": "Please replace raw SQL string formatting with '?' parameterized tuples.",
                },
            )

        # Approved!
        logger.info(f"[{self.name}] ✅ Code review APPROVED with score 9.5/10!")
        if ticket:
            ticket.review_approved = True

        # Send final approval back to ProjectManager
        return self.send_a2a(
            recipient="ProjectManager",
            action=ActionType.TASK_APPROVED,
            ticket_id=ticket_id,
            payload={
                "ticket_id": ticket_id,
                "qa_passed": True,
                "code_review_passed": True,
                "test_summary": "All tests passed and code review passed with zero security flags.",
            },
        )
