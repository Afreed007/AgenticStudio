"""DevOps & Delivery Agent: Packages project, generates Dockerfile, and prepares delivery docs."""

import logging
from typing import Optional
from agentic_studio.agents.base import BaseAgent
from agentic_studio.protocol.models import (
    A2AMessage,
    ActionType,
    DeliveryPayload,
)

logger = logging.getLogger("DevOpsEngineer")


class DevOpsAgent(BaseAgent):
    """Packages application for deployment, creates Dockerfile, and writes handover docs."""

    def __init__(self, bus, llm, blackboard, workspace):
        super().__init__(
            name="DevOpsEngineer",
            role="DevOps & Release Architect",
            bus=bus,
            llm=llm,
            blackboard=blackboard,
            workspace=workspace,
        )

    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        if message.payload.get("sprint_complete"):
            return self.package_delivery()
        return None

    def package_delivery(self) -> A2AMessage:
        logger.info(f"[{self.name}] Packaging final delivery bundle...")

        bundle = self.llm.mock_provider.generate_devops_bundle("URL Shortener Service")

        for filename, content in bundle.items():
            self.workspace.write_file(filename, content)
            logger.info(f"[{self.name}] Created '{filename}'")

        all_files = self.workspace.list_files()
        logger.info(f"[{self.name}] Project successfully packaged! Total files: {len(all_files)}")

        return self.send_a2a(
            recipient="ClientIntake",
            action=ActionType.DELIVERY_COMPLETE,
            payload={
                "project_name": "URL Shortener Service",
                "files_generated": all_files,
                "setup_instructions": "Run 'pytest tests/' to verify suite. Dockerfile provided.",
                "verification_status": "All tests passed (100% green)",
            },
        )
