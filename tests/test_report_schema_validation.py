from __future__ import annotations

import unittest

from medtour_ai.api.main import CreateReportRequest, _normalize_generated_report
from medtour_ai.agents.schemas import IntakeAnswers
from medtour_ai.agents.tools import (
    audit_city_option_sources_and_costs,
    get_hospital_visit_protocol,
    lookup_china_hospital_contact_guidance,
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

    def test_invalid_city_option_fails_schema_validation(self) -> None:
        raw = {
            "profile": self.draft["profile"],
            "city_options": [
                {
                    "option_id": "opt_invalid",
                    "city": "Shanghai",
                    "recommendation_label": "Invalid fixture",
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

        self.assertEqual(normalized["status"], "failed")
        self.assertEqual(normalized["error"]["code"], "REPORT_SCHEMA_VALIDATION_FAILED")
        self.assertTrue(
            any(error["path"].endswith(".flight") for error in normalized["error"]["validation_errors"])
        )

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

    def test_audit_flags_unverified_service_billing(self) -> None:
        raw = LocalPlannerService().generate_report(self.draft, self.request.model_dump())
        option = raw["city_options"][0]

        audit = audit_city_option_sources_and_costs(option)

        self.assertTrue(
            any(check["category"] == "service_billing" for check in audit["checks"])
        )


if __name__ == "__main__":
    unittest.main()
