"""FastAPI service exposing the MedTour AI backend contract."""

from __future__ import annotations

from typing import Any, Literal
import os

from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

load_dotenv()

from medtour_ai.agents.schemas import IntakeAnswers
from medtour_ai.agents.config import get_settings
from medtour_ai.services.adk_runner import AdkPlannerRunner
from medtour_ai.services.auth_store import TRUSTED_SESSION_DAYS, InMemoryAuthStore
from medtour_ai.services.planner import LocalPlannerService
from medtour_ai.services.report_store import InMemoryReportStore

app = FastAPI(title="MedTour AI API", version="0.1.0")
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:8000,http://localhost:5173,http://127.0.0.1:8000,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
cors_origins = sorted(
    {
        *cors_origins,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    }
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
store = InMemoryReportStore()
auth_store = InMemoryAuthStore()
local_planner = LocalPlannerService()
_adk_runner: AdkPlannerRunner | None = None

SESSION_COOKIE_NAME = "medtour_session"


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "code": "UNHANDLED_SERVER_ERROR",
                "message": str(exc) or exc.__class__.__name__,
                "path": request.url.path,
            }
        },
    )


class NormalizeRequest(BaseModel):
    answers: IntakeAnswers


class CreateReportRequest(BaseModel):
    profile_draft_id: str
    generation_mode: str = "multi_city"
    max_city_options: int = Field(default=4, ge=1, le=4)
    currency: str = "SGD"
    language: str = "en"
    run_now: bool = True
    planner_backend: Literal["local", "adk"] = Field(default_factory=lambda: os.getenv("DEFAULT_PLANNER_BACKEND", "local"))


class RegenerateTimelineRequest(BaseModel):
    base_timeline_version_id: str
    preferences: dict[str, Any]
    run_now: bool = True
    planner_backend: Literal["local", "adk"] = Field(default_factory=lambda: os.getenv("DEFAULT_PLANNER_BACKEND", "local"))


class UpdateReadinessItemRequest(BaseModel):
    status: Literal["pending", "in_progress", "complete", "blocked"]
    note: str | None = None


class StartLoginRequest(BaseModel):
    email: str
    trusted_device: bool = True


class VerifyLoginRequest(BaseModel):
    challenge_id: str
    code: str
    trusted_device: bool = True


class RecoveryLoginRequest(BaseModel):
    email: str
    recovery_code: str
    trusted_device: bool = True


class CompletePasskeyRegistrationRequest(BaseModel):
    challenge_id: str
    label: str = "Trusted device"


class AnswerConfirmationRequest(BaseModel):
    selected_option: str
    freeform_note: str | None = None


class AdvisorHandoffRequest(BaseModel):
    selected_option_id: str
    contact: dict[str, str]
    preferred_language: str = "en"
    consent: bool


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/planner/config")
def planner_config() -> dict[str, Any]:
    settings = get_settings()
    default_backend = os.getenv("DEFAULT_PLANNER_BACKEND", "local")
    return {
        "default_backend": default_backend if default_backend in {"local", "adk"} else "local",
        "adk_available": bool(settings.openai_api_key),
        "agent_backend": {
            "app_name": settings.app_name,
            "profile_model": settings.llm_model,
            "planner_model": settings.planner_model,
        },
    }


@app.post("/api/v1/auth/login/start")
def start_login(request: StartLoginRequest) -> dict[str, Any]:
    if "@" not in request.email:
        raise HTTPException(status_code=400, detail="A valid email address is required")
    login = auth_store.start_email_login(request.email, request.trusted_device)
    return {
        "challenge_id": login["challenge_id"],
        "email": login["email"],
        "delivery_channel": login["delivery_channel"],
        "expires_in_seconds": login["expires_in_seconds"],
        "created_user": login["created_user"],
        "dev_code": login["dev_code"],
        "message": "Local dev code returned in dev_code. Production should send this by email.",
    }


@app.post("/api/v1/auth/login/verify")
def verify_login(request: VerifyLoginRequest, response: Response) -> dict[str, Any]:
    result = auth_store.verify_email_login(request.challenge_id, request.code, request.trusted_device)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired login code")
    _set_session_cookie(response, result["session_token"])
    return {
        "user": result["user"],
        "session": result["session"],
        "recovery_codes": result["recovery_codes"],
    }


@app.post("/api/v1/auth/recovery/verify")
def verify_recovery_login(request: RecoveryLoginRequest, response: Response) -> dict[str, Any]:
    result = auth_store.verify_recovery_code(request.email, request.recovery_code, request.trusted_device)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid recovery code")
    _set_session_cookie(response, result["session_token"])
    return {
        "user": result["user"],
        "session": result["session"],
        "recovery_codes": result["recovery_codes"],
    }


@app.get("/api/v1/auth/session")
def get_auth_session(medtour_session: str | None = Cookie(default=None)) -> dict[str, Any]:
    session = auth_store.session_from_token(medtour_session)
    if not session:
        return {"authenticated": False}
    user = auth_store.users_by_id[session["user_id"]]
    return {
        "authenticated": True,
        "user": auth_store.public_user(user),
        "session": auth_store.public_session(session),
    }


@app.post("/api/v1/auth/logout")
def logout(response: Response, medtour_session: str | None = Cookie(default=None)) -> dict[str, str]:
    auth_store.end_session(medtour_session)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"status": "signed_out"}


@app.post("/api/v1/auth/passkeys/register/start")
def start_passkey_registration(medtour_session: str | None = Cookie(default=None)) -> dict[str, Any]:
    session = _require_session(medtour_session)
    return auth_store.start_passkey_registration(session["user_id"])


@app.post("/api/v1/auth/passkeys/register/complete")
def complete_passkey_registration(
    request: CompletePasskeyRegistrationRequest,
    medtour_session: str | None = Cookie(default=None),
) -> dict[str, Any]:
    _require_session(medtour_session)
    credential = auth_store.complete_passkey_registration(request.challenge_id, request.label)
    if not credential:
        raise HTTPException(status_code=401, detail="Invalid or expired passkey challenge")
    return {"status": "registered", "credential": credential}


@app.get("/api/v1/intake/schema")
def intake_schema() -> dict[str, Any]:
    return {
        "steps": [
            {
                "id": "medical_purpose",
                "type": "single_choice",
                "title": "What medical care are you planning for?",
                "options": ["eye_surgery", "dental_care", "health_checkup", "medical_aesthetics"],
            },
            {
                "id": "procedure_subtype",
                "type": "adaptive_single_choice",
                "title": "Which procedure are you considering?",
                "depends_on": "medical_purpose",
                "options_by_medical_purpose": {
                    "eye_surgery": ["smile_pro", "lasik", "icl", "cataract", "not_sure"],
                    "dental_care": ["single_implant", "multiple_implants", "crown_bridge", "root_canal", "not_sure"],
                    "health_checkup": ["executive_screening", "cardio_screening", "cancer_markers", "women_health", "not_sure"],
                    "medical_aesthetics": ["skin_laser", "injectables", "body_contouring", "minor_surgery", "not_sure"],
                },
            },
            {
                "id": "program_details",
                "type": "adaptive_object",
                "title": "What details clarify this medical program?",
                "depends_on": "medical_purpose",
            },
            {
                "id": "nationality",
                "type": "country_select",
                "title": "Which passport will you travel with?",
            },
            {
                "id": "departure_city",
                "type": "short_search",
                "title": "Where will you depart from?",
            },
            {
                "id": "current_insurance_holder",
                "type": "short_text",
                "title": "Who is your current insurance holder?",
                "optional": True,
            },
            {
                "id": "duration_preference",
                "type": "single_choice",
                "title": "How long can you stay?",
                "options": ["3_4_days", "5_7_days", "8_plus_days", "not_sure"],
            },
            {
                "id": "season_flexibility",
                "type": "single_choice",
                "title": "Are winter or off-season dates acceptable?",
                "options": ["winter_ok", "offseason_ok", "selected_month_only", "depends_on_price"],
            },
        ],
        "defaults": {
            "budget_tier": "balanced",
            "traveler_count": 1,
            "hotel_preference": "near_hospital_foreign_guest_eligible",
            "tourism_intensity": "light",
        },
    }


@app.post("/api/v1/intake/normalize")
def normalize_intake(request: NormalizeRequest) -> dict[str, Any]:
    answers = request.answers.model_dump()
    field_status = {key: "user_confirmed" for key, value in answers.items() if value not in (None, "")}
    defaults = {
        "budget_tier": answers.get("budget_tier", "balanced"),
        "traveler_count": answers.get("traveler_count", 1),
        "hotel_preference": answers.get("hotel_preference", "near_hospital_foreign_guest_eligible"),
        "tourism_intensity": answers.get("tourism_intensity", "light"),
    }
    confirmation_requests = []
    if answers.get("procedure_subtype") in (None, "not_sure"):
        confirmation_requests.append(
            {
                "confirmation_id": "conf_procedure_subtype",
                "blocking": False,
                "question": "Do you want us to choose the likely procedure type?",
                "reason": "Procedure type can change the required medical days and budget range.",
                "recommended_option": "let_system_choose",
                "options": [
                    {
                        "id": "let_system_choose",
                        "label": "Let system choose",
                        "impact": "Generate options using conservative assumptions.",
                        "recommended": True,
                    },
                    {
                        "id": "ask_advisor",
                        "label": "Ask advisor",
                        "impact": "Pause final locking until a human advisor confirms.",
                    },
                ],
                "affected_sections": ["medical_rules", "timeline", "costs"],
            }
        )

    draft = store.create_profile_draft(
        {
            "profile": answers,
            "field_status": field_status,
            "defaults": defaults,
            "confirmation_requests": confirmation_requests,
        }
    )
    return draft


@app.post("/api/v1/reports")
async def create_report(request: CreateReportRequest) -> dict[str, Any]:
    draft = store.get_profile_draft(request.profile_draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="profile_draft_id not found")

    operation = store.create_report_operation(request.profile_draft_id, request.model_dump())
    if not request.run_now:
        return operation

    store.update_operation(operation["operation_id"], {"status": "running", "current_stage": "generating_report", "progress": 35})
    try:
        raw_report = await _generate_report(draft, request)
    except HTTPException as exc:
        raw_report = {
            "status": "failed",
            "error": {
                "code": "PLANNER_BACKEND_ERROR",
                "message": str(exc.detail),
            },
        }
    except Exception as exc:
        raw_report = {
            "status": "failed",
            "error": {
                "code": "PLANNER_BACKEND_EXCEPTION",
                "message": str(exc) or exc.__class__.__name__,
            },
        }
    try:
        generated = _normalize_generated_report(raw_report, draft, request)
    except Exception as exc:
        generated = _normalize_generated_report(
            {
                "status": "failed",
                "error": {
                    "code": "REPORT_NORMALIZATION_EXCEPTION",
                    "message": str(exc) or exc.__class__.__name__,
                },
            },
            draft,
            request,
        )
    if generated.get("status") != "failed" and not generated.get("city_options"):
        generated = {
            **generated,
            "status": "failed",
            "report_status": "failed",
            "error": {
                "code": "PLANNER_EMPTY_OPTIONS",
                "message": "Planner completed but returned no city options.",
            },
        }
    ready = generated.get("status") != "failed" and "error" not in generated
    store.update_report(
        operation["report_id"],
        {
            "status": "ready" if ready else "failed",
            "generated_report": generated,
            "city_options": generated.get("city_options", []),
            "confirmation_requests": generated.get("confirmation_requests", []),
            "disclaimers": generated.get("disclaimers", []),
        },
    )
    store.update_operation(
        operation["operation_id"],
        {
            "status": "complete" if ready else "failed",
            "current_stage": "ready" if ready else "failed",
            "progress": 100 if ready else 0,
        },
    )
    return {**operation, "status": "ready" if ready else "failed", "report": generated}


@app.get("/api/v1/operations/{operation_id}")
def get_operation(operation_id: str) -> dict[str, Any]:
    operation = store.get_operation(operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="operation_id not found")
    return operation


@app.get("/api/v1/reports/{report_id}/status")
def report_status(report_id: str) -> dict[str, Any]:
    status = store.get_status(report_id)
    if not status:
        raise HTTPException(status_code=404, detail="report_id not found")
    return status


@app.get("/api/v1/reports/{report_id}")
def get_report(report_id: str) -> dict[str, Any]:
    report = store.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report_id not found")
    return report


@app.get("/api/v1/reports/{report_id}/options")
def get_options(report_id: str) -> dict[str, Any]:
    report = store.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report_id not found")
    generated = report.get("generated_report", {})
    return {
        "options": report.get("city_options", []),
        "comparison": generated.get("comparison", {}),
    }


@app.post("/api/v1/reports/{report_id}/options/{option_id}/select")
def select_option(report_id: str, option_id: str) -> dict[str, Any]:
    report = store.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report_id not found")
    if not store.find_option(report_id, option_id):
        raise HTTPException(status_code=404, detail="option_id not found")
    store.select_option(report_id, option_id)
    return {"report_id": report_id, "selected_option_id": option_id, "status": "selected"}


@app.get("/api/v1/reports/{report_id}/options/{option_id}/timeline")
def get_timeline(report_id: str, option_id: str) -> dict[str, Any]:
    option = _find_option(report_id, option_id)
    return {
        "option_id": option_id,
        "timeline_version_id": option.get("timeline_version_id", "tlv_1"),
        "days": option.get("timeline", []),
    }


@app.post("/api/v1/reports/{report_id}/options/{option_id}/timeline/regenerate")
async def regenerate_timeline(
    report_id: str,
    option_id: str,
    request: RegenerateTimelineRequest,
) -> dict[str, Any]:
    option = _find_option(report_id, option_id)
    if not request.run_now:
        return {"operation_id": f"op_regen_{option_id}", "status": "queued"}
    regenerated = await _regenerate_timeline(report_id, option, request)
    store.add_timeline_version(report_id, option_id, regenerated, accepted=False)
    return {"operation_id": f"op_regen_{option_id}", "status": "ready", "timeline": regenerated}


@app.post("/api/v1/reports/{report_id}/options/{option_id}/timeline/{timeline_version_id}/accept")
def accept_timeline(report_id: str, option_id: str, timeline_version_id: str) -> dict[str, Any]:
    accepted = store.accept_timeline_version(report_id, option_id, timeline_version_id)
    if not accepted:
        raise HTTPException(status_code=404, detail="timeline_version_id not found")
    return {
        "report_id": report_id,
        "option_id": option_id,
        "timeline_version_id": timeline_version_id,
        "status": "accepted",
    }


@app.get("/api/v1/reports/{report_id}/options/{option_id}/costs")
def get_costs(report_id: str, option_id: str) -> dict[str, Any]:
    option = _find_option(report_id, option_id)
    return {
        "option_id": option_id,
        "currency": "SGD",
        "total": option.get("total_estimated_cost"),
        "categories": option.get("cost_breakdown", {}),
        "benchmark": {"net_savings": option.get("estimated_net_savings")},
    }


@app.get("/api/v1/reports/{report_id}/options/{option_id}/readiness")
def get_readiness(report_id: str, option_id: str) -> dict[str, Any]:
    option = _find_option(report_id, option_id)
    items = option.get("readiness_items") or option.get("readiness_summary") or []
    completed = [item for item in items if item.get("status") == "complete"]
    high_risk = [item for item in items if item.get("priority") == "high" and item.get("status") != "complete"]
    return {
        "option_id": option_id,
        "completion_percent": round((len(completed) / len(items)) * 100) if items else 0,
        "completed_count": len(completed),
        "total_count": len(items),
        "high_risk_items": high_risk,
        "sections": [{"title": "Pre-trip readiness", "items": items}],
    }


@app.patch("/api/v1/reports/{report_id}/options/{option_id}/readiness/items/{item_id}")
def update_readiness_item(
    report_id: str,
    option_id: str,
    item_id: str,
    request: UpdateReadinessItemRequest,
) -> dict[str, Any]:
    item = store.update_readiness_item(report_id, option_id, item_id, request.status, request.note)
    if not item:
        raise HTTPException(status_code=404, detail="readiness item not found")
    return item


@app.get("/api/v1/reports/{report_id}/confirmations")
def get_confirmations(report_id: str) -> dict[str, Any]:
    report = store.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report_id not found")
    return {"confirmation_requests": report.get("confirmation_requests", [])}


@app.post("/api/v1/reports/{report_id}/confirmations/{confirmation_id}/answer")
def answer_confirmation(
    report_id: str,
    confirmation_id: str,
    request: AnswerConfirmationRequest,
) -> dict[str, Any]:
    confirmation = store.answer_confirmation(
        report_id,
        confirmation_id,
        request.selected_option,
        request.freeform_note,
    )
    if not confirmation:
        raise HTTPException(status_code=404, detail="confirmation_id not found")
    return {
        "status": "accepted",
        "confirmation": confirmation,
        "affected_sections": confirmation.get("affected_sections", []),
        "regeneration_required": bool(confirmation.get("blocking")),
    }


@app.post("/api/v1/reports/{report_id}/advisor/handoff")
def advisor_handoff(report_id: str, request: AdvisorHandoffRequest) -> dict[str, Any]:
    if not request.consent:
        raise HTTPException(status_code=400, detail="User consent is required for advisor handoff")
    if not store.find_option(report_id, request.selected_option_id):
        raise HTTPException(status_code=404, detail="selected_option_id not found")
    lead = store.create_advisor_lead(report_id, request.model_dump())
    if not lead:
        raise HTTPException(status_code=404, detail="report_id not found")
    return lead


def _find_option(report_id: str, option_id: str) -> dict[str, Any]:
    if not store.get_report(report_id):
        raise HTTPException(status_code=404, detail="report_id not found")
    option = store.find_option(report_id, option_id)
    if option:
        return option
    raise HTTPException(status_code=404, detail="option_id not found")


def _require_session(session_token: str | None) -> dict[str, Any]:
    session = auth_store.session_from_token(session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    return session


def _set_session_cookie(response: Response, session_token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_token,
        max_age=TRUSTED_SESSION_DAYS * 24 * 60 * 60,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )


def _normalize_generated_report(raw: dict[str, Any], draft: dict[str, Any], request: CreateReportRequest) -> dict[str, Any]:
    if raw.get("error") or raw.get("status") == "failed":
        return {
            "status": "failed",
            "report_status": "failed",
            "profile": draft.get("profile", {}),
            "city_options": [],
            "comparison": {},
            "confirmation_requests": [],
            "disclaimers": [],
            "error": raw.get("error", {"code": "PLANNER_FAILED", "message": "Planner failed."}),
            "events": raw.get("events", []),
            "session_id": raw.get("session_id"),
            "planner_backend": request.planner_backend,
        }

    report = raw.get("generated_report") if isinstance(raw.get("generated_report"), dict) else raw
    profile = report.get("profile") or draft.get("profile", {})
    options = [
        _normalize_city_option(option, index, request.currency)
        for index, option in enumerate(report.get("city_options") or report.get("options") or [])
        if isinstance(option, dict)
    ]
    recommended_option_id = report.get("recommended_option_id") or (options[0]["option_id"] if options else None)
    for option in options:
        option["selected_as_primary"] = option["option_id"] == recommended_option_id

    return {
        **report,
        "status": "ready",
        "report_status": report.get("report_status", "ready"),
        "profile": profile,
        "city_options": options,
        "comparison": report.get("comparison") or _comparison_from_options(options),
        "recommended_option_id": recommended_option_id,
        "confirmation_requests": report.get("confirmation_requests", []),
        "disclaimers": report.get("disclaimers", []),
        "assumptions": report.get("assumptions", []),
        "planner_backend": request.planner_backend,
        "agent_session_id": raw.get("session_id"),
        "agent_events": raw.get("events", []),
    }


def _normalize_city_option(option: dict[str, Any], index: int, currency: str) -> dict[str, Any]:
    city = option.get("city") or f"City {index + 1}"
    option_id = option.get("option_id") or f"opt_{_slug(city)}_{index + 1}"
    normalized = dict(option)
    normalized["option_id"] = option_id
    normalized["city"] = city
    normalized["recommendation_label"] = option.get("recommendation_label") or option.get("label") or "City Option"
    normalized["target_hospital"] = option.get("target_hospital") or option.get("hospital") or option.get("hospital_name") or "Hospital to confirm"
    normalized["required_days"] = int(option.get("required_days") or option.get("total_days") or len(option.get("timeline", [])) or 0)
    normalized["timeline"] = _normalize_timeline(option.get("timeline", []), currency)
    normalized["cost_breakdown"] = {
        key: _normalize_money(value, currency)
        for key, value in (option.get("cost_breakdown") or {}).items()
    }
    insurance = option.get("insurance_policy")
    if isinstance(insurance, dict):
        insurance = dict(insurance)
        insurance["estimated_premium"] = _normalize_money(insurance.get("estimated_premium"), currency)
        normalized["insurance_policy"] = insurance
        normalized["cost_breakdown"].setdefault("travel_insurance", insurance["estimated_premium"])
    total = option.get("total_estimated_cost") or option.get("total_estimated_cost_sgd")
    if not total and normalized["cost_breakdown"]:
        total = {
            "amount": sum(float(value.get("amount") or 0) for value in normalized["cost_breakdown"].values()),
            "currency": currency,
        }
    normalized["total_estimated_cost"] = _normalize_money(total, currency)
    normalized["estimated_net_savings"] = _normalize_money(option.get("estimated_net_savings") or option.get("estimated_net_savings_sgd"), currency)
    normalized["readiness_items"] = _normalize_readiness_items(option.get("readiness_items") or option.get("readiness_summary") or [])
    normalized["key_risks"] = option.get("key_risks") or []
    normalized["metadata"] = {
        "source": "agent_estimate",
        "confidence_level": "medium",
        "data_status": "estimated",
        **(option.get("metadata") or {}),
    }
    return normalized


def _normalize_timeline(timeline: Any, currency: str) -> list[dict[str, Any]]:
    if not isinstance(timeline, list):
        return []
    if timeline and all(isinstance(item, dict) and ("time" in item or "event" in item) for item in timeline):
        grouped: dict[str, list[dict[str, Any]]] = {}
        for item in timeline:
            time_value = str(item.get("time") or "")
            date_value = time_value[:10] if len(time_value) >= 10 else ""
            grouped.setdefault(date_value, []).append(item)
        timeline = [
            {
                "day": index,
                "date": date_value,
                "title": f"Day {index}",
                "items": [
                    {
                        "category": "medical" if any(keyword in str(item.get("event", "")).lower() for keyword in ("hospital", "registration", "diagnostic", "procedure", "follow-up", "consultation")) else "readiness",
                        "title": item.get("event") or "Plan item",
                        "start_time": _normalize_agent_time(item.get("time"), date_value),
                        "end_time": _normalize_agent_time(item.get("time"), date_value),
                        "location_name": item.get("location_name"),
                        "details": item.get("details") or {},
                    }
                    for item in items
                ],
            }
            for index, (date_value, items) in enumerate(grouped.items(), start=1)
        ]
    days = []
    for index, day in enumerate(timeline, start=1):
        if not isinstance(day, dict):
            continue
        items = []
        for item in day.get("items", []):
            if not isinstance(item, dict):
                continue
            item = dict(item)
            item.setdefault("item_id", f"tli_agent_{index}_{len(items) + 1}")
            item.setdefault("category", "readiness")
            item.setdefault("title", item.get("event") or "Plan item")
            if item.get("time") and not item.get("start_time"):
                item["start_time"] = _normalize_agent_time(item.get("time"), day.get("date") or "")
            if item.get("start_time") and not item.get("end_time"):
                item["end_time"] = item["start_time"]
            if item.get("estimated_cost") is not None:
                item["estimated_cost"] = _normalize_money(item["estimated_cost"], currency)
            items.append(item)
        days.append(
            {
                **day,
                "day": int(day.get("day") or index),
                "date": day.get("date") or "",
                "title": day.get("title") or f"Day {index}",
                "items": items,
            }
        )
    return days


def _normalize_agent_time(value: Any, fallback_date: str) -> str:
    text = str(value or "")
    if "T" in text and len(text) == 16:
        return f"{text}:00+08:00"
    if "T" in text:
        return text
    if len(text) == 5 and fallback_date:
        return f"{fallback_date}T{text}:00+08:00"
    if len(text) >= 10:
        return f"{text[:10]}T09:00:00+08:00"
    if fallback_date:
        return f"{fallback_date}T09:00:00+08:00"
    return ""


def _normalize_readiness_items(items: Any) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        return []
    normalized = []
    for index, item in enumerate(items, start=1):
        if isinstance(item, str):
            item = {"title": item, "steps": [item]}
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "id": item.get("id") or f"readiness_{index}",
                "title": item.get("title") or f"Readiness item {index}",
                "priority": item.get("priority") or "medium",
                "status": item.get("status") or "pending",
                "steps": item.get("steps") or [],
                "helpful_links": item.get("helpful_links") or [],
            }
        )
    return normalized


def _normalize_money(value: Any, currency: str) -> dict[str, Any]:
    if isinstance(value, dict):
        result = dict(value)
        result["amount"] = _safe_float(result.get("amount") or result.get("mid") or result.get("value") or 0)
        result["currency"] = result.get("currency") or currency
        return result
    if isinstance(value, (int, float)):
        return {"amount": float(value), "currency": currency}
    if isinstance(value, str):
        return {"amount": _safe_float(value), "currency": currency, "label": value}
    return {"amount": 0, "currency": currency}


def _safe_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if cleaned.upper() in {"", "TBD", "N/A", "NA", "-", "UNKNOWN"}:
            return 0
        try:
            return float(cleaned)
        except ValueError:
            return 0
    return 0


def _comparison_from_options(options: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "metrics": [
            {
                "option_id": option["option_id"],
                "city": option["city"],
                "hospital": option.get("target_hospital"),
                "required_days": option.get("required_days"),
                "medical_cost": option.get("cost_breakdown", {}).get("medical"),
                "insurance_estimate": option.get("cost_breakdown", {}).get("travel_insurance"),
                "total_cost": option.get("total_estimated_cost"),
                "estimated_savings": option.get("estimated_net_savings"),
                "readiness_risk_count": len(option.get("key_risks", [])),
            }
            for option in options
        ]
    }


def _slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_") or "option"


async def _generate_report(draft: dict[str, Any], request: CreateReportRequest) -> dict[str, Any]:
    if request.planner_backend == "local":
        return local_planner.generate_report(draft, request.model_dump())

    runner = _get_adk_runner()
    return await runner.generate_report(
        {
            "profile_draft_id": request.profile_draft_id,
            "answers": draft["profile"],
            "generation_request": request.model_dump(),
        }
    )


async def _regenerate_timeline(
    report_id: str,
    option: dict[str, Any],
    request: RegenerateTimelineRequest,
) -> dict[str, Any]:
    if request.planner_backend == "local":
        return local_planner.regenerate_timeline(option, request.preferences)

    runner = _get_adk_runner()
    return await runner.regenerate_timeline(
        {
            "report_id": report_id,
            "option": option,
            "base_timeline_version_id": request.base_timeline_version_id,
            "preferences": request.preferences,
        }
    )


def _get_adk_runner() -> AdkPlannerRunner:
    global _adk_runner
    if _adk_runner is None:
        try:
            _adk_runner = AdkPlannerRunner()
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    return _adk_runner
