"""End-to-end integration test for the complete multi-agent SDLC agency workflow."""

from pathlib import Path
from agentic_studio.config import StudioConfig
from agentic_studio.orchestrator import StudioOrchestrator
from agentic_studio.protocol.models import ActionType


def test_full_agency_workflow(tmp_path):
    # Configure an isolated workspace and force mock LLM
    custom_cfg = StudioConfig(
        workspace_root=tmp_path / "test_target",
        use_mock_llm=True,
        max_review_retries=3,
        test_timeout_seconds=20,
    )

    orchestrator = StudioOrchestrator(custom_config=custom_cfg)

    # Run complete agency pipeline
    result = orchestrator.run(
        client_prompt="Build a URL shortener REST service with SQLite persistence and analytics",
        clean_workspace=True,
    )

    # 1. Pipeline should complete with SUCCESS
    assert result["status"] == "SUCCESS", f"Expected SUCCESS, got {result['status']}: {result.get('escalation')}"

    # 2. Check message history contains the full A2A conversation lifecycle
    actions = [m.action for m in orchestrator.bus.message_history]
    assert ActionType.SCOPING_REQUEST in actions
    assert ActionType.PRD_GENERATED in actions
    assert ActionType.ARCH_SPEC_GENERATED in actions
    assert ActionType.TASK_ASSIGNMENT in actions
    assert ActionType.TASK_SUBMISSION in actions
    assert ActionType.BUG_REPORT in actions        # QA caught initial bug!
    assert ActionType.TASK_APPROVED in actions     # Dev fixed and QA passed!
    assert ActionType.DELIVERY_COMPLETE in actions # DevOps packaged!

    # 3. Check target files were generated in workspace
    workspace = orchestrator.workspace
    assert workspace.file_exists("url_shortener/service.py")
    assert workspace.file_exists("tests/test_shortener.py")
    assert workspace.file_exists("Dockerfile")
    assert workspace.file_exists("README.md")
    assert workspace.file_exists("docs/architecture.json")

    # 4. Verify that running pytest inside the generated workspace passes 100%
    test_result = orchestrator.qa.exec_tools.run_pytest()
    assert test_result["passed"] is True, f"Pytest failed in generated workspace: {test_result['stdout']}"
