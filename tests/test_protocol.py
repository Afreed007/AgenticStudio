"""Tests for A2A protocol envelopes, validation, and the message bus."""

import pytest
from agentic_studio.protocol.models import (
    ActionType,
    A2AMessage,
    TaskAssignmentPayload,
    BugReportPayload,
)
from agentic_studio.protocol.bus import A2ABus


def test_a2a_message_creation():
    msg = A2AMessage(
        sender="ProjectManager",
        recipient="DeveloperAgent",
        action=ActionType.TASK_ASSIGNMENT,
        ticket_id="TICK-101",
        payload={
            "ticket_id": "TICK-101",
            "title": "Build Auth",
            "description": "Add JWT auth",
            "acceptance_criteria": ["200 on login", "401 on bad creds"],
            "target_files": ["auth.py"],
        }
    )
    assert msg.sender == "ProjectManager"
    assert msg.recipient == "DeveloperAgent"
    assert msg.action == ActionType.TASK_ASSIGNMENT
    assert msg.ticket_id == "TICK-101"
    assert "TICK-101" in msg.summary()


def test_a2a_bus_dispatch_and_history():
    bus = A2ABus()

    received_messages = []

    def mock_developer_handler(msg: A2AMessage):
        received_messages.append(msg)
        return A2AMessage(
            sender="DeveloperAgent",
            recipient="QAEngineer",
            action=ActionType.TASK_SUBMISSION,
            ticket_id=msg.ticket_id,
            payload={"files_created": ["auth.py"]}
        )

    bus.register_agent("DeveloperAgent", mock_developer_handler)

    incoming = A2AMessage(
        sender="ProjectManager",
        recipient="DeveloperAgent",
        action=ActionType.TASK_ASSIGNMENT,
        ticket_id="TICK-101",
        payload={}
    )

    response = bus.dispatch(incoming)

    assert len(received_messages) == 1
    assert response is not None
    assert response.sender == "DeveloperAgent"
    assert response.action == ActionType.TASK_SUBMISSION
    assert len(bus.message_history) == 2


def test_a2a_bus_dead_letter():
    bus = A2ABus()
    msg = A2AMessage(
        sender="AgentA",
        recipient="NonExistentAgent",
        action=ActionType.SCOPING_REQUEST,
        payload={}
    )
    response = bus.dispatch(msg)
    assert response is None
    # Message should still be in history for audit
    assert len(bus.message_history) == 1
