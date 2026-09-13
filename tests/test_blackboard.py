"""Tests for TaskBoard state machine and sandboxed WorkspaceManager."""

import pytest
from pathlib import Path
from agentic_studio.blackboard.state import TaskBoard, Ticket
from agentic_studio.blackboard.workspace import WorkspaceManager
from agentic_studio.protocol.models import TaskStatus


def test_taskboard_dependency_ordering():
    board = TaskBoard()
    t1 = Ticket(
        ticket_id="TICK-001",
        title="Setup DB",
        description="Init DB schema",
        dependencies=[],
    )
    t2 = Ticket(
        ticket_id="TICK-002",
        title="Implement API",
        description="CRUD endpoints",
        dependencies=["TICK-001"],
    )
    board.add_ticket(t1)
    board.add_ticket(t2)

    # First actionable must be TICK-001
    next_task = board.get_next_actionable_ticket()
    assert next_task is not None
    assert next_task.ticket_id == "TICK-001"

    # Mark TICK-001 in progress
    board.mark_in_progress("TICK-001", "DeveloperAgent")
    assert t1.status == TaskStatus.IN_PROGRESS

    # Now no actionable tickets exist (t1 is in progress, t2 is blocked)
    assert board.get_next_actionable_ticket() is None

    # Mark TICK-001 done
    board.mark_done("TICK-001")
    assert t1.status == TaskStatus.DONE

    # Now TICK-002 should become actionable!
    next_task = board.get_next_actionable_ticket()
    assert next_task is not None
    assert next_task.ticket_id == "TICK-002"


def test_workspace_safe_paths(tmp_path):
    ws = WorkspaceManager(tmp_path)

    # Valid write and read
    ws.write_file("sub/dir/test.txt", "hello world")
    assert ws.file_exists("sub/dir/test.txt")
    assert ws.read_file("sub/dir/test.txt") == "hello world"

    # Directory traversal attack prevention
    with pytest.raises(ValueError, match="Security violation"):
        ws.write_file("../../../evil.txt", "pwned")

    with pytest.raises(ValueError, match="Security violation"):
        ws.read_file("../../outside.txt")
