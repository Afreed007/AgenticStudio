"""Typed models and message envelopes for the Agent-to-Agent (A2A) protocol."""

from enum import Enum
import time
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    # Discovery & Architecture
    SCOPING_REQUEST = "SCOPING_REQUEST"
    PRD_GENERATED = "PRD_GENERATED"
    ARCH_SPEC_GENERATED = "ARCH_SPEC_GENERATED"

    # Sprint Planning & Implementation
    TASK_ASSIGNMENT = "TASK_ASSIGNMENT"
    TASK_SUBMISSION = "TASK_SUBMISSION"

    # QA & Security Code Review
    BUG_REPORT = "BUG_REPORT"
    CODE_REVIEW_REJECTED = "CODE_REVIEW_REJECTED"
    CODE_REVIEW_APPROVED = "CODE_REVIEW_APPROVED"
    TASK_APPROVED = "TASK_APPROVED"

    # DevOps & Lifecycle
    DELIVERY_COMPLETE = "DELIVERY_COMPLETE"
    ESCALATE = "ESCALATE"


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    DONE = "DONE"
    BLOCKED = "BLOCKED"


# --- Specialized Payloads ---

class UserStory(BaseModel):
    id: str
    title: str
    acceptance_criteria: List[str]


class PRDPayload(BaseModel):
    project_name: str
    summary: str
    target_audience: str
    user_stories: List[UserStory]
    tech_stack_recommendation: List[str]


class ArchitectureSpecPayload(BaseModel):
    project_name: str
    tech_stack: Dict[str, str] = Field(default_factory=dict)
    file_tree: List[str] = Field(default_factory=list)
    api_contracts: Dict[str, Any] = Field(default_factory=dict)
    db_schema: str = ""
    notes: str = ""


class TaskAssignmentPayload(BaseModel):
    ticket_id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    target_files: List[str]
    dependencies: List[str] = Field(default_factory=list)


class TaskSubmissionPayload(BaseModel):
    ticket_id: str
    files_created: List[str]
    files_modified: List[str]
    commit_summary: str


class BugReportPayload(BaseModel):
    ticket_id: str
    failure_reason: str
    test_command: str
    stdout: str
    stderr: str
    stack_trace: Optional[str] = None
    retry_count: int = 1


class CodeReviewPayload(BaseModel):
    ticket_id: str
    approved: bool
    quality_score: float = Field(ge=0.0, le=10.0, default=8.0)
    security_issues: List[str] = Field(default_factory=list)
    style_improvements: List[str] = Field(default_factory=list)
    feedback: str = ""


class ApprovalPayload(BaseModel):
    ticket_id: str
    qa_passed: bool = True
    code_review_passed: bool = True
    test_summary: str = ""


class EscalatePayload(BaseModel):
    ticket_id: str
    reason: str
    retry_count: int
    suggested_action: str = "Human Review"


class DeliveryPayload(BaseModel):
    project_name: str
    files_generated: List[str]
    setup_instructions: str
    verification_status: str


# --- Core A2A Message Envelope ---

class A2AMessage(BaseModel):
    """Universal envelope for all Agent-to-Agent transmissions."""

    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    timestamp: float = Field(default_factory=time.time)
    sender: str
    recipient: str
    action: ActionType
    ticket_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)

    def summary(self) -> str:
        tid = f"[{self.ticket_id}] " if self.ticket_id else ""
        return f"{self.sender} -> {self.recipient} : {self.action.value} {tid}"
