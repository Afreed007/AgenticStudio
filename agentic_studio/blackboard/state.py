"""State models and TaskBoard blackboard for tracking project execution."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from agentic_studio.protocol.models import TaskStatus


class Ticket(BaseModel):
    """An individual work ticket assigned to engineering agents."""

    ticket_id: str
    title: str
    description: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    target_files: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.TODO
    assigned_to: Optional[str] = None
    retry_count: int = 0
    qa_approved: bool = False
    review_approved: bool = False


class TaskBoard:
    """The central shared task board managing tickets and dependencies."""

    def __init__(self):
        self.tickets: Dict[str, Ticket] = {}

    def add_ticket(self, ticket: Ticket) -> None:
        self.tickets[ticket.ticket_id] = ticket

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return self.tickets.get(ticket_id)

    def get_next_actionable_ticket(self) -> Optional[Ticket]:
        """Find the next TODO ticket whose dependencies are all DONE."""
        for ticket in self.tickets.values():
            if ticket.status == TaskStatus.TODO:
                # Check all dependencies
                all_deps_done = True
                for dep_id in ticket.dependencies:
                    dep_ticket = self.tickets.get(dep_id)
                    if not dep_ticket or dep_ticket.status != TaskStatus.DONE:
                        all_deps_done = False
                        break
                if all_deps_done:
                    return ticket
        return None

    def mark_in_progress(self, ticket_id: str, agent_name: str) -> None:
        if ticket_id in self.tickets:
            t = self.tickets[ticket_id]
            t.status = TaskStatus.IN_PROGRESS
            t.assigned_to = agent_name

    def mark_in_review(self, ticket_id: str) -> None:
        if ticket_id in self.tickets:
            self.tickets[ticket_id].status = TaskStatus.IN_REVIEW

    def mark_done(self, ticket_id: str) -> None:
        if ticket_id in self.tickets:
            t = self.tickets[ticket_id]
            t.status = TaskStatus.DONE
            t.qa_approved = True
            t.review_approved = True

    def mark_blocked(self, ticket_id: str) -> None:
        if ticket_id in self.tickets:
            self.tickets[ticket_id].status = TaskStatus.BLOCKED

    def is_complete(self) -> bool:
        """Returns True if all tickets on the board are marked DONE."""
        if not self.tickets:
            return False
        return all(t.status == TaskStatus.DONE for t in self.tickets.values())

    def get_stats(self) -> Dict[str, int]:
        """Returns ticket counts by status."""
        stats = {s.value: 0 for s in TaskStatus}
        for t in self.tickets.values():
            stats[t.status.value] += 1
        return stats
