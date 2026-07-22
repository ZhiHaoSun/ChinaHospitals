"""Runtime configuration for ADK agents."""

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    """Environment-backed settings.

    OPENAI_API_KEY is read by LiteLLM/OpenAI at runtime. We still expose the
    field here so API startup checks can fail fast in deployed environments.
    """

    app_name: str = "medtour_ai_planner"
    llm_model: str = "openai/gpt-4o-mini"
    planner_model: str = "openai/gpt-4o"
    report_synthesis_model: str = "openai/gpt-5.1"
    embedding_model: str = "text-embedding-3-small"
    default_currency: str = "SGD"
    default_language: str = "en"
    openai_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "medtour_ai_planner"),
        llm_model=os.getenv("LLM_MODEL", "openai/gpt-4o-mini"),
        planner_model=os.getenv("PLANNER_MODEL", "openai/gpt-4o"),
        report_synthesis_model=os.getenv("REPORT_SYNTHESIS_MODEL", "openai/gpt-5.1"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        default_currency=os.getenv("DEFAULT_CURRENCY", "SGD"),
        default_language=os.getenv("DEFAULT_LANGUAGE", "en"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
