"""LLM provider factory for CloudDesk Support Platform."""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract LLM provider."""

    @abstractmethod
    async def call_structured(
        self,
        prompt: str,
        output_model: Type[T],
        **kwargs,
    ) -> tuple[T, Dict[str, int], int, int]:
        """Call LLM and return structured output.

        Returns: (output_model, token_usage, latency_ms, call_count)
        """
        pass

    @abstractmethod
    async def call(
        self,
        prompt: str,
        **kwargs,
    ) -> str:
        """Call LLM and return raw text."""
        pass


class FakeLLMProvider(LLMProvider):
    """Fake LLM provider for offline testing."""

    def __init__(self):
        self.call_count = 0

    async def call_structured(
        self,
        prompt: str,
        output_model: Type[T],
        **kwargs,
    ) -> tuple[T, Dict[str, int], int, int]:
        """Return a fake structured response based on output model."""
        self.call_count += 1

        # Generate appropriate fake response based on model
        if output_model.__name__ == "Classification":
            from app.schemas.workflow import Classification
            return Classification(
                category="login_issue",
                summary="Fake classification summary",
                confidence=0.95,
            ), {"input": 100, "output": 50, "total": 150}, 10, 1

        elif output_model.__name__ == "SeverityAssessment":
            from app.schemas.workflow import SeverityAssessment
            return SeverityAssessment(
                level="medium",
                reason="Fake severity assessment",
            ), {"input": 100, "output": 30, "total": 130}, 10, 1

        elif output_model.__name__ == "Diagnosis":
            from app.schemas.workflow import Diagnosis
            return Diagnosis(
                probable_causes=["Cause 1", "Cause 2"],
                steps=["Step 1", "Step 2"],
            ), {"input": 200, "output": 100, "total": 300}, 15, 1

        elif output_model.__name__ == "ResolutionPlan":
            from app.schemas.workflow import ResolutionPlan, PlannedAction
            return ResolutionPlan(
                summary="Fake resolution summary",
                customer_reply="Fake customer reply",
                internal_notes="Fake internal notes",
                actions=[PlannedAction(tool="update_ticket", args={"status": "resolved"})],
                grounding_score=0.9,
            ), {"input": 300, "output": 150, "total": 450}, 20, 1

        elif output_model.__name__ == "EscalationDecision":
            from app.schemas.workflow import EscalationDecision
            return EscalationDecision(
                escalation_required=False,
                team=None,
                reason="No escalation needed",
                confidence=0.9,
            ), {"input": 150, "output": 50, "total": 200}, 10, 1

        elif output_model.__name__ == "KnowledgeOutput":
            from app.schemas.workflow import KnowledgeOutput, Evidence, PreviousCase
            return KnowledgeOutput(
                evidence=[],
                similar_cases=[],
            ), {"input": 100, "output": 50, "total": 150}, 10, 1

        # Default: try to create empty model
        try:
            return output_model(), {"input": 0, "output": 0, "total": 0}, 0, 0
        except Exception:
            raise ValueError(f"No fake response for model: {output_model.__name__}")

    async def call(
        self,
        prompt: str,
        **kwargs,
    ) -> str:
        """Return fake text response."""
        self.call_count += 1
        return "Fake LLM response"


# Global provider instance
_provider: Optional[LLMProvider] = None


def get_llm() -> LLMProvider:
    """Get or create the LLM provider."""
    global _provider
    if _provider is None:
        settings = get_settings()
        if settings.LLM_PROVIDER == "fake":
            _provider = FakeLLMProvider()
        elif settings.LLM_PROVIDER == "openai":
            _provider = _create_openai_provider()
        elif settings.LLM_PROVIDER == "anthropic":
            _provider = _create_anthropic_provider()
        else:
            logger.warning(f"Unknown LLM provider: {settings.LLM_PROVIDER}, using fake")
            _provider = FakeLLMProvider()
    return _provider


def _create_openai_provider() -> LLMProvider:
    """Create OpenAI provider."""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import PydanticOutputParser
        from langchain_core.prompts import ChatPromptTemplate

        settings = get_settings()

        class OpenAIProvider(LLMProvider):
            def __init__(self):
                self.llm = ChatOpenAI(
                    model=settings.LLM_MODEL,
                    api_key=settings.LLM_API_KEY,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                )

            async def call_structured(
                self,
                prompt: str,
                output_model: Type[T],
                **kwargs,
            ) -> tuple[T, Dict[str, int], int, int]:
                parser = PydanticOutputParser(pydantic_object=output_model)
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", "You are a helpful assistant. {format_instructions}"),
                    ("human", "{prompt}"),
                ])
                chain = prompt_template | self.llm | parser
                result = await chain.ainvoke({
                    "prompt": prompt,
                    "format_instructions": parser.get_format_instructions(),
                })
                # Token usage would come from callback
                return result, {"input": 0, "output": 0, "total": 0}, 0, 1

            async def call(self, prompt: str, **kwargs) -> str:
                result = await self.llm.ainvoke(prompt)
                return result.content

        return OpenAIProvider()
    except ImportError:
        logger.warning("langchain_openai not installed, using fake provider")
        return FakeLLMProvider()


def _create_anthropic_provider() -> LLMProvider:
    """Create Anthropic provider."""
    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_core.output_parsers import PydanticOutputParser
        from langchain_core.prompts import ChatPromptTemplate

        settings = get_settings()

        class AnthropicProvider(LLMProvider):
            def __init__(self):
                self.llm = ChatAnthropic(
                    model=settings.LLM_MODEL,
                    api_key=settings.LLM_API_KEY,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                )

            async def call_structured(
                self,
                prompt: str,
                output_model: Type[T],
                **kwargs,
            ) -> tuple[T, Dict[str, int], int, int]:
                parser = PydanticOutputParser(pydantic_object=output_model)
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", "You are a helpful assistant. {format_instructions}"),
                    ("human", "{prompt}"),
                ])
                chain = prompt_template | self.llm | parser
                result = await chain.ainvoke({
                    "prompt": prompt,
                    "format_instructions": parser.get_format_instructions(),
                })
                return result, {"input": 0, "output": 0, "total": 0}, 0, 1

            async def call(self, prompt: str, **kwargs) -> str:
                result = await self.llm.ainvoke(prompt)
                return result.content

        return AnthropicProvider()
    except ImportError:
        logger.warning("langchain_anthropic not installed, using fake provider")
        return FakeLLMProvider()


async def call_structured(
    prompt: str,
    output_model: Type[T],
    **kwargs,
) -> tuple[T, Dict[str, int], int, int]:
    """Convenience function to call structured LLM."""
    provider = get_llm()
    return await provider.call_structured(prompt, output_model, **kwargs)