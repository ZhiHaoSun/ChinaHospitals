from __future__ import annotations

import unittest

from medtour_ai.api.main import CreateReportRequest, _normalize_generated_report
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
