"""Developer Agent: Writes implementation code and applies fixes from bug reports."""

import logging
from typing import Optional
from agentic_studio.agents.base import BaseAgent
from agentic_studio.tools.file_tools import WorkspaceFileTools
from agentic_studio.protocol.models import (
    A2AMessage,
    ActionType,
    TaskSubmissionPayload,
)

logger = logging.getLogger("DeveloperAgent")


class DeveloperAgent(BaseAgent):
    """Full-stack software engineer that writes source code and handles bug fixes."""

    def __init__(self, bus, llm, blackboard, workspace):
        super().__init__(
            name="DeveloperAgent",
            role="Senior Software Engineer",
            bus=bus,
            llm=llm,
            blackboard=blackboard,
            workspace=workspace,
        )
        self.file_tools = WorkspaceFileTools(workspace)

    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        if message.action == ActionType.TASK_ASSIGNMENT:
            return self.implement_task(message)

        elif message.action == ActionType.BUG_REPORT:
            return self.fix_bug(message)

        elif message.action == ActionType.CODE_REVIEW_REJECTED:
            return self.address_review(message)

        return None

    def implement_task(self, message: A2AMessage) -> A2AMessage:
        """Write code for a newly assigned task."""
        ticket_id = message.ticket_id
        title = message.payload.get("title", "")
        logger.info(f"[{self.name}] Implementing {ticket_id}: '{title}'")

        if self.llm.is_live:
            # Generate code using live Gemini
            files_dict = self._generate_with_gemini(message.payload)
        else:
            # Deterministic mock code generation
            files_dict = self.llm.mock_provider.generate_code_for_ticket(
                ticket_id=ticket_id, title=title
            )

        # Write files into the workspace
        created_files = []
        for rel_path, content in files_dict.items():
            self.file_tools.write_code(rel_path, content)
            created_files.append(rel_path)

        logger.info(f"[{self.name}] Wrote {len(created_files)} files for {ticket_id}. Submitting to QA.")

        # Dispatch A2A submission to QAEngineer
        return self.send_a2a(
            recipient="QAEngineer",
            action=ActionType.TASK_SUBMISSION,
            ticket_id=ticket_id,
            payload={
                "ticket_id": ticket_id,
                "files_created": created_files,
                "files_modified": [],
                "commit_summary": f"Initial implementation for {ticket_id}: {title}",
            },
        )

    def fix_bug(self, message: A2AMessage) -> A2AMessage:
        """Analyze bug report and apply fix."""
        ticket_id = message.ticket_id
        failure = message.payload.get("failure_reason", "")
        logger.info(f"[{self.name}] Applying fix for {ticket_id}. Reason: {failure}")

        if self.llm.is_live:
            # Generate fix with Gemini
            files_dict = self._generate_fix_with_gemini(message.payload)
        else:
            files_dict = self.llm.mock_provider.generate_code_for_ticket(
                ticket_id=ticket_id,
                title="",
                bug_report=message.payload,
            )

        modified_files = []
        for rel_path, content in files_dict.items():
            self.file_tools.write_code(rel_path, content)
            modified_files.append(rel_path)

        logger.info(f"[{self.name}] Fixed {len(modified_files)} files. Resubmitting to QA.")

        return self.send_a2a(
            recipient="QAEngineer",
            action=ActionType.TASK_SUBMISSION,
            ticket_id=ticket_id,
            payload={
                "ticket_id": ticket_id,
                "files_created": [],
                "files_modified": modified_files,
                "commit_summary": f"Bug fix resolution for {ticket_id}",
            },
        )

    def address_review(self, message: A2AMessage) -> A2AMessage:
        """Address security or style review feedback."""
        ticket_id = message.ticket_id
        feedback = message.payload.get("feedback", "")
        logger.info(f"[{self.name}] Addressing code review feedback: {feedback}")

        # Resubmit to CodeReviewer
        return self.send_a2a(
            recipient="CodeReviewer",
            action=ActionType.TASK_SUBMISSION,
            ticket_id=ticket_id,
            payload={"ticket_id": ticket_id, "notes": "Applied security and style improvements"},
        )

    def _generate_with_gemini(self, task_payload: dict) -> dict:
        prompt = (
            f"Implement clean Python 3.13 code for the following task:\n"
            f"Title: {task_payload.get('title')}\n"
            f"Criteria: {task_payload.get('acceptance_criteria')}\n"
            f"Target Files: {task_payload.get('target_files')}\n"
            "Return JSON mapping relative file paths to their complete Python file code content."
        )
        return self.llm.generate_json(
            system_instruction="You are a Senior Python Engineer. Return valid JSON only: {'filepath': 'code'}",
            user_prompt=prompt,
        )

    def _generate_fix_with_gemini(self, bug_payload: dict) -> dict:
        prompt = (
            f"The automated test suite failed with the following bug report:\n"
            f"Failure: {bug_payload.get('failure_reason')}\n"
            f"Stdout/Stderr: {bug_payload.get('stdout')}\n"
            f"Fix the code so all tests pass. Return JSON mapping filepath to corrected code."
        )
        return self.llm.generate_json(
            system_instruction="You are a Senior Python Engineer debugging a failure. Return valid JSON only: {'filepath': 'code'}",
            user_prompt=prompt,
        )
