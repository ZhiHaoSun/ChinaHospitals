from __future__ import annotations

import asyncio
import unittest
from unittest.mock import patch

from medtour_ai.api.main import CreateReportRequest, _generate_report, _normalize_generated_report
from medtour_ai.agents.schemas import IntakeAnswers
from medtour_ai.agents.tools import (
    audit_city_option_sources_and_costs,
    estimate_trip_costs,
    get_city_cost_profile,
    get_hospital_visit_protocol,
    get_medical_process_timeline_guidance,
    lookup_china_hospital_contact_guidance,
    search_hotels,
)
from medtour_ai.services.planner import LocalPlannerService


class ReportSchemaValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.draft = {
            "profile": {
                "medical_purpose": "eye_surgery",
                "procedure_subtype": "lasik",
                "nationality": "Singapore",
                "residence_country": "Singapore",
                "departure_city": "Singapore",
                "current_insurance_holder": "AIA",
                "duration_preference": "5_7_days",
                "budget_tier": "balanced",
                "tourism_intensity": "light",
            },
            "confirmation_requests": [],
        }
        self.request = CreateReportRequest(profile_draft_id="draft_test", planner_backend="local")

    def test_local_planner_output_satisfies_generated_report_schema(self) -> None:
        raw = LocalPlannerService().generate_report(self.draft, self.request.model_dump())

        normalized = _normalize_generated_report(raw, self.draft, self.request, "report_test")

        self.assertEqual(normalized["status"], "ready")
        self.assertEqual(normalized["report_id"], "report_test")
        self.assertGreater(len(normalized["city_options"]), 0)
        first_option = normalized["city_options"][0]
        breakdown_total = sum(item["amount"] for item in first_option["cost_breakdown"].values())
        self.assertEqual(first_option["total_estimated_cost"]["amount"], breakdown_total)

    def test_city_cost_breakdowns_use_city_specific_assumptions(self) -> None:
        shanghai = estimate_trip_costs("eye_surgery", "Shanghai", nights=3, budget_tier="balanced")
        guangzhou = estimate_trip_costs("eye_surgery", "Guangzhou", nights=3, budget_tier="balanced")
        beijing_hotel = search_hotels("Beijing", "Peking Union Medical College Hospital International Medical Services")["hotels"][0]
        shenzhen_profile = get_city_cost_profile("Shenzhen")

        self.assertEqual(shanghai["hotel"]["nightly_rate"], 190)
        self.assertEqual(guangzhou["hotel"]["nightly_rate"], 145)
        self.assertGreater(shanghai["meals"]["amount"], guangzhou["meals"]["amount"])
        self.assertEqual(beijing_hotel["nightly_rate_sgd"], 185)
        self.assertEqual(shenzhen_profile["arrival_transfer_sgd"], 42)

    def test_adk_connection_error_falls_back_to_local_planner(self) -> None:
        request = CreateReportRequest(profile_draft_id="draft_test", planner_backend="adk")

        with patch("medtour_ai.api.main._get_adk_runner", side_effect=RuntimeError("OpenAIException - Connection error.")):
            raw = asyncio.run(_generate_report(self.draft, request))

        normalized = _normalize_generated_report(raw, self.draft, request, "report_fallback")

        self.assertEqual(normalized["status"], "ready")
        self.assertEqual(normalized["planner_backend"], "local")
        self.assertEqual(normalized["requested_planner_backend"], "adk")
        self.assertGreater(len(normalized["city_options"]), 0)
        self.assertTrue(any("local deterministic planner" in item for item in normalized["disclaimers"]))

    def test_adk_payload_includes_requested_language(self) -> None:
        class FakeRunner:
            def __init__(self) -> None:
                self.payload = None

            async def generate_report(self, payload: dict) -> dict:
                self.payload = payload
                return {"city_options": []}

        runner = FakeRunner()
        request = CreateReportRequest(profile_draft_id="draft_test", planner_backend="adk", language="zh-Hans")
        self.draft["profile"]["preferred_language"] = "zh-Hans"

        with patch("medtour_ai.api.main._get_adk_runner", return_value=runner):
            asyncio.run(_generate_report(self.draft, request))

        self.assertEqual(runner.payload["generation_request"]["language"], "zh-Hans")
        self.assertEqual(runner.payload["answers"]["preferred_language"], "zh-Hans")

    def test_program_details_normalizes_to_plain_string(self) -> None:
        answers = IntakeAnswers.model_validate(
            {
                "medical_purpose": "eye_surgery",
                "procedure_subtype": "lasik",
                "program_details": {
                    "current_prescription": "-4.50 both eyes",
                    "contact_lens_usage": "soft lenses",
                },
                "nationality": "Singapore",
                "departure_city": "Singapore",
            }
        )

        self.assertIsInstance(answers.program_details, str)
        self.assertEqual(
            answers.program_details,
            "current prescription: -4.50 both eyes; contact lens usage: soft lenses",
        )

    def test_missing_hotel_falls_back_before_schema_validation(self) -> None:
        raw = {
            "profile": self.draft["profile"],
            "city_options": [
                {
                    "option_id": "opt_missing_hotel",
                    "city": "Shanghai",
                    "recommendation_label": "Missing hotel fixture",
                    "target_hospital": "Hospital to confirm",
                    "required_days": 3,
                    "total_estimated_cost": {"amount": 1000, "currency": "SGD"},
                    "estimated_net_savings": {"amount": 100, "currency": "SGD"},
                    "timeline": [],
                    "cost_breakdown": {},
                    "key_risks": [],
                    "metadata": {"source": "agent_estimate"},
                }
            ],
        }

        normalized = _normalize_generated_report(raw, self.draft, self.request, "report_invalid")

        self.assertEqual(normalized["status"], "ready")
        self.assertEqual(normalized["city_options"][0]["hotel"]["name"], "Hotel to confirm")
        self.assertEqual(normalized["city_options"][0]["hotel"]["nightly_rate"]["amount"], 0)

    def test_agent_style_partial_travel_output_is_normalized_before_validation(self) -> None:
        raw = {
            "profile": self.draft["profile"],
            "confirmation_requests": ["Confirm insurance coverage with AIA."],
            "audit_summary": "Agent audit completed with confirmation blockers.",
            "city_options": [
                {
                    "option_id": "opt_agent_partial",
                    "city": "Guangzhou",
                    "recommendation_label": "Agent partial",
                    "target_hospital": "Concord Medical Center",
                    "required_days": 4,
                    "cost_breakdown": {
                        "medical": {"amount": 2500, "currency": "SGD"},
                        "flight": {"amount": 420, "currency": "SGD"},
                        "hotel": {"amount": 360, "currency": "SGD"},
                    },
                    "total_estimated_cost": {"amount": 3280, "currency": "SGD"},
                    "home_country_benchmark": {"amount": 5200, "currency": "SGD"},
                    "estimated_net_savings": {"amount": 1920, "currency": "SGD"},
                    "timeline": [
                        {
                            "day": 1,
                            "date": "2026-09-01",
                            "title": "Arrival",
                            "items": [
                                {
                                    "category": "appointment",
                                    "title": "International clinic confirmation",
                                    "confidence_level": "official",
                                    "details": "Confirm registration route before sending documents.",
                                },
                                {
                                    "category": "transport",
                                    "title": "Taxi to hotel",
                                    "details": ["Use official taxi queue."],
                                }
                            ],
                        }
                    ],
                    "insurance_policy": {
                        "direct_billing_status": "unknown",
                        "claim_documents": "Itemized invoice",
                    },
                    "audit_report": {
                        "checks": [
                            {"category": "billing", "status": "missing", "finding": "Billing route not verified."}
                        ],
                        "metadata": {"source": "agent_estimate"},
                    },
                    "readiness_items": [
                        {"title": "Confirm appointment", "priority": "urgent", "status": "todo"}
                    ],
                    "key_risks": [],
                    "metadata": {
                        "source": "official_hospital_website",
                        "confidence_level": "official",
                        "data_status": "planning_estimate",
                    },
                }
            ],
        }

        normalized = _normalize_generated_report(raw, self.draft, self.request, "report_agent_partial")

        self.assertEqual(normalized["status"], "ready")
        option = normalized["city_options"][0]
        self.assertEqual(option["flight"]["estimated_cost"]["amount"], 420)
        self.assertEqual(option["hotel"]["nightly_rate"]["amount"], 120)
        self.assertEqual(option["metadata"]["source"], "agent_estimate")
        self.assertEqual(option["metadata"]["original_source"], "official_hospital_website")
        self.assertEqual(option["timeline"][0]["items"][0]["category"], "medical")
        self.assertEqual(option["timeline"][0]["items"][0]["start_time"], "2026-09-01T09:00:00+08:00")
        self.assertEqual(option["timeline"][0]["items"][0]["end_time"], "2026-09-01T09:45:00+08:00")
        self.assertEqual(option["timeline"][0]["items"][1]["start_time"], "2026-09-01T10:00:00+08:00")
        self.assertEqual(option["timeline"][0]["items"][1]["end_time"], "2026-09-01T10:45:00+08:00")
        self.assertEqual(option["timeline"][0]["items"][0]["details"]["note"], "Confirm registration route before sending documents.")
        self.assertEqual(option["insurance_policy"]["hospital_name"], "Concord Medical Center")
        self.assertEqual(option["insurance_policy"]["hospital_policy"]["direct_billing"], "unknown")
        self.assertEqual(option["audit_report"]["checks"][0]["check_id"], "audit_check_1")
        self.assertEqual(option["audit_report"]["checks"][0]["category"], "service_billing")
        self.assertEqual(option["audit_report"]["audit_status"], "needs_confirmation")
        self.assertEqual(normalized["audit_summary"]["summary"], "Agent audit completed with confirmation blockers.")
        self.assertEqual(normalized["confirmation_requests"][0]["confirmation_id"], "conf_agent_1")
        self.assertEqual(option["readiness_items"][0]["priority"], "high")

    def test_agent_string_hotel_is_normalized_before_schema_validation(self) -> None:
        raw = {
            "profile": self.draft["profile"],
            "city_options": [
                {
                    "option_id": "opt_string_hotel",
                    "city": "Shanghai",
                    "recommendation_label": "String hotel fixture",
                    "target_hospital": "Shanghai International Medical Center",
                    "required_days": 3,
                    "flight": {"estimated_cost": {"amount": 520, "currency": "SGD"}},
                    "hotel": "Hotel near Shanghai International Medical Center to confirm",
                    "cost_breakdown": {
                        "medical": {"amount": 2800, "currency": "SGD"},
                        "flight": {"amount": 520, "currency": "SGD"},
                    },
                    "total_estimated_cost": {"amount": 3320, "currency": "SGD"},
                    "estimated_net_savings": {"amount": 1200, "currency": "SGD"},
                    "timeline": [],
                    "key_risks": [],
                    "metadata": {"source": "agent_estimate"},
                }
            ],
        }

        normalized = _normalize_generated_report(raw, self.draft, self.request, "report_string_hotel")

        self.assertEqual(normalized["status"], "ready")
        option = normalized["city_options"][0]
        self.assertEqual(option["hotel"]["name"], "Hotel near Shanghai International Medical Center to confirm")
        self.assertEqual(option["hotel"]["nightly_rate"]["amount"], 0)
        self.assertEqual(option["hotel"]["nights"], 2)

    def test_empty_timeline_day_shells_fall_back_to_itemized_timeline(self) -> None:
        raw = {
            "profile": self.draft["profile"],
            "city_options": [
                {
                    "option_id": "opt_empty_day_shells",
                    "city": "Shanghai",
                    "recommendation_label": "Empty shell fixture",
                    "target_hospital": "Shanghai International Medical Center",
                    "required_days": 2,
                    "flight": {"estimated_cost": {"amount": 520, "currency": "SGD"}},
                    "hotel": {"nightly_rate": {"amount": 165, "currency": "SGD"}, "nights": 1},
                    "timeline": [
                        {"day": 1, "date": "2026-09-01", "title": "Arrival", "items": []},
                        {"day": 2, "date": "2026-09-02", "title": "Assessment", "items": []},
                    ],
                    "cost_breakdown": {
                        "medical": {"amount": 3900, "currency": "SGD"},
                        "flight": {"amount": 520, "currency": "SGD"},
                        "hotel": {"amount": 165, "currency": "SGD"},
                    },
                    "total_estimated_cost": {"amount": 4585, "currency": "SGD"},
                    "estimated_net_savings": {"amount": 800, "currency": "SGD"},
                    "key_risks": [],
                    "metadata": {"source": "agent_estimate"},
                }
            ],
        }

        normalized = _normalize_generated_report(raw, self.draft, self.request, "report_empty_shells")

        self.assertEqual(normalized["status"], "ready")
        items = [
            item
            for day in normalized["city_options"][0]["timeline"]
            for item in day["items"]
        ]
        self.assertGreater(len(items), 0)
        self.assertTrue(any(item["category"] == "medical" for item in items))

    def test_missing_savings_uses_hard_written_singapore_budget(self) -> None:
        raw = {
            "profile": self.draft["profile"],
            "city_options": [
                {
                    "option_id": "opt_missing_savings",
                    "city": "Guangzhou",
                    "recommendation_label": "Missing savings fixture",
                    "target_hospital": "Concord Medical Center",
                    "required_days": 3,
                    "cost_breakdown": {
                        "medical": {"amount": 2500, "currency": "SGD"},
                        "flight": {"amount": 420, "currency": "SGD"},
                        "hotel": {"amount": 360, "currency": "SGD"},
                    },
                    "total_estimated_cost": {"amount": 3280, "currency": "SGD"},
                    "timeline": [
                        {
                            "day": 1,
                            "date": "2026-09-01",
                            "title": "Arrival",
                            "items": ["International registration check"],
                        }
                    ],
                    "key_risks": [],
                    "metadata": {"source": "agent_estimate"},
                }
            ],
        }

        normalized = _normalize_generated_report(raw, self.draft, self.request, "report_missing_savings")

        option = normalized["city_options"][0]
        self.assertEqual(normalized["status"], "ready")
        self.assertEqual(option["home_country_benchmark"]["amount"], 5200)
        self.assertEqual(option["home_country_benchmark"]["source"], "hard_written_singapore_budget")
        self.assertEqual(option["estimated_net_savings"]["amount"], 1920)

    def test_string_disclaimers_are_normalized_to_list(self) -> None:
        raw = {
            "profile": self.draft["profile"],
            "disclaimers": "Planning estimate only; verify directly with the hospital.",
            "assumptions": "Singapore resident paying out of pocket unless insurance confirms coverage.",
            "city_options": [
                {
                    "option_id": "opt_string_disclaimer",
                    "city": "Guangzhou",
                    "recommendation_label": "String disclaimer fixture",
                    "target_hospital": "Concord Medical Center",
                    "required_days": 3,
                    "flight": {"estimated_cost": {"amount": 420, "currency": "SGD"}},
                    "hotel": {"nightly_rate": {"amount": 120, "currency": "SGD"}, "nights": 3},
                    "cost_breakdown": {
                        "medical": {"amount": 2500, "currency": "SGD"},
                        "flight": {"amount": 420, "currency": "SGD"},
                        "hotel": {"amount": 360, "currency": "SGD"},
                    },
                    "total_estimated_cost": {"amount": 3280, "currency": "SGD"},
                    "estimated_net_savings": {"amount": 1920, "currency": "SGD"},
                    "timeline": [
                        {
                            "day": 1,
                            "date": "2026-09-01",
                            "title": "Arrival",
                            "items": ["International registration check"],
                        }
                    ],
                    "key_risks": [],
                    "metadata": {"source": "agent_estimate"},
                }
            ],
        }

        normalized = _normalize_generated_report(raw, self.draft, self.request, "report_string_disclaimer")

        self.assertEqual(normalized["status"], "ready")
        self.assertEqual(normalized["disclaimers"], ["Planning estimate only; verify directly with the hospital."])
        self.assertEqual(
            normalized["assumptions"],
            ["Singapore resident paying out of pocket unless insurance confirms coverage."],
        )

    def test_missing_insurance_policy_uses_profile_holder_for_fallback_detail(self) -> None:
        raw = {
            "profile": self.draft["profile"],
            "city_options": [
                {
                    "option_id": "opt_missing_insurance",
                    "city": "Guangzhou",
                    "recommendation_label": "Missing insurance fixture",
                    "target_hospital": "Concord Medical Center",
                    "required_days": 3,
                    "flight": {"estimated_cost": {"amount": 420, "currency": "SGD"}},
                    "hotel": {"nightly_rate": {"amount": 120, "currency": "SGD"}, "nights": 3},
                    "cost_breakdown": {
                        "medical": {"amount": 2500, "currency": "SGD"},
                        "flight": {"amount": 420, "currency": "SGD"},
                        "hotel": {"amount": 360, "currency": "SGD"},
                    },
                    "total_estimated_cost": {"amount": 3280, "currency": "SGD"},
                    "timeline": [
                        {
                            "day": 1,
                            "date": "2026-09-01",
                            "title": "Arrival",
                            "items": ["International registration check"],
                        }
                    ],
                    "key_risks": [],
                    "metadata": {"source": "agent_estimate"},
                }
            ],
        }

        normalized = _normalize_generated_report(raw, self.draft, self.request, "report_missing_insurance")

        option = normalized["city_options"][0]
        insurance = option["insurance_policy"]
        self.assertEqual(normalized["status"], "ready")
        self.assertEqual(insurance["current_holder"], "AIA")
        self.assertEqual(insurance["provider_policy"]["display_name"], "AIA")
        self.assertGreater(len(insurance["suggestions"]), 0)
        self.assertIn("travel_insurance", option["cost_breakdown"])

    def test_missing_flight_uses_representative_flight_fallback(self) -> None:
        raw = {
            "profile": self.draft["profile"],
            "city_options": [
                {
                    "option_id": "opt_missing_flight",
                    "city": "Guangzhou",
                    "recommendation_label": "Missing flight fixture",
                    "target_hospital": "Concord Medical Center",
                    "required_days": 3,
                    "hotel": {"nightly_rate": {"amount": 120, "currency": "SGD"}, "nights": 3},
                    "cost_breakdown": {
                        "medical": {"amount": 2500, "currency": "SGD"},
                        "hotel": {"amount": 360, "currency": "SGD"},
                    },
                    "total_estimated_cost": {"amount": 2860, "currency": "SGD"},
                    "timeline": [
                        {
                            "day": 1,
                            "date": "2026-09-01",
                            "title": "Arrival",
                            "items": ["International registration check"],
                        }
                    ],
                    "key_risks": [],
                    "metadata": {"source": "agent_estimate"},
                }
            ],
        }

        normalized = _normalize_generated_report(raw, self.draft, self.request, "report_missing_flight")

        option = normalized["city_options"][0]
        self.assertEqual(normalized["status"], "ready")
        self.assertEqual(option["flight"]["flight_number"], "SQ850")
        self.assertEqual(option["flight"]["departure_airport"], "SIN")
        self.assertEqual(option["flight"]["arrival_airport"], "CAN")
        self.assertEqual(option["cost_breakdown"]["flight"]["source"], "representative_flight_fallback")

    def test_timeline_object_strings_are_normalized_to_readable_text(self) -> None:
        raw = {
            "profile": self.draft["profile"],
            "city_options": [
                {
                    "option_id": "opt_structured_timeline",
                    "city": "Guangzhou",
                    "recommendation_label": "Structured timeline fixture",
                    "target_hospital": "Concord Medical Center",
                    "required_days": 2,
                    "flight": {"estimated_cost": {"amount": 420, "currency": "SGD"}},
                    "hotel": {"nightly_rate": {"amount": 120, "currency": "SGD"}, "nights": 2},
                    "cost_breakdown": {
                        "medical": {"amount": 2500, "currency": "SGD"},
                        "flight": {"amount": 420, "currency": "SGD"},
                        "hotel": {"amount": 240, "currency": "SGD"},
                    },
                    "total_estimated_cost": {"amount": 3160, "currency": "SGD"},
                    "timeline": [
                        {
                            "day": 1,
                            "date": "2026-09-01",
                            "title": "Arrival",
                            "items": [
                                {
                                    "category": "flight",
                                    "title": "{'flight_number': 'SQ850', 'arrival_time': '13:30'}",
                                    "location_name": {"arrival_airport": "CAN", "terminal": "T2"},
                                    "details": {"flight_number": "SQ850", "arrival_time": "13:30"},
                                }
                            ],
                        }
                    ],
                    "key_risks": [],
                    "metadata": {"source": "agent_estimate"},
                }
            ],
        }

        normalized = _normalize_generated_report(raw, self.draft, self.request, "report_structured_timeline")

        item = normalized["city_options"][0]["timeline"][0]["items"][0]
        self.assertEqual(normalized["status"], "ready")
        self.assertEqual(item["title"], "Flight SQ850 arrives 13:30")
        self.assertEqual(item["location_name"], "Arrival Airport: CAN · Terminal: T2")
        self.assertEqual(item["details"]["flight_number"], "SQ850")

    def test_lookup_guidance_returns_official_seed_sources_and_billing_fields(self) -> None:
        guidance = lookup_china_hospital_contact_guidance(
            "Guangdong Provincial People's Hospital International Clinic",
            city="Guangzhou",
            medical_purpose="eye_surgery",
        )

        self.assertEqual(guidance["source_registry_reference"], "skills/lookup-china-hospital-contacts/references/source-registry.md")
        self.assertGreater(len(guidance["seed_official_sources"]), 0)
        source = guidance["seed_official_sources"][0]
        self.assertEqual(source["international_department_name"], "Concord Medical Center")
        self.assertIn("service_billing", source)
        self.assertIn("source_records", source)

    def test_hospital_protocol_preserves_contact_and_billing_evidence(self) -> None:
        protocol = get_hospital_visit_protocol(
            "The University of Hong Kong-Shenzhen Hospital International Medical Center",
            "health_checkup",
        )

        contact = protocol["registration_contact"]
        self.assertEqual(contact["email_status"], "not_found")
        self.assertEqual(contact["appointment_phone"], "0755-86913388")
        self.assertEqual(protocol["service_billing"]["service_billing_status"], "needs_confirmation")
        self.assertGreater(len(protocol["source_records"]), 0)

    def test_medical_process_guidance_routes_to_split_reference_files(self) -> None:
        eye = get_medical_process_timeline_guidance("eye_surgery", "lasik")
        implant = get_medical_process_timeline_guidance("dental_care", "single_implant")
        car_t = get_medical_process_timeline_guidance("car_t_blood_cancer", "car_t_consult")
        checkup = get_medical_process_timeline_guidance("health_checkup", "executive_screening")

        self.assertEqual(eye["skill_name"], "medical-process-timeline-planner")
        self.assertEqual(eye["selected_reference_file"], "skills/medical-process-timeline-planner/references/eye-surgery.md")
        self.assertEqual(implant["selected_reference_file"], "skills/medical-process-timeline-planner/references/tooth-implant.md")
        self.assertEqual(car_t["selected_reference_file"], "skills/medical-process-timeline-planner/references/car-t.md")
        self.assertEqual(checkup["selected_reference_file"], "skills/medical-process-timeline-planner/references/premium-medical-check.md")

    def test_local_planner_timeline_preserves_medical_process_skill_reference(self) -> None:
        raw = LocalPlannerService().generate_report(self.draft, self.request.model_dump())
        option = raw["city_options"][0]
        medical_items = [
            item
            for day in option["timeline"]
            for item in day["items"]
            if item["category"] == "medical"
        ]

        self.assertEqual(option["medical_process_timeline_guidance"]["skill_name"], "medical-process-timeline-planner")
        self.assertEqual(
            option["medical_process_timeline_guidance"]["selected_reference_file"],
            "skills/medical-process-timeline-planner/references/eye-surgery.md",
        )
        self.assertTrue(any(
            item["details"].get("medical_process_reference_file")
            == "skills/medical-process-timeline-planner/references/eye-surgery.md"
            for item in medical_items
        ))

    def test_audit_flags_unverified_service_billing(self) -> None:
        raw = LocalPlannerService().generate_report(self.draft, self.request.model_dump())
        option = raw["city_options"][0]

        audit = audit_city_option_sources_and_costs(option)

        self.assertTrue(
            any(check["category"] == "service_billing" for check in audit["checks"])
        )
        self.assertTrue(
            any(check["check_id"] == "medical_process_timeline_skill" for check in audit["checks"])
        )


if __name__ == "__main__":
    unittest.main()
