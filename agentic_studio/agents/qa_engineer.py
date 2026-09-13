"""QA Engineer Agent: Generates tests, executes pytest in sandbox, and gates quality."""

import logging
from typing import Optional
from agentic_studio.config import config
from agentic_studio.agents.base import BaseAgent
from agentic_studio.tools.execution_tools import SandboxedExecutionTools
from agentic_studio.protocol.models import (
    A2AMessage,
    ActionType,
    BugReportPayload,
)

logger = logging.getLogger("QAEngineer")


class QAEngineerAgent(BaseAgent):
    """Quality Assurance engineer responsible for automated testing and bug verification."""

    def __init__(self, bus, llm, blackboard, workspace):
        super().__init__(
            name="QAEngineer",
            role="Lead QA Automation Engineer",
            bus=bus,
            llm=llm,
            blackboard=blackboard,
            workspace=workspace,
        )
        self.exec_tools = SandboxedExecutionTools(
            workspace, timeout_seconds=config.test_timeout_seconds
        )
        self._tests_written = False

    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        if message.action == ActionType.TASK_SUBMISSION:
            return self.verify_submission(message)
        return None

    def verify_submission(self, message: A2AMessage) -> A2AMessage:
        ticket_id = message.ticket_id
        ticket = self.blackboard.get_ticket(ticket_id)
        if not ticket:
            logger.error(f"Ticket {ticket_id} not found on blackboard.")
            return None

        # Ensure QA test suite is written to workspace
        if not self._tests_written:
            self._write_test_suite()

        logger.info(f"[{self.name}] Running pytest for ticket {ticket_id}...")
        test_result = self.exec_tools.run_pytest()

        if not test_result["passed"]:
            ticket.retry_count += 1
            logger.warning(
                f"[{self.name}] ❌ Tests FAILED for {ticket_id} (Attempt {ticket.retry_count}/{config.max_review_retries})"
            )

            # Circuit breaker: escalate if retry limit reached
            if ticket.retry_count >= config.max_review_retries:
                logger.critical(
                    f"[{self.name}] Circuit Breaker Triggered: Ticket {ticket_id} reached max retries."
                )
                return self.send_a2a(
                    recipient="ProjectManager",
                    action=ActionType.ESCALATE,
                    ticket_id=ticket_id,
                    payload={
                        "ticket_id": ticket_id,
                        "reason": f"QA test suite failed after {ticket.retry_count} iterations.",
                        "retry_count": ticket.retry_count,
                        "suggested_action": "Human Lead Review",
                    },
                )

            # Send bug report back to Developer
            return self.send_a2a(
                recipient="DeveloperAgent",
                action=ActionType.BUG_REPORT,
                ticket_id=ticket_id,
                payload={
                    "ticket_id": ticket_id,
                    "failure_reason": "Unit tests failed with assertion or syntax errors",
                    "test_command": test_result["command"],
                    "stdout": test_result["stdout"],
                    "stderr": test_result["stderr"],
                    "retry_count": ticket.retry_count,
                },
            )

        logger.info(f"[{self.name}] ✅ QA Tests PASSED for {ticket_id}! Forwarding to Code Reviewer.")
        ticket.qa_approved = True

        # Forward to CodeReviewer for security and style sign-off
        return self.send_a2a(
            recipient="CodeReviewer",
            action=ActionType.TASK_SUBMISSION,
            ticket_id=ticket_id,
            payload={"ticket_id": ticket_id, "qa_passed": True},
        )

    def _write_test_suite(self):
        """Write automated test suite into tests/."""
        if self.llm.is_live:
            # Generate tests dynamically
            test_code = self.llm.generate_text(
                system_instruction="You are a QA Engineer writing pytest tests. Return code only.",
                user_prompt="Write comprehensive pytest test suite for the url_shortener service.",
            )
        else:
            test_code = self.llm.mock_provider.generate_qa_tests("URL Shortener")

        self.workspace.write_file("tests/__init__.py", "")
        self.workspace.write_file("tests/test_shortener.py", test_code)
        self._tests_written = True
        logger.info(f"[{self.name}] Generated and saved test suite in 'tests/test_shortener.py'.")
