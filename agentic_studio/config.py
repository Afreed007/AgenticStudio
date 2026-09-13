"""Configuration settings for Agentic Studio."""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


class StudioConfig(BaseModel):
    """Global configuration for Agentic Studio agency."""

    # Workspace directory where target projects are generated
    workspace_root: Path = Field(
        default_factory=lambda: Path(os.getenv("WORKSPACE_ROOT", "./target_project")).resolve()
    )

    # LLM Settings
    gemini_api_key: str = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "")
    )
    default_model: str = Field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    )
    use_mock_llm: bool = Field(
        default_factory=lambda: os.getenv("USE_MOCK_LLM", "false").lower() in ("1", "true", "yes")
    )

    # SDLC Governance & Circuit Breakers
    max_review_retries: int = Field(
        default=3,
        description="Max bug fix / review attempts per ticket before human escalation"
    )
    test_timeout_seconds: int = Field(
        default=30,
        description="Max execution time for automated test runs"
    )
    verbose: bool = Field(
        default=True,
        description="Whether to emit detailed A2A message logs"
    )


# Default shared singleton config
config = StudioConfig()
