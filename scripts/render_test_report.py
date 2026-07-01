"""Call local MedTour AI APIs and render a test report.

This script expects the FastAPI app to be running on http://127.0.0.1:8000.
It writes:
- reports/local_api_report.json
- reports/local_api_report.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx


BASE_URL = "http://127.0.0.1:8000"
OUT_DIR = Path("reports")
JSON_PATH = OUT_DIR / "local_api_report.json"
MD_PATH = OUT_DIR / "local_api_report.md"


TEST_INTAKE = {
    "answers": {
        "medical_purpose": "eye_surgery",
        "procedure_subtype": "smile_pro",
        "nationality": "SG",
        "residence_country": "SG",
        "departure_city": "Singapore",
        "date_mode": "range",
        "date_range": {"start": "2026-08-12", "end": "2026-08-18"},
        "duration_preference": "5_7_days",
        "season_flexibility": "depends_on_price",
        "budget_tier": "balanced",
        "traveler_count": 1,
        "hotel_preference": "near_hospital_foreign_guest_eligible",
        "tourism_intensity": "light",
    }
}


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    with httpx.Client(base_url=BASE_URL, timeout=20.0) as client:
        health = _request(client, "GET", "/api/v1/health")
        schema = _request(client, "GET", "/api/v1/intake/schema")
        draft = _request(client, "POST", "/api/v1/intake/normalize", json=TEST_INTAKE)
        report_create = _request(
            client,
            "POST",
            "/api/v1/reports",
            json={
                "profile_draft_id": draft["profile_draft_id"],
                "generation_mode": "multi_city",
                "max_city_options": 4,
                "currency": "SGD",
                "language": "en",
                "run_now": True,
                "planner_backend": "local",
            },
        )

        report_id = report_create["report_id"]
        operation_id = report_create["operation_id"]
        operation = _request(client, "GET", f"/api/v1/operations/{operation_id}")
        status = _request(client, "GET", f"/api/v1/reports/{report_id}/status")
        options = _request(client, "GET", f"/api/v1/reports/{report_id}/options")

        first_option_id = options["options"][0]["option_id"]
        selected = _request(client, "POST", f"/api/v1/reports/{report_id}/options/{first_option_id}/select")
        timeline = _request(client, "GET", f"/api/v1/reports/{report_id}/options/{first_option_id}/timeline")
        costs = _request(client, "GET", f"/api/v1/reports/{report_id}/options/{first_option_id}/costs")
        readiness = _request(client, "GET", f"/api/v1/reports/{report_id}/options/{first_option_id}/readiness")

        regenerated = _request(
            client,
            "POST",
            f"/api/v1/reports/{report_id}/options/{first_option_id}/timeline/regenerate",
            json={
                "base_timeline_version_id": timeline["timeline_version_id"],
                "preferences": {
                    "stay_length_preference": "8_plus_days",
                    "flight_preference": "avoid_red_eye",
                    "hotel_budget_tier": "balanced",
                    "tourism_intensity": "light",
                },
                "run_now": True,
                "planner_backend": "local",
            },
        )
        accepted = _request(
            client,
            "POST",
            f"/api/v1/reports/{report_id}/options/{first_option_id}/timeline/"
            f"{regenerated['timeline']['timeline_version_id']}/accept",
        )

        readiness_after_update = _request(
            client,
            "PATCH",
            f"/api/v1/reports/{report_id}/options/{first_option_id}/readiness/items/alipay_setup",
            json={"status": "complete", "note": "Installed Alipay and linked international card for test."},
        )

        confirmations = _request(client, "GET", f"/api/v1/reports/{report_id}/confirmations")
        confirmation_answer = None
        if confirmations["confirmation_requests"]:
            confirmation_id = confirmations["confirmation_requests"][0]["confirmation_id"]
            confirmation_answer = _request(
                client,
                "POST",
                f"/api/v1/reports/{report_id}/confirmations/{confirmation_id}/answer",
                json={"selected_option": "let_system_choose", "freeform_note": None},
            )

        advisor_lead = _request(
            client,
            "POST",
            f"/api/v1/reports/{report_id}/advisor/handoff",
            json={
                "selected_option_id": first_option_id,
                "contact": {
                    "name": "Test User",
                    "email": "test@example.com",
                    "phone": "+6512345678",
                },
                "preferred_language": "en",
                "consent": True,
            },
        )

    bundle = {
        "health": health,
        "schema_step_count": len(schema["steps"]),
        "draft": draft,
        "report_create": report_create,
        "operation": operation,
        "status": status,
        "options": options,
        "selected": selected,
        "timeline": timeline,
        "costs": costs,
        "readiness": readiness,
        "regenerated": regenerated,
        "accepted": accepted,
        "readiness_after_update": readiness_after_update,
        "confirmations": confirmations,
        "confirmation_answer": confirmation_answer,
        "advisor_lead": advisor_lead,
    }
    JSON_PATH.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    MD_PATH.write_text(render_markdown(bundle), encoding="utf-8")
    print(f"Wrote {JSON_PATH}")
    print(f"Wrote {MD_PATH}")
    print(f"report_id={report_id}")
    print(f"selected_option_id={first_option_id}")


def _request(client: httpx.Client, method: str, path: str, **kwargs: Any) -> Any:
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    return response.json()


def render_markdown(bundle: dict[str, Any]) -> str:
    report = bundle["report_create"]["report"]
    selected_option_id = bundle["selected"]["selected_option_id"]
    selected_option = next(option for option in report["city_options"] if option["option_id"] == selected_option_id)
    lines = [
        "# MedTour AI Local API Test Report",
        "",
        f"Report ID: `{bundle['report_create']['report_id']}`",
        f"Operation ID: `{bundle['report_create']['operation_id']}`",
        f"Status: `{bundle['status']['status']}`",
        f"Generated options: `{len(report['city_options'])}`",
        "",
        "## Test Intake",
        "",
        f"- Medical purpose: {report['profile']['medical_purpose']}",
        f"- Procedure subtype: {report['profile']['procedure_subtype']}",
        f"- Nationality: {report['profile']['nationality']}",
        f"- Departure city: {report['profile']['departure_city']}",
        f"- Date range: {report['profile']['date_range']['start']} to {report['profile']['date_range']['end']}",
        f"- Duration preference: {report['profile']['duration_preference']}",
        f"- Planner backend: local deterministic API planner",
        "",
        "## City Options",
        "",
    ]

    for option in report["city_options"]:
        lines.extend(
            [
                f"### {option['recommendation_label']}: {option['city']}",
                "",
                f"- Option ID: `{option['option_id']}`",
                f"- Hospital: {option['target_hospital']}",
                f"- Required days: {option['required_days']}",
                f"- Total estimated cost: {_money(option['total_estimated_cost'])}",
                f"- Estimated net savings: {_money(option['estimated_net_savings'])}",
                f"- Flight: {option['flight']['flight_number']} from {option['flight']['departure_airport']} "
                f"to {option['flight']['arrival_airport']}, arrives {option['flight']['arrival_time']}",
                f"- Hotel: {option['hotel']['name']}, {option['hotel']['address']}",
                f"- Nightly hotel rate: {_money(option['hotel']['nightly_rate'])} for {option['hotel']['nights']} nights",
                f"- Key risks: {'; '.join(option['key_risks'])}",
                "",
            ]
        )

    lines.extend(
        [
            "## Selected Plan Detail",
            "",
            f"Selected option: `{selected_option_id}` ({selected_option['city']})",
            "",
            "### Cost Breakdown",
            "",
        ]
    )
    for label, value in bundle["costs"]["categories"].items():
        lines.append(f"- {label.replace('_', ' ').title()}: {_money(value)}")

    lines.extend(
        [
            f"- Total: {_money(bundle['costs']['total'])}",
            "",
            "### Original Timeline",
            "",
        ]
    )
    lines.extend(_timeline_lines(bundle["timeline"]["days"]))

    lines.extend(
        [
            "",
            "### Regenerated Timeline",
            "",
            f"- New timeline version: `{bundle['regenerated']['timeline']['timeline_version_id']}`",
            f"- Accept status: `{bundle['accepted']['status']}`",
            f"- Changes: {'; '.join(bundle['regenerated']['timeline']['diff_summary'])}",
            "",
        ]
    )
    lines.extend(_timeline_lines(bundle["regenerated"]["timeline"]["timeline"]))

    lines.extend(
        [
            "",
            "## Readiness Checklist",
            "",
            f"Completion before update: {bundle['readiness']['completion_percent']}%",
            f"Updated item: `{bundle['readiness_after_update']['id']}` -> `{bundle['readiness_after_update']['status']}`",
            "",
        ]
    )
    for section in bundle["readiness"]["sections"]:
        for item in section["items"]:
            lines.extend(
                [
                    f"### {item['title']}",
                    "",
                    f"- Priority: {item['priority']}",
                    f"- Status: {item['status']}",
                    f"- Steps: {'; '.join(item['steps'])}",
                    f"- Links: {_links(item.get('helpful_links', []))}",
                    "",
                ]
            )

    if bundle["confirmations"]["confirmation_requests"]:
        lines.extend(
            [
                "## Confirmation Flow",
                "",
                f"- Pending confirmation tested: `{bundle['confirmations']['confirmation_requests'][0]['confirmation_id']}`",
                f"- Answer status: `{bundle['confirmation_answer']['status']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Advisor Handoff",
            "",
            f"- Lead ID: `{bundle['advisor_lead']['lead_id']}`",
            f"- Lead status: `{bundle['advisor_lead']['status']}`",
            "",
            "## Disclaimers",
            "",
        ]
    )
    for disclaimer in report["disclaimers"]:
        lines.append(f"- {disclaimer}")
    lines.append("")
    return "\n".join(lines)


def _timeline_lines(days: list[dict[str, Any]]) -> list[str]:
    lines = []
    for day in days:
        lines.append(f"#### Day {day['day']}: {day['title']} ({day['date']})")
        lines.append("")
        for item in day["items"]:
            cost = f", cost {_money(item['estimated_cost'])}" if item.get("estimated_cost") else ""
            hard = " [medical constraint]" if item.get("hard_constraint") else ""
            lines.append(
                f"- {item['start_time'][11:16]}-{item['end_time'][11:16]}: "
                f"{item['title']} at {item['location_name']}{cost}{hard}"
            )
        lines.append("")
    return lines


def _money(value: dict[str, Any] | None) -> str:
    if not value:
        return "N/A"
    amount = value.get("amount")
    currency = value.get("currency", "SGD")
    if value.get("low") is not None and value.get("high") is not None:
        return f"{currency} {amount:,.0f} (range {value['low']:,.0f}-{value['high']:,.0f})"
    return f"{currency} {amount:,.0f}" if isinstance(amount, (int, float)) else f"{currency} {amount}"


def _links(links: list[dict[str, str]]) -> str:
    if not links:
        return "None"
    return "; ".join(f"{link['title']} ({link['url']})" for link in links)


if __name__ == "__main__":
    main()
