"""Async runner adapter for MedTour AI ADK agents."""

from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from medtour_ai.agents.config import get_settings


class AdkPlannerRunner:
    """Small wrapper around ADK Runner.

    The API layer should depend on this wrapper instead of importing ADK
    directly. That keeps future moves to Vertex AI Agent Engine or another
    session service localized.
    """

    def __init__(self) -> None:
        try:
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            from medtour_ai.agents.agent import root_agent, timeline_regeneration_agent
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "google-adk is not installed. Install requirements.txt or use planner_backend='local'."
            ) from exc

        self.settings = get_settings()
        self.session_service = InMemorySessionService()
        self.report_runner = Runner(
            app_name=self.settings.app_name,
            agent=root_agent,
            session_service=self.session_service,
        )
        self.timeline_runner = Runner(
            app_name=f"{self.settings.app_name}_timeline",
            agent=timeline_regeneration_agent,
            session_service=self.session_service,
        )

    async def generate_report(
        self,
        intake_payload: dict[str, Any],
        *,
        user_id: str = "anonymous",
        session_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._run(
            runner=self.report_runner,
            app_name=self.settings.app_name,
            payload=intake_payload,
            user_id=user_id,
            session_id=session_id,
        )

    async def regenerate_timeline(
        self,
        timeline_payload: dict[str, Any],
        *,
        user_id: str = "anonymous",
        session_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._run(
            runner=self.timeline_runner,
            app_name=f"{self.settings.app_name}_timeline",
            payload=timeline_payload,
            user_id=user_id,
            session_id=session_id,
        )

    async def _run(
        self,
        *,
        runner: Runner,
        app_name: str,
        payload: dict[str, Any],
        user_id: str,
        session_id: str | None,
    ) -> dict[str, Any]:
        from google.genai import types

        session_id = session_id or f"ses_{uuid4().hex}"
        await self.session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

        message = types.Content(
            role="user",
            parts=[types.Part(text=json.dumps(payload, ensure_ascii=False))],
        )

        final_text = ""
        events = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            events.append(
                {
                    "author": getattr(event, "author", None),
                    "is_final": bool(getattr(event, "is_final_response", lambda: False)()),
                }
            )
            if getattr(event, "is_final_response", lambda: False)():
                final_text = _event_text(event)

        if not final_text:
            return {
                "status": "failed",
                "error": {
                    "code": "ADK_NO_FINAL_RESPONSE",
                    "message": "The ADK runner finished without a final response.",
                },
                "events": events,
            }

        try:
            parsed = _parse_json_text(final_text)
        except json.JSONDecodeError:
            return {
                "status": "failed",
                "error": {
                    "code": "ADK_INVALID_JSON",
                    "message": "The planner returned non-JSON output.",
                    "raw_output": final_text,
                },
                "events": events,
            }

        if isinstance(parsed, dict):
            parsed.setdefault("session_id", session_id)
            parsed.setdefault("events", events)
        return parsed


def _parse_json_text(text: str) -> Any:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return json.loads(cleaned)


def _event_text(event: Any) -> str:
    content = getattr(event, "content", None)
    if not content:
        return ""
    parts = getattr(content, "parts", None) or []
    texts = []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            texts.append(text)
    return "\n".join(texts).strip()
