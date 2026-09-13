"""Interactive Rich Terminal CLI for running Agentic Studio multi-agent runs."""

import argparse
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from agentic_studio.config import StudioConfig
from agentic_studio.orchestrator import StudioOrchestrator
from agentic_studio.protocol.models import A2AMessage, ActionType

console = Console(safe_box=True)

# Color badges for each specialized agent persona
AGENT_COLORS = {
    "ClientIntake": "bright_white",
    "BusinessAnalyst": "cyan",
    "SolutionsArchitect": "blue",
    "ProjectManager": "yellow",
    "DeveloperAgent": "green",
    "QAEngineer": "magenta",
    "CodeReviewer": "red",
    "DevOpsEngineer": "bright_green",
}

# Cross-platform safe badge tags
ACTION_BADGES = {
    ActionType.SCOPING_REQUEST: "[REQ]",
    ActionType.PRD_GENERATED: "[PRD]",
    ActionType.ARCH_SPEC_GENERATED: "[ARCH]",
    ActionType.TASK_ASSIGNMENT: "[ASSIGN]",
    ActionType.TASK_SUBMISSION: "[SUBMIT]",
    ActionType.BUG_REPORT: "[BUG]",
    ActionType.CODE_REVIEW_REJECTED: "[REJECT]",
    ActionType.CODE_REVIEW_APPROVED: "[SECURITY_OK]",
    ActionType.TASK_APPROVED: "[PASS]",
    ActionType.DELIVERY_COMPLETE: "[DELIVERY]",
    ActionType.ESCALATE: "[ALERT]",
}


def render_a2a_message(msg: A2AMessage) -> None:
    """Format and stream an A2A message to the terminal."""
    sender_color = AGENT_COLORS.get(msg.sender, "white")
    recipient_color = AGENT_COLORS.get(msg.recipient, "white")
    badge = ACTION_BADGES.get(msg.action, f"[{msg.action.value}]")

    header = Text()
    header.append(f"[{msg.sender}]", style=f"bold {sender_color}")
    header.append(" ---> ", style="dim")
    header.append(f"[{msg.recipient}]", style=f"bold {recipient_color}")
    header.append(f"  {badge} {msg.action.value}", style="bold white")

    if msg.ticket_id:
        header.append(f" ({msg.ticket_id})", style="dim yellow")

    details = []
    if msg.action == ActionType.BUG_REPORT:
        reason = msg.payload.get("failure_reason", "Failure detected")
        retry = msg.payload.get("retry_count", 1)
        details.append(f"[bold red]Issue:[/] {reason} (Attempt #{retry})")
    elif msg.action == ActionType.TASK_ASSIGNMENT:
        title = msg.payload.get("title", "")
        if title:
            details.append(f"[cyan]Task:[/] {title}")
    elif msg.action == ActionType.DELIVERY_COMPLETE:
        status = msg.payload.get("verification_status", "Complete")
        details.append(f"[bold green]Status:[/] {status}")

    content = "\n".join(details) if details else ""
    console.print(Panel(content, title=header, title_align="left", border_style="dim", box=box.ROUNDED))


def main():
    parser = argparse.ArgumentParser(description="Agentic Studio Multi-Agent Agency")
    parser.add_argument(
        "--prompt",
        type=str,
        default="Build a production-ready URL Shortener REST service with SQLite and analytics",
        help="Client software requirement prompt",
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default="./target_project",
        help="Target directory to build the software in",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force deterministic offline mock provider",
    )

    args = parser.parse_args()

    console.print(
        Panel.fit(
            "[bold cyan]AGENTIC STUDIO[/bold cyan]\n"
            "[dim]Autonomous Freelance Software Development Agency[/dim]\n"
            "[magenta]Architecture: ADK Agents + A2A Protocol[/magenta]",
            border_style="cyan",
            box=box.DOUBLE,
        )
    )

    console.print(f"[bold]Client Prompt:[/] [italic]{args.prompt}[/italic]")
    console.print(f"[bold]Target Workspace:[/] [yellow]{Path(args.workspace).resolve()}[/yellow]\n")

    cfg = StudioConfig(
        workspace_root=Path(args.workspace),
        use_mock_llm=args.mock,
    )

    orchestrator = StudioOrchestrator(custom_config=cfg, observer=render_a2a_message)

    console.print("[bold green]Starting agency agents collaboration...[/bold green]\n")
    result = orchestrator.run(client_prompt=args.prompt)

    # Print Final Summary Table
    table = Table(title="Studio Execution Summary", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold")

    table.add_row(
        "Final Status",
        f"[green]{result['status']}[/green]"
        if result['status'] == "SUCCESS"
        else f"[red]{result['status']}[/red]",
    )
    table.add_row("Total A2A Messages Exchanged", str(result["total_messages"]))
    table.add_row("Target Files Generated", str(len(result["files_generated"])))

    console.print("\n", table)

    console.print("\n[bold]Generated Project Files:[/bold]")
    for f in result["files_generated"]:
        console.print(f"  [green]{f}[/green]")

    console.print("\n[bold green]Project Ready for Handover! Run tests inside workspace with 'pytest'.[/bold green]\n")


if __name__ == "__main__":
    main()
