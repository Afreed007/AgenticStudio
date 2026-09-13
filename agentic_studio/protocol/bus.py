"""A2A Message Bus implementation for routing, dispatching, and audit logging."""

import logging
from typing import Callable, Dict, List, Optional
from .models import A2AMessage

logger = logging.getLogger("A2ABus")


class A2ABus:
    """In-memory Agent-to-Agent message router and event bus."""

    def __init__(self):
        # agent_name -> message handler callable: handler(msg: A2AMessage) -> Optional[A2AMessage]
        self._handlers: Dict[str, Callable[[A2AMessage], Optional[A2AMessage]]] = {}
        # Chronological audit log of all messages
        self.message_history: List[A2AMessage] = []
        # Observers for streaming UI/CLI output
        self._observers: List[Callable[[A2AMessage], None]] = []

    def register_agent(
        self, agent_name: str, handler: Callable[[A2AMessage], Optional[A2AMessage]]
    ) -> None:
        """Register an agent's incoming mailbox handler."""
        self._handlers[agent_name] = handler
        logger.debug(f"Registered agent '{agent_name}' on A2A bus.")

    def add_observer(self, observer: Callable[[A2AMessage], None]) -> None:
        """Add an observer callback to tap into real-time bus traffic."""
        self._observers.append(observer)

    def dispatch(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Dispatch a message to its recipient agent and notify observers.

        Returns the response message produced by the recipient agent (if any).
        """
        self.message_history.append(message)

        # Notify observers (UI / CLI logger)
        for obs in self._observers:
            try:
                obs(message)
            except Exception as e:
                logger.error(f"Observer error: {e}")

        recipient = message.recipient
        if recipient not in self._handlers:
            logger.warning(
                f"Dead letter: recipient '{recipient}' is not registered on the A2A bus."
            )
            return None

        handler = self._handlers[recipient]
        response = handler(message)

        if response:
            self.message_history.append(response)
            for obs in self._observers:
                try:
                    obs(response)
                except Exception as e:
                    logger.error(f"Observer error on response: {e}")

        return response

    def get_ticket_history(self, ticket_id: str) -> List[A2AMessage]:
        """Return all messages associated with a given ticket."""
        return [m for m in self.message_history if m.ticket_id == ticket_id]
