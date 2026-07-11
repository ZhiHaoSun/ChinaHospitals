"""FastAPI service exposing the MedTour AI backend contract."""

from __future__ import annotations

from typing import Any, Literal
from io import BytesIO
import os
from pathlib import Path
import re

from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, ValidationError
import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

load_dotenv()

from medtour_ai.agents.schemas import GeneratedReport, IntakeAnswers
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
PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_FILES = {
    "index.html": PROJECT_ROOT / "index.html",
    "app.js": PROJECT_ROOT / "app.js",
    "styles.css": PROJECT_ROOT / "styles.css",
}
PDF_FONT_NAME = "MedTourSans"
REPORTLAB_FONT_DIR = Path(reportlab.__file__).resolve().parent / "fonts"
PDF_FONT_PATHS = [
    Path(os.getenv("MEDTOUR_PDF_FONT_PATH", "")),
    PROJECT_ROOT / "assets" / "fonts" / "DejaVuSans.ttf",
    REPORTLAB_FONT_DIR / "Vera.ttf",
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
]


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


class PlanExportRequest(BaseModel):
    option: dict[str, Any]
    report: dict[str, Any] = Field(default_factory=dict)


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
                "options": ["eye_surgery", "dental_care", "health_checkup", "car_t_blood_cancer"],
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
                    "car_t_blood_cancer": ["car_t_consult", "b_cell_lymphoma", "multiple_myeloma", "leukemia", "not_sure"],
                },
            },
            {
                "id": "program_details",
                "type": "adaptive_text",
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
        generated = _normalize_generated_report(raw_report, draft, request, operation["report_id"])
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
            operation["report_id"],
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


@app.get("/api/v1/reports/{report_id}/options/{option_id}/export.pdf")
def export_plan_pdf(report_id: str, option_id: str) -> Response:
    report = store.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report_id not found")
    option = store.find_option(report_id, option_id)
    if not option:
        raise HTTPException(status_code=404, detail="option_id not found")

    pdf_bytes = _build_plan_pdf(report, option)
    filename = f"medtour_{_slug(option.get('city') or 'plan')}_{_slug(option_id)}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/v1/plan-export.pdf")
def export_plan_snapshot_pdf(request: PlanExportRequest) -> Response:
    option = request.option
    if not option:
        raise HTTPException(status_code=422, detail="option is required")

    pdf_bytes = _build_plan_pdf(request.report, option)
    option_id = option.get("option_id") or "local_plan"
    filename = f"medtour_{_slug(option.get('city') or 'local_plan')}_{_slug(option_id)}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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


def _normalize_generated_report(
    raw: Any,
    draft: dict[str, Any],
    request: CreateReportRequest,
    report_id: str | None = None,
) -> dict[str, Any]:
    if isinstance(raw, list):
        raw = {"city_options": raw}
    if not isinstance(raw, dict):
        return {
            "report_id": report_id,
            "status": "failed",
            "report_status": "failed",
            "profile": draft.get("profile", {}),
            "city_options": [],
            "comparison": {},
            "confirmation_requests": [],
            "disclaimers": [],
            "error": {
                "code": "PLANNER_INVALID_OUTPUT",
                "message": f"Planner returned {type(raw).__name__}; expected an object or a list of city options.",
            },
            "events": [],
            "session_id": None,
            "planner_backend": request.planner_backend,
        }
    if raw.get("error") or raw.get("status") == "failed":
        return {
            "report_id": report_id,
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

    generated_report = raw.get("generated_report")
    if isinstance(generated_report, list):
        report = {"city_options": generated_report}
    elif isinstance(generated_report, dict):
        report = generated_report
    else:
        report = raw
    profile = _normalize_profile_program_details(report.get("profile") or draft.get("profile", {}))
    options = [
        _normalize_city_option(option, index, request.currency)
        for index, option in enumerate(report.get("city_options") or report.get("options") or [])
        if isinstance(option, dict)
    ]
    comparison = report.get("comparison") or {}
    _apply_comparison_metrics_to_options(options, comparison, request.currency)
    recommended_option_id = report.get("recommended_option_id") or (options[0]["option_id"] if options else None)
    for option in options:
        option["selected_as_primary"] = option["option_id"] == recommended_option_id

    normalized = {
        **report,
        "report_id": report_id or report.get("report_id") or "",
        "status": "ready",
        "report_status": report.get("report_status", "ready"),
        "profile": profile,
        "city_options": options,
        "comparison": comparison or _comparison_from_options(options),
        "recommended_option_id": recommended_option_id,
        "confirmation_requests": _normalize_confirmation_requests(report.get("confirmation_requests", [])),
        "audit_summary": _normalize_audit_summary(report.get("audit_summary")),
        "disclaimers": report.get("disclaimers", []),
        "assumptions": report.get("assumptions", []),
        "planner_backend": request.planner_backend,
        "agent_session_id": raw.get("session_id"),
        "agent_events": raw.get("events", []),
    }
    try:
        GeneratedReport.model_validate(normalized)
    except ValidationError as exc:
        return {
            "report_id": normalized["report_id"],
            "status": "failed",
            "report_status": "failed",
            "profile": profile,
            "city_options": [],
            "comparison": {},
            "confirmation_requests": normalized.get("confirmation_requests", []),
            "disclaimers": normalized.get("disclaimers", []),
            "error": {
                "code": "REPORT_SCHEMA_VALIDATION_FAILED",
                "message": "Planner output did not satisfy the GeneratedReport schema.",
                "validation_errors": _schema_error_summary(exc),
            },
            "events": raw.get("events", []),
            "session_id": raw.get("session_id"),
            "planner_backend": request.planner_backend,
        }
    return normalized


def _schema_error_summary(exc: ValidationError) -> list[dict[str, Any]]:
    return [
        {
            "path": ".".join(str(part) for part in error.get("loc", ())),
            "message": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        for error in exc.errors()
    ]


def _normalize_confirmation_requests(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    normalized = []
    for index, item in enumerate(value, start=1):
        if isinstance(item, str):
            text = item.strip()
            if not text:
                continue
            normalized.append(
                {
                    "confirmation_id": f"conf_agent_{index}",
                    "blocking": False,
                    "question": text if text.endswith("?") else text,
                    "reason": "Agent requested user confirmation.",
                    "recommended_option": "confirm",
                    "options": [
                        {
                            "id": "confirm",
                            "label": "Confirm",
                            "impact": "Keeps planning moving after this detail is verified.",
                            "recommended": True,
                        },
                        {
                            "id": "needs_help",
                            "label": "Need help",
                            "impact": "Marks this item for advisor follow-up.",
                        },
                    ],
                    "affected_sections": ["planning"],
                }
            )
            continue
        if isinstance(item, dict):
            request = dict(item)
            request.setdefault("confirmation_id", f"conf_agent_{index}")
            request.setdefault("blocking", False)
            request.setdefault("question", request.get("title") or request.get("message") or "Please confirm this planning detail.")
            request.setdefault("reason", request.get("description") or "Agent requested user confirmation.")
            request.setdefault("recommended_option", None)
            request["options"] = _normalize_confirmation_options(request.get("options"))
            request.setdefault("affected_sections", [])
            normalized.append(request)
    return normalized


def _normalize_profile_program_details(profile: Any) -> dict[str, Any]:
    if not isinstance(profile, dict):
        return {}
    normalized = dict(profile)
    normalized["program_details"] = _program_details_text(normalized.get("program_details"))
    return normalized


def _program_details_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return "; ".join(
            f"{str(key).replace('_', ' ')}: {value_part}"
            for key, value_part in value.items()
            if value_part not in (None, "")
        )
    if isinstance(value, list):
        return "; ".join(str(item) for item in value if item not in (None, ""))
    return str(value)


def _normalize_confirmation_options(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        return [
            {
                "id": "confirm",
                "label": "Confirm",
                "impact": "Uses this confirmed detail in the plan.",
                "recommended": True,
            },
            {
                "id": "needs_help",
                "label": "Need help",
                "impact": "Marks this item for follow-up.",
            },
        ]
    normalized = []
    for index, option in enumerate(value, start=1):
        if isinstance(option, str):
            normalized.append(
                {
                    "id": f"option_{index}",
                    "label": option,
                    "impact": "Uses this answer for planning.",
                    "recommended": index == 1,
                }
            )
            continue
        if isinstance(option, dict):
            normalized.append(
                {
                    "id": str(option.get("id") or f"option_{index}"),
                    "label": str(option.get("label") or option.get("title") or f"Option {index}"),
                    "impact": str(option.get("impact") or option.get("description") or "Uses this answer for planning."),
                    "recommended": bool(option.get("recommended", index == 1)),
                }
            )
    return normalized or _normalize_confirmation_options(None)


def _normalize_insurance_policy(
    insurance: dict[str, Any],
    option: dict[str, Any],
    currency: str,
) -> dict[str, Any]:
    normalized = dict(insurance)
    hospital_name = option.get("target_hospital") or normalized.get("hospital_name") or "Hospital to confirm"
    normalized["hospital_name"] = hospital_name
    normalized["medical_purpose"] = normalized.get("medical_purpose") or option.get("medical_purpose")
    normalized["policy_status"] = str(
        normalized.get("policy_status")
        or normalized.get("coverage_status")
        or normalized.get("status")
        or "needs_confirmation"
    )
    normalized["summary"] = str(
        normalized.get("summary")
        or normalized.get("notes")
        or "Insurance coverage, pre-authorization, direct billing, and reimbursement require insurer confirmation."
    )
    hospital_policy = normalized.get("hospital_policy")
    if not isinstance(hospital_policy, dict):
        hospital_policy = {}
    normalized["hospital_policy"] = {
        "direct_billing": str(
            hospital_policy.get("direct_billing")
            or normalized.get("direct_billing")
            or normalized.get("direct_billing_status")
            or "unknown"
        ),
        "preauthorization_required": bool(
            hospital_policy.get("preauthorization_required", normalized.get("preauthorization_required", True))
        ),
        "claim_documents": _string_list(
            hospital_policy.get("claim_documents")
            or normalized.get("claim_documents")
            or ["Medical report", "Itemized invoice", "Official receipt"]
        ),
        "common_exclusions": _string_list(hospital_policy.get("common_exclusions") or normalized.get("common_exclusions") or []),
    }
    normalized["provider_policy"] = normalized.get("provider_policy") if isinstance(normalized.get("provider_policy"), dict) else {}
    normalized["estimated_premium"] = _normalize_money(normalized.get("estimated_premium") or 0, currency)
    normalized["suggestions"] = _string_list(normalized.get("suggestions") or normalized.get("next_steps") or [])
    normalized["helpful_links"] = normalized.get("helpful_links") if isinstance(normalized.get("helpful_links"), list) else []
    normalized["metadata"] = _normalize_source_metadata(normalized.get("metadata"))
    return normalized


def _apply_comparison_metrics_to_options(
    options: list[dict[str, Any]],
    comparison: dict[str, Any],
    currency: str,
) -> None:
    metrics = comparison.get("metrics") if isinstance(comparison, dict) else None
    if not isinstance(metrics, list):
        return
    for option in options:
        metric = _find_comparison_metric(option, metrics)
        if not metric:
            continue
        current_savings = option.get("estimated_net_savings") or {}
        if (
            not _money_has_numeric_value(option.get("estimated_net_savings"), current_savings)
            or current_savings.get("source") == "derived_from_home_benchmark"
        ):
            raw_metric_savings = _first_present(
                metric,
                "estimated_savings",
                "estimated_net_savings",
                "net_savings",
                "savings",
                "savings_vs_home",
                "estimated_savings_vs_home",
            )
            savings = _normalize_money(raw_metric_savings, currency)
            if _money_has_numeric_value(raw_metric_savings, savings):
                option["estimated_net_savings"] = savings
        if not _money_has_numeric_value(option.get("total_estimated_cost"), option.get("total_estimated_cost") or {}):
            option["total_estimated_cost"] = _normalize_money(
                _first_present(metric, "total_cost", "total_estimated_cost"),
                currency,
            )
        if not _money_has_numeric_value(option.get("home_country_benchmark"), option.get("home_country_benchmark") or {}):
            option["home_country_benchmark"] = _normalize_money(
                _first_present(
                    metric,
                    "home_country_benchmark",
                    "home_cost_benchmark",
                    "home_total_cost",
                    "home_estimated_cost",
                ),
                currency,
            )
        if not _money_has_numeric_value(option.get("estimated_net_savings"), option.get("estimated_net_savings") or {}):
            option["estimated_net_savings"] = _normalize_estimated_savings({**metric, **option}, option, currency)


def _find_comparison_metric(option: dict[str, Any], metrics: list[Any]) -> dict[str, Any] | None:
    option_id = option.get("option_id")
    city = str(option.get("city") or "").strip().lower()
    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        if option_id and metric.get("option_id") == option_id:
            return metric
    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        if city and str(metric.get("city") or "").strip().lower() == city:
            return metric
    return None


def _normalize_city_option(option: dict[str, Any], index: int, currency: str) -> dict[str, Any]:
    city = option.get("city") or f"City {index + 1}"
    option_id = option.get("option_id") or f"opt_{_slug(city)}_{index + 1}"
    normalized = dict(option)
    normalized["option_id"] = option_id
    normalized["city"] = city
    normalized["recommendation_label"] = option.get("recommendation_label") or option.get("label") or "City Option"
    normalized["target_hospital"] = option.get("target_hospital") or option.get("hospital") or option.get("hospital_name") or "Hospital to confirm"
    timeline_source = _first_non_empty(
        option,
        "timeline",
        "detailed_timeline",
        "plan_timeline",
        "hospital_timeline",
        "itinerary",
        "schedule",
        "days",
        "timeline_days",
    )
    normalized["required_days"] = int(
        option.get("required_days")
        or option.get("total_days")
        or _timeline_day_count(timeline_source)
        or 0
    )
    normalized["timeline"] = _normalize_timeline(timeline_source, currency)
    normalized["cost_breakdown"] = {
        key: _normalize_money(value, currency)
        for key, value in (option.get("cost_breakdown") or {}).items()
    }
    flight = _normalize_flight(option, normalized, currency)
    if flight:
        normalized["flight"] = flight
        normalized["cost_breakdown"].setdefault("flight", flight["estimated_cost"])
    hotel = _normalize_hotel(option, normalized, currency)
    if hotel:
        normalized["hotel"] = hotel
        normalized["cost_breakdown"].setdefault(
            "hotel",
            {
                "amount": hotel["nightly_rate"]["amount"] * hotel["nights"],
                "currency": hotel["nightly_rate"]["currency"],
            },
        )
    insurance = option.get("insurance_policy")
    if isinstance(insurance, dict):
        insurance = _normalize_insurance_policy(insurance, normalized, currency)
        normalized["insurance_policy"] = insurance
        normalized["cost_breakdown"].setdefault("travel_insurance", insurance["estimated_premium"])
    total = option.get("total_estimated_cost") or option.get("total_estimated_cost_sgd")
    if not total and normalized["cost_breakdown"]:
        total = {
            "amount": sum(float(value.get("amount") or 0) for value in normalized["cost_breakdown"].values()),
            "currency": currency,
        }
    normalized["total_estimated_cost"] = _normalize_money(total, currency)
    normalized["home_country_benchmark"] = _normalize_money(
        _first_present(
            option,
            "home_country_benchmark",
            "home_country_benchmark_sgd",
            "home_cost_benchmark",
            "home_total_cost",
            "home_estimated_cost",
        ),
        currency,
    )
    normalized["estimated_net_savings"] = _normalize_estimated_savings(option, normalized, currency)
    normalized["readiness_items"] = _normalize_readiness_items(option.get("readiness_items") or option.get("readiness_summary") or [])
    normalized["key_risks"] = option.get("key_risks") or []
    normalized["metadata"] = _normalize_source_metadata({
        "source": "agent_estimate",
        "confidence_level": "medium",
        "data_status": "estimated",
        **(option.get("metadata") or {}),
    })
    if isinstance(normalized.get("audit_report"), dict):
        normalized["audit_report"] = _normalize_audit_report(normalized["audit_report"])
    if not normalized["timeline"] or not _timeline_has_items(normalized["timeline"]):
        normalized["timeline"] = _fallback_timeline_for_option(normalized, currency)
        normalized["required_days"] = normalized["required_days"] or len(normalized["timeline"])
    return normalized


def _normalize_flight(
    option: dict[str, Any],
    normalized: dict[str, Any],
    currency: str,
) -> dict[str, Any] | None:
    source = _first_non_empty(
        option,
        "flight",
        "recommended_flight",
        "flight_details",
        "travel_flight",
        "arrival_flight",
        "outbound_flight",
    )
    cost_breakdown = normalized.get("cost_breakdown") or {}
    cost_hint = _first_non_empty(cost_breakdown, "flight", "airfare", "air_ticket", "travel")
    if not isinstance(source, dict):
        if cost_hint is None:
            return None
        source = {}
    cost = _normalize_money(
        _first_present(
            source,
            "estimated_cost",
            "estimated_cost_sgd",
            "cost",
            "price",
            "fare",
        )
        or cost_hint,
        currency,
    )
    return {
        "airline": str(_first_present(source, "airline", "carrier") or "Airline to confirm"),
        "flight_number": str(
            _first_present(source, "flight_number", "flight_no", "number") or "Flight number to confirm"
        ),
        "departure_airport": str(
            _first_present(source, "departure_airport", "from_airport", "origin_airport", "origin")
            or option.get("departure_city")
            or "Departure airport to confirm"
        ),
        "arrival_airport": str(
            _first_present(source, "arrival_airport", "to_airport", "destination_airport", "destination")
            or normalized.get("city")
            or "Arrival airport to confirm"
        ),
        "departure_time": str(
            _first_present(source, "departure_time", "depart_at", "departure_datetime", "outbound_departure_time")
            or ""
        ),
        "arrival_time": str(
            _first_present(source, "arrival_time", "arrive_at", "arrival_datetime", "outbound_arrival_time")
            or ""
        ),
        "estimated_cost": cost,
    }


def _normalize_hotel(
    option: dict[str, Any],
    normalized: dict[str, Any],
    currency: str,
) -> dict[str, Any] | None:
    source = _first_non_empty(
        option,
        "hotel",
        "recommended_hotel",
        "hotel_choice",
        "accommodation",
        "lodging",
    )
    cost_breakdown = normalized.get("cost_breakdown") or {}
    cost_hint = _first_non_empty(cost_breakdown, "hotel", "lodging", "accommodation")
    if not isinstance(source, dict):
        if cost_hint is None:
            return None
        source = {}
    nights = int(_safe_float(_first_present(source, "nights", "night_count") or max(normalized.get("required_days", 0) - 1, 1)))
    nightly_rate_raw = _first_present(
        source,
        "nightly_rate",
        "nightly_rate_sgd",
        "rate",
        "daily_rate",
        "price_per_night",
    )
    nightly_rate = _normalize_money(nightly_rate_raw, currency)
    if not _money_has_numeric_value(nightly_rate_raw, nightly_rate) and cost_hint is not None:
        total = _normalize_money(cost_hint, currency)
        nightly_rate = {
            "amount": float(total.get("amount") or 0) / max(nights, 1),
            "currency": total.get("currency") or currency,
        }
    foreign_guest_eligible = _first_present(source, "foreign_guest_eligible", "foreigner_friendly")
    return {
        "name": str(_first_present(source, "name", "hotel_name") or "Hotel to confirm"),
        "address": str(_first_present(source, "address", "location") or normalized.get("city") or ""),
        "nightly_rate": nightly_rate,
        "nights": max(nights, 1),
        "distance_to_hospital": str(
            _first_present(source, "distance_to_hospital", "distance", "hospital_distance")
            or "Distance to hospital to confirm"
        ),
        "foreign_guest_eligible": bool(foreign_guest_eligible) if foreign_guest_eligible is not None else False,
        "cancellation_policy": str(
            _first_present(source, "cancellation_policy", "refund_policy")
            or "Cancellation policy to confirm"
        ),
    }


def _normalize_timeline(timeline: Any, currency: str) -> list[dict[str, Any]]:
    if isinstance(timeline, dict):
        nested = _first_non_empty(
            timeline,
            "days",
            "timeline",
            "timeline_items",
            "items",
            "events",
            "schedule",
            "itinerary",
            "agenda",
            "tasks",
            "steps",
            "timeline_days",
        )
        if nested is None:
            nested = [
                {"title": str(title), "items": items}
                for title, items in timeline.items()
                if isinstance(items, list)
            ]
        timeline = nested
    if not isinstance(timeline, list):
        return []
    if timeline and all(_looks_like_timeline_item(item) for item in timeline):
        grouped: dict[str, list[dict[str, Any]]] = {}
        for item in timeline:
            if isinstance(item, str):
                item = {"event": item}
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
                        "title": item.get("event") or item.get("title") or item.get("name") or "Plan item",
                        "start_time": _normalize_agent_time(item.get("time"), date_value),
                        "end_time": _normalize_agent_time(item.get("time"), date_value),
                        "location_name": item.get("location_name") or item.get("location"),
                        "details": _normalize_timeline_details(item.get("details")),
                        "estimated_cost": _normalize_money(item["estimated_cost"], currency)
                        if item.get("estimated_cost") is not None
                        else None,
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
        day_date = str(day.get("date") or f"0000-00-{index:02d}")
        day_items = _timeline_day_items(day)
        for item in day_items:
            if isinstance(item, str):
                item = {"title": item}
            if not isinstance(item, dict):
                continue
            item = dict(item)
            item.setdefault("item_id", f"tli_agent_{index}_{len(items) + 1}")
            item.setdefault("category", "readiness")
            item.setdefault("title", item.get("event") or item.get("name") or "Plan item")
            if item.get("time") and not item.get("start_time"):
                item["start_time"] = _normalize_agent_time(item.get("time"), day_date)
            if not item.get("start_time"):
                item["start_time"] = _default_timeline_time(day_date, len(items), end=False)
            if item.get("start_time") and not item.get("end_time"):
                item["end_time"] = _default_timeline_time(day_date, len(items), end=True)
            item["category"] = _normalize_timeline_category(item.get("category"))
            item["confidence_level"] = _normalize_confidence_level(item.get("confidence_level"))
            if item.get("estimated_cost") is not None:
                item["estimated_cost"] = _normalize_money(item["estimated_cost"], currency)
            item["details"] = _normalize_timeline_details(item.get("details"))
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


def _timeline_day_items(day: dict[str, Any]) -> list[Any]:
    source = _first_non_empty(
        day,
        "items",
        "timeline_items",
        "events",
        "schedule",
        "activities",
        "agenda",
        "tasks",
        "steps",
        "appointments",
    )
    if isinstance(source, dict):
        flattened = []
        for section_title, section_items in source.items():
            if isinstance(section_items, list):
                for item in section_items:
                    if isinstance(item, dict):
                        flattened.append({"phase": str(section_title), **item})
                    else:
                        flattened.append({"phase": str(section_title), "title": str(item)})
            elif section_items:
                flattened.append({"phase": str(section_title), "title": str(section_items)})
        return flattened
    if isinstance(source, list):
        return source
    if isinstance(source, str):
        return [source]
    if _looks_like_timeline_item(day):
        return [day]
    summary = _first_non_empty(day, "summary", "description", "details", "plan")
    if summary:
        return [{"title": str(summary)}]
    return []


def _timeline_has_items(days: list[dict[str, Any]]) -> bool:
    return any(day.get("items") for day in days if isinstance(day, dict))


def _looks_like_timeline_item(item: Any) -> bool:
    if isinstance(item, str):
        return True
    if not isinstance(item, dict):
        return False
    return not any(key in item for key in ("items", "events", "schedule", "activities", "timeline_items", "tasks", "steps")) and any(
        key in item
        for key in (
            "time",
            "event",
            "title",
            "name",
            "location",
            "location_name",
            "start_time",
            "estimated_cost",
            "description",
            "summary",
        )
    )


def _timeline_day_count(timeline: Any) -> int:
    normalized = timeline
    if isinstance(normalized, dict):
        normalized = _first_non_empty(normalized, "days", "timeline", "schedule", "itinerary", "timeline_items", "timeline_days")
    if isinstance(normalized, list):
        return len(normalized)
    return 0


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


def _default_timeline_time(day_date: str, item_index: int, *, end: bool) -> str:
    hour = min(9 + item_index, 21)
    minute = 45 if end else 0
    return f"{day_date}T{hour:02d}:{minute:02d}:00+08:00"


def _fallback_timeline_for_option(option: dict[str, Any], currency: str) -> list[dict[str, Any]]:
    city = option.get("city") or "Selected city"
    hospital = option.get("target_hospital") or "selected hospital international clinic"
    flight = option.get("flight") or {}
    hotel = option.get("hotel") or {}
    protocol = option.get("hospital_visit_protocol") or {}
    contact = protocol.get("registration_contact") if isinstance(protocol, dict) else {}
    doctor = protocol.get("suggested_doctor") if isinstance(protocol, dict) else {}
    registration_email = (contact or {}).get("email") or option.get("registration_email")
    doctor_name = (doctor or {}).get("name") or option.get("suggested_doctor_name")
    doctor_specialty = (
        (doctor or {}).get("specialty")
        or option.get("suggested_doctor_specialty")
        or "Assigned specialist to confirm"
    )
    medical_cost = option.get("cost_breakdown", {}).get("medical")
    flight_cost = flight.get("estimated_cost") or option.get("cost_breakdown", {}).get("flight")
    hotel_cost = option.get("cost_breakdown", {}).get("hotel")

    def item(
        category: str,
        title: str,
        day: int,
        start: str,
        end: str,
        *,
        location: str = "",
        cost: Any = None,
        hard: bool = False,
        steps: list[str] | None = None,
    ) -> dict[str, Any]:
        details = {}
        if category == "medical":
            details = {
                "registration_email": registration_email,
                "registration_email_status": (contact or {}).get("email_status") or "needs_confirmation",
                "appointment_phone": (contact or {}).get("appointment_phone"),
                "main_phone": (contact or {}).get("main_phone"),
                "wechat_or_portal_route": (contact or {}).get("wechat_or_portal_route"),
                "service_billing": protocol.get("service_billing") if isinstance(protocol, dict) else {},
                "service_billing_status": (protocol.get("service_billing") or {}).get("service_billing_status", "needs_confirmation") if isinstance(protocol, dict) else "needs_confirmation",
                "direct_billing_status": (protocol.get("service_billing") or {}).get("direct_billing_status", "unknown") if isinstance(protocol, dict) else "unknown",
                "suggested_doctor_name": doctor_name,
                "suggested_doctor_specialty": doctor_specialty,
                "hospital_steps": steps or [],
            }
        return {
            "item_id": f"tli_fallback_{day}_{_slug(title)}",
            "category": category,
            "title": title,
            "start_time": f"0000-00-{day:02d}T{start}:00+08:00",
            "end_time": f"0000-00-{day:02d}T{end}:00+08:00",
            "location_name": location,
            "estimated_cost": _normalize_money(cost, currency) if cost is not None else None,
            "hard_constraint": hard,
            "confidence_level": "medium",
            "details": details,
        }

    return [
        {
            "day": 1,
            "date": "",
            "title": f"Arrival and {city} Setup",
            "items": [
                item("flight", "Arrival flight", 1, "08:00", "13:30", location=flight.get("arrival_airport") or city, cost=flight_cost),
                item("hotel", "Hotel check-in near international clinic", 1, "15:00", "16:00", location=hotel.get("name") or city, cost=hotel_cost),
                item(
                    "medical",
                    "International desk pre-registration email check",
                    1,
                    "16:30",
                    "17:00",
                    location=hospital,
                    hard=True,
                    steps=[
                        "Confirm official international desk email before sending documents.",
                        "Send passport name, preferred appointment window, medical purpose, and current insurance holder.",
                        "Ask for doctor assignment, deposit requirement, interpreter support, and claim-document process.",
                    ],
                ),
            ],
        },
        {
            "day": 2,
            "date": "",
            "title": "Registration and Medical Assessment",
            "items": [
                item(
                    "medical",
                    "International outpatient registration and file setup",
                    2,
                    "08:30",
                    "09:30",
                    location=hospital,
                    hard=True,
                    steps=[
                        "Show passport, appointment confirmation, insurance card or guarantee letter, and payment method.",
                        "Create outpatient profile and confirm invoice name for insurance reimbursement.",
                        "Complete consent, privacy, interpreter, and deposit or pre-authorization checks.",
                    ],
                ),
                item(
                    "medical",
                    "Program-specific diagnostics and nurse intake",
                    2,
                    "09:30",
                    "12:00",
                    location=hospital,
                    cost=medical_cost,
                    hard=True,
                    steps=[
                        "Complete vitals, medical history, medication review, and program-specific tests.",
                        "Confirm whether results allow the planned procedure or checkup to continue on this trip.",
                    ],
                ),
                item(
                    "medical",
                    "Suggested doctor consultation and treatment decision",
                    2,
                    "14:00",
                    "15:30",
                    location=hospital,
                    hard=True,
                    steps=[
                        f"Meet {doctor_name} or request confirmed assignment through the international clinic.",
                        "Review eligibility, alternatives, risks, final price, insurance handling, and timing.",
                    ],
                ),
            ],
        },
        {
            "day": 3,
            "date": "",
            "title": "Procedure, Documents, and Follow-up",
            "items": [
                item(
                    "medical",
                    "Procedure or treatment block",
                    3,
                    "09:00",
                    "12:00",
                    location=hospital,
                    cost=medical_cost,
                    hard=True,
                    steps=[
                        "Reconfirm consent, assigned doctor, final estimate, deposit, and pre-authorization status.",
                        "Proceed only after same-day safety and eligibility confirmation.",
                    ],
                ),
                item(
                    "medical",
                    "Discharge briefing and insurance claim document collection",
                    3,
                    "14:00",
                    "15:30",
                    location=hospital,
                    hard=True,
                    steps=[
                        "Collect medical report, diagnosis certificate, itemized invoice, prescriptions, and receipts.",
                        "Confirm emergency contact route, medication instructions, and remote follow-up channel.",
                    ],
                ),
                item("flight", "Return flight after medical clearance", 3, "17:30", "22:30", location=flight.get("arrival_airport") or city, cost=flight_cost),
            ],
        },
    ]


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
                "priority": _normalize_priority(item.get("priority")),
                "status": _normalize_readiness_status(item.get("status")),
                "steps": item.get("steps") or [],
                "helpful_links": item.get("helpful_links") or [],
            }
        )
    return normalized


def _normalize_source_metadata(metadata: Any) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        metadata = {}
    normalized = dict(metadata)
    original_source = normalized.get("source")
    source = str(original_source or "agent_estimate").strip()
    if source not in {"rag", "external_api", "agent_estimate", "advisor_confirmed"}:
        normalized["original_source"] = source
        source = "agent_estimate"
    normalized["source"] = source
    normalized["confidence_level"] = _normalize_confidence_level(normalized.get("confidence_level"))
    normalized["data_status"] = _normalize_data_status(normalized.get("data_status"))
    return normalized


def _normalize_audit_report(audit_report: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(audit_report)
    normalized["metadata"] = _normalize_source_metadata(normalized.get("metadata"))
    normalized["checks"] = _normalize_audit_checks(normalized.get("checks"))
    normalized["blocking_issues"] = _normalize_audit_checks(normalized.get("blocking_issues"))
    normalized["warnings"] = _normalize_audit_checks(normalized.get("warnings"))
    normalized["audit_status"] = _normalize_option_audit_status(
        normalized.get("audit_status"),
        normalized["checks"],
        normalized["blocking_issues"],
        normalized["warnings"],
    )
    return normalized


def _normalize_audit_summary(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        return {"summary_items": _string_list(value)}
    if isinstance(value, str) and value.strip():
        return {"summary": value.strip()}
    return {}


def _normalize_option_audit_status(
    value: Any,
    checks: list[dict[str, Any]],
    blocking_issues: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> str:
    status = str(value or "").strip().lower()
    aliases = {
        "pass": "passed",
        "ok": "passed",
        "warn": "passed_with_warnings",
        "warning": "passed_with_warnings",
        "blocked": "needs_confirmation",
        "missing": "needs_confirmation",
    }
    status = aliases.get(status, status)
    if status in {"passed", "passed_with_warnings", "needs_confirmation", "failed"}:
        return status
    if blocking_issues or any(check.get("status") in {"fail", "needs_confirmation"} for check in checks):
        return "needs_confirmation"
    if warnings or any(check.get("status") == "warn" for check in checks):
        return "passed_with_warnings"
    if checks:
        return "passed"
    return "needs_confirmation"


def _normalize_audit_checks(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    normalized = []
    for index, check in enumerate(value, start=1):
        if isinstance(check, str):
            check = {"finding": check}
        if not isinstance(check, dict):
            continue
        item = dict(check)
        item["check_id"] = str(item.get("check_id") or f"audit_check_{index}")
        item["category"] = _normalize_audit_category(item.get("category"))
        item["status"] = _normalize_audit_status(item.get("status"))
        item["finding"] = str(item.get("finding") or item.get("message") or "Audit check requires review.")
        item["evidence"] = _string_list(item.get("evidence"))
        item["suggested_action"] = str(
            item.get("suggested_action")
            or item.get("action")
            or "Review this item before booking non-refundable travel."
        )
        normalized.append(item)
    return normalized


def _normalize_audit_category(value: Any) -> str:
    category = str(value or "source_freshness").strip().lower()
    aliases = {
        "hospital": "hospital_source",
        "contact": "hospital_contact",
        "billing": "service_billing",
        "service": "service_billing",
        "flight": "flight_price",
        "hotel": "hotel_price",
        "medical": "medical_cost",
        "insurance": "insurance_source",
        "math": "cost_math",
        "freshness": "source_freshness",
        "timeline": "itinerary_consistency",
        "itinerary": "itinerary_consistency",
    }
    category = aliases.get(category, category)
    allowed = {
        "hospital_source",
        "hospital_contact",
        "service_billing",
        "flight_price",
        "hotel_price",
        "medical_cost",
        "insurance_source",
        "cost_math",
        "source_freshness",
        "itinerary_consistency",
    }
    return category if category in allowed else "source_freshness"


def _normalize_audit_status(value: Any) -> str:
    status = str(value or "needs_confirmation").strip().lower()
    aliases = {
        "passed": "pass",
        "ok": "pass",
        "warning": "warn",
        "blocked": "fail",
        "missing": "needs_confirmation",
        "unknown": "needs_confirmation",
    }
    status = aliases.get(status, status)
    if status in {"pass", "warn", "fail", "needs_confirmation"}:
        return status
    return "needs_confirmation"


def _normalize_timeline_details(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        return {"notes": _string_list(value)}
    if isinstance(value, str) and value.strip():
        return {"note": value.strip()}
    return {}


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None and str(item).strip()]
    if isinstance(value, tuple):
        return [str(item) for item in value if item is not None and str(item).strip()]
    if isinstance(value, str):
        return [value] if value.strip() else []
    return [str(value)]


def _normalize_timeline_category(value: Any) -> str:
    category = str(value or "readiness").strip().lower()
    aliases = {
        "airport_transfer": "transport",
        "transfer": "transport",
        "appointment": "medical",
        "consultation": "medical",
        "registration": "medical",
        "procedure": "medical",
        "checkup": "medical",
        "accommodation": "hotel",
        "lodging": "hotel",
        "dining": "meal",
        "food": "meal",
        "prep": "readiness",
        "preparation": "readiness",
    }
    category = aliases.get(category, category)
    if category in {"flight", "hotel", "medical", "transport", "meal", "tourism", "readiness"}:
        return category
    return "readiness"


def _normalize_confidence_level(value: Any) -> str:
    confidence = str(value or "medium").strip().lower()
    aliases = {
        "med": "medium",
        "moderate": "medium",
        "estimated": "medium",
        "representative": "medium",
        "confirmed": "high",
        "official": "high",
        "uncertain": "low",
        "needs_confirmation": "low",
    }
    confidence = aliases.get(confidence, confidence)
    if confidence in {"high", "medium", "low"}:
        return confidence
    return "medium"


def _normalize_data_status(value: Any) -> str:
    status = str(value or "estimated").strip().lower()
    aliases = {
        "live": "real_time",
        "realtime": "real_time",
        "real-time": "real_time",
        "representative": "estimated",
        "planning_estimate": "estimated",
        "official": "needs_confirmation",
        "unverified": "needs_confirmation",
        "unknown": "needs_confirmation",
        "tbd": "needs_confirmation",
    }
    status = aliases.get(status, status)
    if status in {"real_time", "estimated", "stale", "needs_confirmation"}:
        return status
    return "estimated"


def _normalize_priority(value: Any) -> str:
    priority = str(value or "medium").strip().lower()
    if priority in {"low", "medium", "high"}:
        return priority
    if priority in {"urgent", "critical", "blocking"}:
        return "high"
    return "medium"


def _normalize_readiness_status(value: Any) -> str:
    status = str(value or "pending").strip().lower()
    aliases = {
        "todo": "pending",
        "to_do": "pending",
        "not_started": "pending",
        "needs_confirmation": "blocked",
        "waiting": "blocked",
        "done": "complete",
        "completed": "complete",
    }
    status = aliases.get(status, status)
    if status in {"pending", "in_progress", "complete", "blocked"}:
        return status
    return "pending"


def _normalize_money(value: Any, currency: str) -> dict[str, Any]:
    if isinstance(value, dict):
        result = dict(value)
        amount = _extract_money_amount(result)
        result["amount"] = amount
        result["currency"] = result.get("currency") or _extract_money_currency(result) or currency
        for range_key in ("low", "high", "min", "max"):
            if range_key in result:
                result[range_key] = _safe_float(result[range_key])
        return result
    if isinstance(value, (int, float)):
        return {"amount": float(value), "currency": currency}
    if isinstance(value, str):
        return {"amount": _safe_float(value), "currency": currency, "label": value}
    return {"amount": 0, "currency": currency}


def _extract_money_amount(value: dict[str, Any]) -> float:
    for key in (
        "amount",
        "mid",
        "median",
        "value",
        "estimated_amount",
        "estimated_cost",
        "estimated_cost_sgd",
        "estimated_cost_rmb",
        "cost",
        "cost_sgd",
        "cost_rmb",
        "price",
        "price_sgd",
        "price_rmb",
        "total",
        "total_cost",
        "total_estimated_cost",
        "estimated_net_savings",
        "estimated_savings",
        "net_savings",
        "savings",
        "savings_vs_home",
        "estimated_savings_vs_home",
        "premium",
        "estimated_premium",
    ):
        if key in value and value[key] is not None:
            amount = _money_amount_from_candidate(value[key])
            if amount is not None:
                return amount

    low = _first_present(value, "low", "min", "minimum", "lower_bound", "from")
    high = _first_present(value, "high", "max", "maximum", "upper_bound", "to")
    low_amount = _money_amount_from_candidate(low)
    high_amount = _money_amount_from_candidate(high)
    if low_amount is not None and high_amount is not None:
        return (low_amount + high_amount) / 2
    if low_amount is not None:
        return low_amount
    if high_amount is not None:
        return high_amount

    range_value = _first_present(value, "range", "estimate_range", "estimated_range")
    range_amount = _money_range_midpoint(range_value)
    if range_amount is not None:
        return range_amount

    return 0


def _money_amount_from_candidate(candidate: Any) -> float | None:
    if isinstance(candidate, (int, float)):
        return float(candidate)
    if isinstance(candidate, str):
        amount = _safe_float(candidate)
        return amount if amount != 0 else None
    if isinstance(candidate, dict):
        amount = _extract_money_amount(candidate)
        return amount if amount != 0 else None
    return None


def _money_range_midpoint(value: Any) -> float | None:
    if isinstance(value, (list, tuple)) and value:
        amounts = [
            amount
            for amount in (_money_amount_from_candidate(item) for item in value[:2])
            if amount is not None
        ]
        if len(amounts) == 2:
            return sum(amounts) / 2
        if amounts:
            return amounts[0]
    if isinstance(value, str):
        numbers = _numbers_from_text(value)
        if len(numbers) >= 2:
            return (numbers[0] + numbers[1]) / 2
        if numbers:
            return numbers[0]
    return None


def _extract_money_currency(value: dict[str, Any]) -> str | None:
    for key in (
        "amount",
        "estimated_cost",
        "cost",
        "price",
        "total",
        "estimated_net_savings",
        "estimated_savings",
        "net_savings",
        "savings",
        "estimated_premium",
    ):
        nested = value.get(key)
        if isinstance(nested, dict) and nested.get("currency"):
            return nested["currency"]
    return None


def _normalize_estimated_savings(
    option: dict[str, Any],
    normalized: dict[str, Any],
    currency: str,
) -> dict[str, Any]:
    raw_savings = _first_present(
        option,
        "estimated_net_savings",
        "estimated_net_savings_sgd",
        "estimated_savings",
        "estimated_savings_sgd",
        "net_savings",
        "savings",
        "savings_vs_home",
        "estimated_savings_vs_home",
    )
    savings = _normalize_money(raw_savings, currency)
    if _money_has_numeric_value(raw_savings, savings):
        return savings

    home_benchmark = normalized.get("home_country_benchmark") or {}
    total = normalized.get("total_estimated_cost") or {}
    home_amount = float(home_benchmark.get("amount") or 0)
    total_amount = float(total.get("amount") or 0)
    if home_amount and total_amount:
        return {
            "amount": max(home_amount - total_amount, 0),
            "currency": home_benchmark.get("currency") or total.get("currency") or currency,
            "source": "derived_from_home_benchmark",
        }
    return savings


def _first_present(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def _first_non_empty(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key not in payload:
            continue
        value = payload[key]
        if value is None:
            continue
        if isinstance(value, (str, list, dict, tuple, set)) and not value:
            continue
        return value
    return None


def _money_has_numeric_value(raw_value: Any, normalized_value: dict[str, Any]) -> bool:
    if raw_value is None:
        return False
    if isinstance(raw_value, str) and raw_value.strip().upper() in {"", "TBD", "N/A", "NA", "-", "UNKNOWN"}:
        return False
    return float(normalized_value.get("amount") or 0) != 0


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
            numbers = _numbers_from_text(cleaned)
            if numbers:
                return numbers[0]
            return 0
    return 0


def _numbers_from_text(value: str) -> list[float]:
    numbers = []
    for match in re.finditer(r"[-+]?\d*\.?\d+", value.replace(",", "")):
        try:
            numbers.append(float(match.group(0)))
        except ValueError:
            continue
    return numbers


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


def _build_plan_pdf(report: dict[str, Any], option: dict[str, Any]) -> bytes:
    font_name = _register_pdf_fonts()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.55 * inch,
        title=f"MedTour AI Plan - {option.get('city') or 'Selected City'}",
        author="MedTour AI",
    )
    styles = _pdf_styles(font_name)
    story: list[Any] = []

    city = _clean_text(option.get("city") or "Selected City")
    hospital = _clean_text(option.get("target_hospital") or "Hospital to confirm")
    story.append(Paragraph("MedTour AI Care Plan", styles["title"]))
    story.append(Paragraph(f"{city} - {hospital}", styles["subtitle"]))
    story.append(Spacer(1, 14))

    summary_rows = [
        ["City", city],
        ["Hospital", hospital],
        ["Medical need", _clean_text(option.get("medical_purpose") or "To confirm").replace("_", " ")],
        ["Procedure", _clean_text(option.get("procedure_subtype") or "To confirm").replace("_", " ")],
        ["Duration", f"{option.get('required_days') or '-'} days"],
        ["Total estimate", _format_money(option.get("total_estimated_cost"))],
    ]
    story.append(Paragraph("Plan Summary", styles["section"]))
    story.append(_pdf_key_value_table(summary_rows, styles))
    story.append(Spacer(1, 12))

    categories = option.get("cost_breakdown") or {}
    if categories:
        cost_rows = [["Category", "Estimate"]]
        cost_rows.extend(
            [_clean_text(label).replace("_", " ").title(), _format_money(value)]
            for label, value in categories.items()
        )
        story.append(Paragraph("Cost Breakdown", styles["section"]))
        story.append(_pdf_table(cost_rows, [3.8 * inch, 1.8 * inch], styles))
        story.append(Spacer(1, 12))

    policy = option.get("insurance_policy") or {}
    if policy:
        story.append(Paragraph("Insurance Notes", styles["section"]))
        story.append(Paragraph(_clean_text(policy.get("summary") or "Confirm coverage and claim requirements before booking."), styles["body"]))
        insurance_rows = [
            ["Policy status", _clean_text(policy.get("policy_status") or "needs confirmation").replace("_", " ")],
            ["Current holder", _clean_text(policy.get("current_holder") or "Not provided")],
            ["Hospital billing", _clean_text((policy.get("hospital_policy") or {}).get("direct_billing") or "Confirm with hospital")],
        ]
        story.append(_pdf_key_value_table(insurance_rows, styles))
        suggestions = policy.get("suggestions") or []
        if suggestions:
            story.append(Paragraph("Suggested Actions", styles["small_heading"]))
            for suggestion in suggestions[:6]:
                story.append(Paragraph(f"- {_clean_text(suggestion)}", styles["bullet"]))
        story.append(Spacer(1, 12))

    timeline = option.get("timeline") or []
    story.append(Paragraph("Itinerary Timeline", styles["section"]))
    if timeline:
        for day in timeline:
            day_parts = [
                Paragraph(
                    f"Day {day.get('day') or '-'}: {_clean_text(day.get('title') or 'Scheduled care')}",
                    styles["day"],
                )
            ]
            if day.get("date"):
                day_parts.append(Paragraph(_clean_text(day["date"]), styles["muted"]))
            for item in day.get("items") or []:
                day_parts.extend(_pdf_timeline_item(item, styles))
            story.append(KeepTogether(day_parts))
            story.append(Spacer(1, 10))
    else:
        story.append(Paragraph("No itinerary timeline is available for this option yet.", styles["body"]))

    readiness_items = option.get("readiness_items") or option.get("readiness_summary") or []
    if readiness_items:
        story.append(Spacer(1, 4))
        story.append(Paragraph("Readiness Checklist", styles["section"]))
        for item in readiness_items[:12]:
            line = (
                f"{_clean_text(item.get('title') or 'Readiness item')} "
                f"({_clean_text(item.get('priority') or 'medium')} priority, {_clean_text(item.get('status') or 'pending')})"
            )
            story.append(Paragraph(f"- {line}", styles["bullet"]))

    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "Planning note: estimates must be confirmed with the hospital, airline, hotel, insurer, and relevant authorities before booking.",
            styles["footnote"],
        )
    )
    doc.build(
        story,
        onFirstPage=lambda canvas, document: _pdf_footer(canvas, document, font_name),
        onLaterPages=lambda canvas, document: _pdf_footer(canvas, document, font_name),
    )
    return buffer.getvalue()


def _register_pdf_fonts() -> str:
    if PDF_FONT_NAME in pdfmetrics.getRegisteredFontNames():
        return PDF_FONT_NAME
    for font_path in PDF_FONT_PATHS:
        if font_path.is_file():
            pdfmetrics.registerFont(TTFont(PDF_FONT_NAME, str(font_path)))
            return PDF_FONT_NAME
    return "Helvetica"


def _pdf_styles(font_name: str) -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "MedTourTitle",
            parent=sample["Title"],
            fontName=font_name,
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#143a5a"),
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "MedTourSubtitle",
            parent=sample["BodyText"],
            fontName=font_name,
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#506070"),
        ),
        "section": ParagraphStyle(
            "MedTourSection",
            parent=sample["Heading2"],
            fontName=font_name,
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#143a5a"),
            spaceBefore=8,
            spaceAfter=8,
        ),
        "small_heading": ParagraphStyle(
            "MedTourSmallHeading",
            parent=sample["Heading3"],
            fontName=font_name,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#143a5a"),
            spaceBefore=8,
            spaceAfter=4,
        ),
        "day": ParagraphStyle(
            "MedTourDay",
            parent=sample["Heading3"],
            fontName=font_name,
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=4,
            spaceAfter=2,
        ),
        "body": ParagraphStyle("MedTourBody", parent=sample["BodyText"], fontName=font_name, fontSize=9, leading=13),
        "muted": ParagraphStyle(
            "MedTourMuted",
            parent=sample["BodyText"],
            fontName=font_name,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#697586"),
        ),
        "bullet": ParagraphStyle(
            "MedTourBullet",
            parent=sample["BodyText"],
            fontName=font_name,
            fontSize=8.5,
            leading=12,
            leftIndent=10,
            firstLineIndent=-7,
        ),
        "footnote": ParagraphStyle(
            "MedTourFootnote",
            parent=sample["BodyText"],
            fontName=font_name,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#697586"),
        ),
    }


def _pdf_key_value_table(rows: list[list[str]], styles: dict[str, ParagraphStyle]) -> Table:
    table_rows = [
        [Paragraph(_clean_text(label), styles["muted"]), Paragraph(_clean_text(value), styles["body"])]
        for label, value in rows
    ]
    return _pdf_table(table_rows, [1.45 * inch, 4.15 * inch], styles, has_header=False)


def _pdf_table(rows: list[Any], widths: list[float], styles: dict[str, ParagraphStyle], has_header: bool = True) -> Table:
    normalized_rows = []
    for row_index, row in enumerate(rows):
        normalized_row = []
        for cell in row:
            if isinstance(cell, Paragraph):
                normalized_row.append(cell)
            else:
                style = styles["small_heading"] if has_header and row_index == 0 else styles["body"]
                normalized_row.append(Paragraph(_clean_text(cell), style))
        normalized_rows.append(normalized_row)
    table = Table(normalized_rows, colWidths=widths, hAlign="LEFT")
    table_style = [
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d7e0ea")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7e0ea")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if has_header:
        table_style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf3ff")))
    table.setStyle(TableStyle(table_style))
    return table


def _pdf_timeline_item(item: dict[str, Any], styles: dict[str, ParagraphStyle]) -> list[Any]:
    time = _format_time_range(item)
    title = _clean_text(item.get("title") or "Scheduled item")
    location = _clean_text(item.get("location_name") or item.get("address") or "")
    cost = _format_money(item.get("estimated_cost")) if item.get("estimated_cost") else ""
    meta = " | ".join(part for part in [time, location, cost] if part)
    parts: list[Any] = [Paragraph(f"- {title}", styles["bullet"])]
    if meta:
        parts.append(Paragraph(meta, styles["muted"]))
    details = item.get("details") or {}
    doctor = details.get("suggested_doctor_name")
    specialty = details.get("suggested_doctor_specialty")
    if doctor or specialty:
        parts.append(Paragraph(f"Suggested doctor: {_clean_text(' - '.join(part for part in [doctor, specialty] if part))}", styles["muted"]))
    for step in (details.get("hospital_steps") or [])[:4]:
        parts.append(Paragraph(f"  - {_clean_text(step)}", styles["bullet"]))
    return parts


def _pdf_footer(canvas: Any, doc: SimpleDocTemplate, font_name: str) -> None:
    canvas.saveState()
    canvas.setFont(font_name, 7)
    canvas.setFillColor(colors.HexColor("#697586"))
    canvas.drawString(doc.leftMargin, 0.32 * inch, "MedTour AI planning export")
    canvas.drawRightString(A4[0] - doc.rightMargin, 0.32 * inch, f"Page {doc.page}")
    canvas.restoreState()


def _format_money(value: Any) -> str:
    if not value:
        return "N/A"
    if isinstance(value, dict):
        amount = value.get("amount")
        currency = value.get("currency") or _extract_money_currency(value) or "SGD"
        if amount is None:
            amount = _extract_money_amount(value)
        try:
            return f"{currency} {float(amount):,.0f}"
        except (TypeError, ValueError):
            return _clean_text(value.get("label") or value)
    if isinstance(value, (int, float)):
        return f"SGD {value:,.0f}"
    return _clean_text(value)


def _format_time_range(item: dict[str, Any]) -> str:
    start = str(item.get("start_time") or "")
    end = str(item.get("end_time") or "")
    start_time = start[11:16] if len(start) >= 16 else start
    end_time = end[11:16] if len(end) >= 16 else end
    if start_time and end_time:
        return f"{start_time} - {end_time}"
    return start_time or end_time


def _clean_text(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\s+", " ", text).strip()


@app.get("/")
def serve_index() -> FileResponse:
    return _static_file_response("index.html")


@app.get("/index.html")
def serve_index_file() -> FileResponse:
    return _static_file_response("index.html")


@app.get("/{asset_path:path}")
def serve_frontend_asset_or_spa(asset_path: str) -> FileResponse:
    if asset_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    if asset_path in STATIC_FILES:
        return _static_file_response(asset_path)
    if "." in asset_path:
        raise HTTPException(status_code=404, detail="Not Found")
    return _static_file_response("index.html")


def _static_file_response(asset_path: str) -> FileResponse:
    file_path = STATIC_FILES.get(asset_path)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(file_path)
