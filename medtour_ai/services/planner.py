"""Deterministic backend planner used by the API service.

The ADK graph remains the production multi-agent implementation. This module
provides a runnable local backend service with the same API contracts, useful
for frontend integration, smoke tests, and fallback behavior when ADK or model
credentials are unavailable.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any
from uuid import uuid4

from medtour_ai.agents.tools import (
    audit_city_option_sources_and_costs,
    estimate_flights,
    estimate_trip_costs,
    get_alipay_international_setup,
    get_hospital_insurance_policy,
    get_hospital_visit_protocol,
    get_visa_entry_guidance,
    retrieve_medical_rules,
    search_hospital_city_candidates,
    search_hotels,
)


class LocalPlannerService:
    """Generate API-compatible medical travel plans without network calls."""

    def generate_report(self, profile_draft: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
        profile = profile_draft["profile"]
        medical_purpose = profile["medical_purpose"]
        procedure_subtype = profile.get("procedure_subtype") or "not_sure"
        departure_city = profile["departure_city"]
        nationality = profile["nationality"]
        budget_tier = profile.get("budget_tier") or "balanced"
        currency = request.get("currency", "SGD")
        max_options = min(int(request.get("max_city_options", 4)), 4)

        medical_rules = retrieve_medical_rules(medical_purpose, procedure_subtype)
        candidate_payload = search_hospital_city_candidates(
            medical_purpose=medical_purpose,
            nationality=nationality,
            departure_city=departure_city,
            budget_tier=budget_tier,
        )

        start_date = _resolve_start_date(profile)
        strategies = [
            ("best_overall", "Best Overall"),
            ("lowest_cost", "Lowest Total Cost"),
            ("shortest_trip", "Shortest Trip"),
            ("medical_strength", "Strongest Medical Resources"),
        ]
        candidates = candidate_payload["candidates"][:max_options]

        city_options = []
        for index, candidate in enumerate(candidates):
            strategy_id, label = strategies[index]
            option = self._build_city_option(
                profile=profile,
                candidate=candidate,
                medical_rules=medical_rules,
                strategy_id=strategy_id,
                recommendation_label=label,
                start_date=start_date,
                currency=currency,
            )
            city_options.append(option)

        confirmation_requests = list(profile_draft.get("confirmation_requests", []))
        if profile.get("season_flexibility") == "selected_month_only":
            confirmation_requests.append(
                {
                    "confirmation_id": f"conf_dates_{uuid4().hex[:8]}",
                    "blocking": False,
                    "question": "Should we keep only your selected month?",
                    "reason": "Allowing adjacent off-season dates may reduce flight and hotel cost.",
                    "recommended_option": "allow_adjacent_dates",
                    "options": [
                        {
                            "id": "allow_adjacent_dates",
                            "label": "Allow adjacent dates",
                            "impact": "May reduce cost while preserving medical schedule.",
                            "recommended": True,
                        },
                        {
                            "id": "selected_month_only",
                            "label": "Selected month only",
                            "impact": "Keeps your travel window strict, possibly at higher cost.",
                        },
                    ],
                    "affected_sections": ["flights", "hotels", "timeline"],
                }
            )

        return {
            "report_status": "ready",
            "profile": profile,
            "medical_rules": medical_rules,
            "city_options": city_options,
            "comparison": _comparison(city_options),
            "recommended_option_id": city_options[0]["option_id"] if city_options else None,
            "audit_summary": _audit_summary(city_options),
            "confirmation_requests": confirmation_requests,
            "disclaimers": [
                "This plan is for travel and budgeting support only and is not medical diagnosis.",
                "Procedure eligibility, final price, and appointment availability must be confirmed by the hospital or licensed clinician.",
                "Visa and entry policies can change; verify official sources before booking non-refundable travel.",
                "Insurance coverage, direct billing, and reimbursement eligibility must be confirmed by the insurer and hospital.",
            ],
            "assumptions": [
                "Flight and hotel values are planning estimates, not live booking inventory.",
                "Hotel choices are filtered for foreign-guest eligibility in the local estimate model.",
                "Medical timelines preserve pre-treatment, procedure, and follow-up hard constraints.",
                "Insurance policy guidance is estimated from hospital-level rules and requires insurer confirmation.",
                "Audit checks identify planning-only values that require official or live-source verification before booking.",
            ],
        }

    def regenerate_timeline(self, option: dict[str, Any], preferences: dict[str, Any]) -> dict[str, Any]:
        """Regenerate a selected option timeline with user preference edits."""

        new_option = dict(option)
        current_days = len(option.get("timeline", [])) or option.get("required_days", 5)
        requested_days = _duration_to_days(preferences.get("stay_length_preference"), fallback=current_days)
        tourism_intensity = preferences.get("tourism_intensity", "light")
        start = _parse_date(option.get("start_date")) or (date.today() + timedelta(days=45))

        medical_rules = {
            "typical_days": requested_days,
            "hard_constraints": option.get("medical_hard_constraints", []),
        }
        hospital_protocol = option.get("hospital_visit_protocol") or get_hospital_visit_protocol(
            option["target_hospital"],
            option.get("medical_purpose", "health_checkup"),
            option.get("procedure_subtype"),
            option.get("program_details"),
        )
        new_option["required_days"] = requested_days
        new_option["timeline"] = _build_timeline(
            city=option["city"],
            hospital=option["target_hospital"],
            start_date=start,
            days=requested_days,
            flight=option["flight"],
            hotel=option["hotel"],
            medical_rules=medical_rules,
            hospital_protocol=hospital_protocol,
            tourism_intensity=tourism_intensity,
        )

        diff_summary = []
        if requested_days != current_days:
            diff_summary.append(f"Stay length changed from {current_days} to {requested_days} days.")
        if preferences.get("flight_preference"):
            diff_summary.append(f"Flight preference applied: {preferences['flight_preference']}.")
        if preferences.get("hotel_budget_tier"):
            diff_summary.append(f"Hotel tier preference applied: {preferences['hotel_budget_tier']}.")
        if tourism_intensity != "light":
            diff_summary.append(f"Tourism intensity changed to {tourism_intensity}.")

        insurance_policy = option.get("insurance_policy")
        if insurance_policy and requested_days != current_days:
            insurance_policy = get_hospital_insurance_policy(
                option["target_hospital"],
                insurance_policy.get("current_holder"),
                insurance_policy.get("medical_purpose"),
                None,
                requested_days,
            )

        return {
            "timeline_version_id": f"tlv_{uuid4().hex}",
            "status": "ready",
            "timeline": new_option["timeline"],
            "cost_delta": {"amount": 0, "currency": "SGD", "note": "Local planner keeps estimated cost unchanged."},
            "diff_summary": diff_summary or ["Timeline regenerated with current constraints."],
            "insurance_policy": insurance_policy,
            "confirmation_requests": [],
            "assumptions": [
                "Medical hard constraints were preserved.",
                "Insurance policy was preserved unless stay length changed.",
                "Regenerated timeline should be revalidated before booking.",
            ],
        }

    def _build_city_option(
        self,
        *,
        profile: dict[str, Any],
        candidate: dict[str, Any],
        medical_rules: dict[str, Any],
        strategy_id: str,
        recommendation_label: str,
        start_date: date,
        currency: str,
    ) -> dict[str, Any]:
        city = candidate["city"]
        hospital = candidate["hospital"]
        required_days = _duration_to_days(profile.get("duration_preference"), medical_rules["typical_days"])
        if profile.get("medical_purpose") == "car_t_blood_cancer":
            required_days = max(required_days, medical_rules["typical_days"])
        nights = max(required_days - 1, 1)
        flight_payload = estimate_flights(profile["departure_city"], city, start_date.isoformat())["recommended"]
        hotel_payload = search_hotels(city, hospital, profile.get("budget_tier", "balanced"))["hotels"][0]
        costs = estimate_trip_costs(profile["medical_purpose"], city, nights, profile.get("budget_tier", "balanced"))
        visa = get_visa_entry_guidance(profile["nationality"], city, required_days)
        alipay = get_alipay_international_setup(profile.get("residence_country") or profile["nationality"])
        insurance = get_hospital_insurance_policy(
            hospital,
            profile.get("current_insurance_holder"),
            profile.get("medical_purpose"),
            profile.get("nationality"),
            required_days,
        )
        hospital_protocol = get_hospital_visit_protocol(
            hospital,
            profile["medical_purpose"],
            profile.get("procedure_subtype"),
            profile.get("program_details"),
        )
        insurance["estimated_premium"]["currency"] = currency
        total_cost = costs["total"]["amount"] + insurance["estimated_premium"]["amount"]
        estimated_net_savings = max(costs["estimated_net_savings"]["amount"] - insurance["estimated_premium"]["amount"], 0)

        flight = {
            "airline": flight_payload["airline"],
            "flight_number": flight_payload["flight_number"],
            "departure_airport": flight_payload["departure_airport"],
            "arrival_airport": flight_payload["arrival_airport"],
            "departure_time": f"{start_date.isoformat()}T{flight_payload['departure_time']}:00+08:00",
            "arrival_time": f"{start_date.isoformat()}T{flight_payload['arrival_time']}:00+08:00",
            "estimated_cost": {"amount": flight_payload["estimated_cost_sgd"], "currency": currency},
            "notes": flight_payload["notes"],
        }
        hotel = {
            "name": hotel_payload["name"],
            "address": hotel_payload["address"],
            "nightly_rate": {"amount": hotel_payload["nightly_rate_sgd"], "currency": currency},
            "nights": nights,
            "distance_to_hospital": hotel_payload["distance_to_hospital"],
            "foreign_guest_eligible": hotel_payload["foreign_guest_eligible"],
            "cancellation_policy": hotel_payload["cancellation_policy"],
        }

        option = {
            "option_id": f"opt_{city.lower()}_{strategy_id}",
            "city": city,
            "recommendation_label": recommendation_label,
            "target_hospital": hospital,
            "medical_purpose": profile["medical_purpose"],
            "procedure_subtype": profile.get("procedure_subtype"),
            "program_details": profile.get("program_details", {}),
            "recommendation_reason": _recommendation_reason(strategy_id, city, candidate),
            "required_days": required_days,
            "start_date": start_date.isoformat(),
            "flight": flight,
            "hotel": hotel,
            "timeline": _build_timeline(
                city=city,
                hospital=hospital,
                start_date=start_date,
                days=required_days,
                flight=flight,
                hotel=hotel,
                medical_rules=medical_rules,
                hospital_protocol=hospital_protocol,
                tourism_intensity=profile.get("tourism_intensity", "light"),
            ),
            "cost_breakdown": {
                "medical": _money(costs["medical"], currency),
                "flight": {"amount": flight_payload["estimated_cost_sgd"], "currency": currency},
                "hotel": _money(costs["hotel"], currency),
                "local_transport": _money(costs["local_transport"], currency),
                "meals": _money(costs["meals"], currency),
                "visa_and_payment_setup": _money(costs["visa_and_payment_setup"], currency),
                "travel_insurance": insurance["estimated_premium"],
            },
            "total_estimated_cost": {"amount": total_cost, "currency": currency},
            "estimated_net_savings": {"amount": estimated_net_savings, "currency": currency},
            "home_country_benchmark": _money(costs["home_country_benchmark"], currency),
            "visa_guidance": visa,
            "alipay_setup": alipay,
            "insurance_policy": insurance,
            "hospital_visit_protocol": hospital_protocol,
            "contact_lookup_guidance": hospital_protocol.get("contact_lookup_guidance"),
            "readiness_items": _readiness_items(visa, alipay, insurance),
            "key_risks": _key_risks(visa, medical_rules, insurance),
            "medical_hard_constraints": medical_rules.get("hard_constraints", []),
            "metadata": {
                "source": "agent_estimate",
                "source_updated_at": date.today().isoformat(),
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "confidence_level": "medium",
                "data_status": "estimated",
            },
            "confirmation_requests": [],
        }
        option["audit_report"] = audit_city_option_sources_and_costs(option)
        option["readiness_items"].append(_audit_readiness_item(option["audit_report"]))
        return option


def _build_timeline(
    *,
    city: str,
    hospital: str,
    start_date: date,
    days: int,
    flight: dict[str, Any],
    hotel: dict[str, Any],
    medical_rules: dict[str, Any],
    hospital_protocol: dict[str, Any],
    tourism_intensity: str,
) -> list[dict[str, Any]]:
    timeline = []
    for offset in range(days):
        current_date = start_date + timedelta(days=offset)
        day_no = offset + 1
        items: list[dict[str, Any]] = []

        if day_no == 1:
            items.extend(
                [
                    _item("flight", "Arrival flight", current_date, time(8, 0), time(13, 30), flight["arrival_airport"], estimated_cost=flight["estimated_cost"], details={"flight": flight}),
                    _item("transport", "Airport transfer to hotel", current_date, time(14, 0), time(15, 0), city, estimated_cost={"amount": 35, "currency": "SGD"}),
                    _item("hotel", "Hotel check-in", current_date, time(15, 30), time(16, 0), hotel["name"], address=hotel["address"], details={"hotel": hotel}),
                ]
            )
            if days <= 4:
                items.append(
                    _item(
                        "medical",
                        "International desk pre-registration email check",
                        current_date,
                        time(16, 30),
                        time(17, 15),
                        hospital,
                        hard_constraint=True,
                        details=_protocol_details(hospital_protocol, "pre_registration"),
                    )
                )
        elif day_no == 2:
            items.extend(
                [
                    _item(
                        "medical",
                        "International desk registration and outpatient file setup",
                        current_date,
                        time(8, 30),
                        time(9, 0),
                        hospital,
                        hard_constraint=True,
                        details=_protocol_details(hospital_protocol, "registration"),
                    ),
                    _item(
                        "medical",
                        "Nurse intake, consent forms, and payment/pre-auth check",
                        current_date,
                        time(9, 0),
                        time(9, 30),
                        hospital,
                        hard_constraint=True,
                        details=_protocol_details(hospital_protocol, "registration"),
                    ),
                    _item(
                        "medical",
                        "Diagnostics and program-specific tests",
                        current_date,
                        time(9, 30),
                        time(11, 30),
                        hospital,
                        hard_constraint=True,
                        details=_protocol_details(hospital_protocol, "diagnostics"),
                    ),
                    _item(
                        "medical",
                        "Suggested doctor consultation and eligibility confirmation",
                        current_date,
                        time(14, 0),
                        time(15, 30),
                        hospital,
                        hard_constraint=True,
                        details=_protocol_details(hospital_protocol, "consultation"),
                    ),
                ]
            )
        elif day_no == 3:
            items.extend(
                [
                    _item(
                        "medical",
                        "Final consent, deposit, and treatment-room preparation",
                        current_date,
                        time(8, 45),
                        time(9, 30),
                        hospital,
                        hard_constraint=True,
                        details=_protocol_details(hospital_protocol, "consultation"),
                    ),
                    _item(
                        "medical",
                        "Procedure or core medical appointment",
                        current_date,
                        time(9, 30),
                        time(12, 0),
                        hospital,
                        hard_constraint=True,
                        details=_protocol_details(hospital_protocol, "procedure"),
                    ),
                    _item(
                        "medical",
                        "Medication, discharge briefing, and claim documents",
                        current_date,
                        time(12, 0),
                        time(12, 45),
                        hospital,
                        hard_constraint=True,
                        details=_protocol_details(hospital_protocol, "discharge"),
                    ),
                    _item("hotel", "Rest window near hospital", current_date, time(14, 0), time(18, 0), hotel["name"], hard_constraint=True),
                ]
            )
        elif day_no == 4:
            items.extend(
                [
                    _item(
                        "medical",
                        "Follow-up review with assigned doctor or international clinic",
                        current_date,
                        time(9, 30),
                        time(10, 30),
                        hospital,
                        hard_constraint=True,
                        details=_protocol_details(hospital_protocol, "consultation"),
                    ),
                    _item(
                        "readiness",
                        "Confirm return fitness, invoices, and insurance documents",
                        current_date,
                        time(11, 0),
                        time(11, 30),
                        hospital,
                        details=_protocol_details(hospital_protocol, "discharge"),
                    ),
                ]
            )
            if day_no == days:
                items.extend(
                    [
                        _item("hotel", "Hotel check-out", current_date, time(11, 30), time(12, 0), hotel["name"]),
                        _item("transport", "Transfer to airport", current_date, time(13, 0), time(14, 0), city, estimated_cost={"amount": 35, "currency": "SGD"}),
                        _item("flight", "Return flight", current_date, time(16, 0), time(21, 30), flight["arrival_airport"], estimated_cost=flight["estimated_cost"]),
                    ]
                )
        elif day_no == days:
            items.extend(
                [
                    _item("hotel", "Hotel check-out", current_date, time(10, 30), time(11, 0), hotel["name"]),
                    _item("transport", "Transfer to airport", current_date, time(12, 0), time(13, 0), city, estimated_cost={"amount": 35, "currency": "SGD"}),
                    _item("flight", "Return flight", current_date, time(15, 30), time(21, 0), flight["arrival_airport"], estimated_cost=flight["estimated_cost"]),
                ]
            )
        else:
            tourism_title = "Light recovery-friendly sightseeing" if tourism_intensity == "light" else "Flexible city activity block"
            items.append(_item("tourism", tourism_title, current_date, time(10, 30), time(13, 0), city, estimated_cost={"amount": 45, "currency": "SGD"}))

        if day_no not in (days,) and day_no >= 2:
            items.append(_item("meal", "Recovery-friendly meals", current_date, time(18, 0), time(19, 0), city, estimated_cost={"amount": 45, "currency": "SGD"}))

        timeline.append(
            {
                "day": day_no,
                "date": current_date.isoformat(),
                "title": _day_title(day_no, days),
                "items": items,
            }
        )
    return timeline


def _protocol_details(protocol: dict[str, Any], step_key: str) -> dict[str, Any]:
    contact = protocol.get("registration_contact", {})
    doctor = protocol.get("suggested_doctor", {})
    contact_lookup_guidance = protocol.get("contact_lookup_guidance", {})
    service_billing = protocol.get("service_billing", {})
    return {
        "registration_desk": contact.get("desk"),
        "registration_email": contact.get("email"),
        "registration_email_status": contact.get("email_status", "needs_confirmation"),
        "appointment_phone": contact.get("appointment_phone"),
        "main_phone": contact.get("main_phone"),
        "wechat_or_portal_route": contact.get("wechat_or_portal_route"),
        "contact_source_records": contact.get("source_records", []),
        "contact_lookup_skill": contact_lookup_guidance.get("skill_name"),
        "contact_lookup_skill_path": contact_lookup_guidance.get("skill_path"),
        "contact_lookup_source_registry": contact_lookup_guidance.get("source_registry_reference"),
        "contact_lookup_seed_sources": contact_lookup_guidance.get("seed_official_sources", []),
        "contact_lookup_required_fields": contact_lookup_guidance.get("required_output_fields", []),
        "contact_lookup_audit_requirements": contact_lookup_guidance.get("audit_requirements", []),
        "service_billing": service_billing,
        "service_billing_status": service_billing.get("service_billing_status", "needs_confirmation"),
        "direct_billing_status": service_billing.get("direct_billing_status", "unknown"),
        "suggested_doctor_name": doctor.get("name"),
        "suggested_doctor_specialty": doctor.get("specialty"),
        "suggested_doctor_request": doctor.get("request_note"),
        "hospital_steps": protocol.get("in_hospital_steps", {}).get(step_key, []),
        "program_details": protocol.get("program_details", {}),
    }


def _item(
    category: str,
    title: str,
    current_date: date,
    start: time,
    end: time,
    location_name: str,
    *,
    address: str | None = None,
    estimated_cost: dict[str, Any] | None = None,
    hard_constraint: bool = False,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "item_id": f"tli_{uuid4().hex[:10]}",
        "category": category,
        "title": title,
        "start_time": f"{current_date.isoformat()}T{start.isoformat()}+08:00",
        "end_time": f"{current_date.isoformat()}T{end.isoformat()}+08:00",
        "location_name": location_name,
        "address": address,
        "estimated_cost": estimated_cost,
        "hard_constraint": hard_constraint,
        "confidence_level": "medium",
        "details": details or {},
    }


def _resolve_start_date(profile: dict[str, Any]) -> date:
    if profile.get("planned_date"):
        parsed = _parse_date(profile["planned_date"])
        if parsed:
            return parsed
    date_range = profile.get("date_range") or {}
    if date_range.get("start"):
        parsed = _parse_date(date_range["start"])
        if parsed:
            return parsed
    return date.today() + timedelta(days=45)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _duration_to_days(value: str | None, fallback: int) -> int:
    mapping = {
        "3_4_days": 4,
        "5_7_days": 6,
        "8_plus_days": 8,
        "not_sure": fallback,
    }
    return mapping.get(value or "", fallback)


def _money(payload: dict[str, Any], currency: str) -> dict[str, Any]:
    result = {"amount": payload.get("amount"), "currency": currency}
    if "low" in payload:
        result["low"] = payload["low"]
    if "high" in payload:
        result["high"] = payload["high"]
    return result


def _comparison(options: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "metrics": [
            {
                "option_id": option["option_id"],
                "city": option["city"],
                "hospital": option["target_hospital"],
                "required_days": option["required_days"],
                "medical_cost": option["cost_breakdown"]["medical"],
                "insurance_estimate": option["cost_breakdown"].get("travel_insurance"),
                "travel_cost": {
                    "amount": option["cost_breakdown"]["flight"]["amount"] + option["cost_breakdown"]["hotel"]["amount"],
                    "currency": option["total_estimated_cost"]["currency"],
                },
                "total_cost": option["total_estimated_cost"],
                "estimated_savings": option["estimated_net_savings"],
                "readiness_risk_count": len(option["key_risks"]),
                "audit_status": option.get("audit_report", {}).get("audit_status", "not_audited"),
            }
            for option in options
        ]
    }


def _audit_summary(options: list[dict[str, Any]]) -> dict[str, Any]:
    option_audits = [option.get("audit_report", {}) for option in options]
    blocking = [
        issue
        for audit in option_audits
        for issue in audit.get("blocking_issues", [])
    ]
    warnings = [
        warning
        for audit in option_audits
        for warning in audit.get("warnings", [])
    ]
    return {
        "audit_status": "needs_confirmation" if blocking else "passed_with_warnings",
        "planning_only": True,
        "option_count": len(options),
        "blocking_issue_count": len(blocking),
        "warning_count": len(warnings),
        "checks_performed": [
            "hospital_source",
            "flight_price",
            "hotel_price",
            "hotel_total_math",
            "medical_cost",
            "total_cost_math",
            "source_freshness",
            "hospital_contact_lookup_skill",
        ],
        "required_before_booking": [
            "Verify selected hospital international department and official appointment contact.",
            "Refresh flight fare from a live provider for the exact travel dates and traveler count.",
            "Refresh hotel nightly rate, taxes, cancellation terms, and foreign-guest eligibility.",
            "Confirm medical package scope, final price, eligibility, and insurance documents with the hospital.",
        ],
    }


def _readiness_items(visa: dict[str, Any], alipay: dict[str, Any], insurance: dict[str, Any]) -> list[dict[str, Any]]:
    items = [
        {
            "id": "visa_entry_status",
            "title": "Confirm visa or visa-free entry status",
            "priority": "high" if visa["requires_user_confirmation"] else "medium",
            "status": "pending",
            "steps": visa["steps"],
            "helpful_links": visa["helpful_links"],
        },
        {
            "id": "alipay_setup",
            "title": "Install and configure Alipay international version",
            "priority": "high",
            "status": "pending",
            "steps": alipay["steps"],
            "helpful_links": alipay["helpful_links"],
        },
        {
            "id": "hospital_appointment",
            "title": "Confirm hospital appointment and required documents",
            "priority": "high",
            "status": "pending",
            "steps": [
                "Confirm appointment date and department.",
                "Ask whether translator or international desk support is available.",
                "Prepare prior test reports and medication list if relevant.",
            ],
            "helpful_links": [],
        },
        {
            "id": "insurance_policy_review",
            "title": "Confirm insurance coverage and hospital claim requirements",
            "priority": "high",
            "status": "pending",
            "steps": insurance["suggestions"][:5],
            "helpful_links": insurance.get("helpful_links", []),
        },
    ]
    return items


def _audit_readiness_item(audit_report: dict[str, Any]) -> dict[str, Any]:
    blocking = audit_report.get("blocking_issues", [])
    warnings = audit_report.get("warnings", [])
    return {
        "id": "audit_source_and_cost_checks",
        "title": "Verify sources and live prices before booking",
        "priority": "high",
        "status": "pending",
        "steps": [
            "Review hospital source, international department, appointment contact, and insurance handling.",
            "Re-check flight fare for exact route, date, cabin, baggage, and refund rules.",
            "Re-check hotel nightly rate, subtotal, taxes, cancellation policy, and foreign-guest eligibility.",
            "Reconcile total estimate against itemized medical, travel, hotel, insurance, and local costs.",
            f"Resolve {len(blocking)} blocking audit items and review {len(warnings)} warnings before any non-refundable booking.",
        ],
        "helpful_links": [],
    }


def _key_risks(visa: dict[str, Any], medical_rules: dict[str, Any], insurance: dict[str, Any]) -> list[str]:
    risks = [
        "Final treatment eligibility depends on in-person clinician assessment.",
        "Flight and hotel prices are estimates until live booking confirmation.",
    ]
    if visa["requires_user_confirmation"]:
        risks.insert(0, "Visa or entry eligibility requires official confirmation.")
    if insurance.get("policy_status") == "needs_insurer_confirmation":
        risks.append("Insurance coverage and hospital billing policy require insurer confirmation before booking.")
    if medical_rules.get("required_user_confirmations"):
        risks.append("Some medical suitability details still need user confirmation.")
    return risks


def _recommendation_reason(strategy_id: str, city: str, candidate: dict[str, Any]) -> str:
    strengths = ", ".join(candidate.get("strengths", []))
    reasons = {
        "best_overall": f"{city} balances international medical service, flight access, and predictable planning.",
        "lowest_cost": f"{city} is positioned as the lower-cost candidate while keeping international patient support.",
        "shortest_trip": f"{city} supports a compact schedule with manageable transfers and hospital access.",
        "medical_strength": f"{city} is selected for stronger specialist depth and hospital reputation.",
    }
    return f"{reasons.get(strategy_id, reasons['best_overall'])} Key strengths: {strengths}."


def _day_title(day_no: int, total_days: int) -> str:
    if day_no == 1:
        return "Arrival and Check-in"
    if day_no == 2:
        return "Pre-treatment Evaluation"
    if day_no == 3:
        return "Core Medical Appointment"
    if day_no == 4:
        return "Follow-up Review"
    if day_no == total_days:
        return "Return Travel"
    return "Recovery and Light City Time"
