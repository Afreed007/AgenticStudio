"""Base Agent abstraction for all Agentic Studio personas."""

import abc
import logging
from typing import Optional
from agentic_studio.protocol.models import A2AMessage
from agentic_studio.protocol.bus import A2ABus
from agentic_studio.llm.client import LLMClient
from agentic_studio.blackboard.state import TaskBoard
from agentic_studio.blackboard.workspace import WorkspaceManager

logger = logging.getLogger("BaseAgent")


class BaseAgent(abc.ABC):
    """Abstract base class representing an autonomous agent in the studio."""

    def __init__(
        self,
        name: str,
        role: str,
        bus: A2ABus,
        llm: LLMClient,
        blackboard: TaskBoard,
        workspace: WorkspaceManager,
    ):
        self.name = name
        self.role = role
        self.bus = bus
        self.llm = llm
        self.blackboard = blackboard
        self.workspace = workspace

        # Register mailbox handler on A2A bus
        self.bus.register_agent(self.name, self.handle_message)

    @abc.abstractmethod
    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Process an incoming A2A message and optionally produce a reply."""
        pass

    def send_a2a(
        self,
        recipient: str,
        action: any,
        payload: dict,
        ticket_id: Optional[str] = None,
    ) -> Optional[A2AMessage]:
        """Helper to create and dispatch a typed message over the A2A bus."""
        msg = A2AMessage(
            sender=self.name,
            recipient=recipient,
            action=action,
            ticket_id=ticket_id,
            payload=payload,
        )
        return self.bus.dispatch(msg)
