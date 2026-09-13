"""Unified LLM client interface supporting Google Gemini and Mock fallback."""

import json
import logging
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from agentic_studio.config import config
from agentic_studio.llm.mock import MockLLMProvider

logger = logging.getLogger("LLMClient")


class LLMClient:
    """Client for generating agent responses using Google Gemini API or Mock provider."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.gemini_api_key
        self.model_name = model or config.default_model
        self.mock_provider = MockLLMProvider()
        self._genai_client = None

        if self.api_key and not config.use_mock_llm:
            try:
                from google import genai
                self._genai_client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Gemini Client with model '{self.model_name}'")
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai: {e}. Falling back to mock.")
                self._genai_client = None

    @property
    def is_live(self) -> bool:
        return self._genai_client is not None

    def generate_json(
        self,
        system_instruction: str,
        user_prompt: str,
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        """Generate structured JSON response adhering to a schema."""
        if not self.is_live:
            # Route to mock based on context
            return self._mock_route_json(system_instruction, user_prompt)

        try:
            from google.genai import types
            
            gen_config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                response_mime_type="application/json"
            )
            if response_schema:
                gen_config.response_schema = response_schema

            response = self._genai_client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=gen_config,
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini API error: {e}. Falling back to mock generator.")
            return self._mock_route_json(system_instruction, user_prompt)

    def generate_text(self, system_instruction: str, user_prompt: str) -> str:
        """Generate raw text/code output."""
        if not self.is_live:
            return self._mock_route_text(system_instruction, user_prompt)

        try:
            from google.genai import types
            gen_config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2
            )
            response = self._genai_client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=gen_config,
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}. Falling back to mock generator.")
            return self._mock_route_text(system_instruction, user_prompt)

    def _mock_route_json(self, system: str, user: str) -> Dict[str, Any]:
        """Route to appropriate mock generator based on system instruction."""
        s = system.lower()
        if "business analyst" in s:
            return self.mock_provider.generate_prd(user)
        elif "architect" in s:
            return self.mock_provider.generate_architecture({"project_name": "url_shortener_service"})
        return {"result": "ok"}

    def _mock_route_text(self, system: str, user: str) -> str:
        s = system.lower()
        if "qa" in s:
            return self.mock_provider.generate_qa_tests("test")
        return "# Generated code placeholder"
