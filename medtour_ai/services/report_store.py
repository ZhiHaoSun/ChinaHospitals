"""In-memory report store for local development.

Production should replace this with Cloud SQL / AlloyDB, Redis status storage,
and Cloud Tasks or Pub/Sub orchestration.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class InMemoryReportStore:
    def __init__(self) -> None:
        self.profile_drafts: dict[str, dict[str, Any]] = {}
        self.reports: dict[str, dict[str, Any]] = {}
        self.operations: dict[str, dict[str, Any]] = {}
        self.advisor_leads: dict[str, dict[str, Any]] = {}

    def create_profile_draft(self, normalized: dict[str, Any]) -> dict[str, Any]:
        profile_draft_id = f"upd_{uuid4().hex}"
        draft = {
            "profile_draft_id": profile_draft_id,
            "created_at": _now(),
            **normalized,
        }
        self.profile_drafts[profile_draft_id] = draft
        return draft

    def get_profile_draft(self, profile_draft_id: str) -> dict[str, Any] | None:
        return self.profile_drafts.get(profile_draft_id)

    def create_report_operation(self, profile_draft_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        report_id = f"rep_{uuid4().hex}"
        operation_id = f"op_{uuid4().hex}"
        report = {
            "report_id": report_id,
            "profile_draft_id": profile_draft_id,
            "status": "queued",
            "selected_option_id": None,
            "city_options": [],
            "confirmation_requests": [],
            "created_at": _now(),
            "request": payload,
        }
        operation = {
            "operation_id": operation_id,
            "report_id": report_id,
            "status": "queued",
            "current_stage": "queued",
            "progress": 0,
            "created_at": _now(),
        }
        self.reports[report_id] = report
        self.operations[operation_id] = operation
        return {"report_id": report_id, "operation_id": operation_id, "status": "queued"}

    def update_operation(self, operation_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        operation = self.operations.get(operation_id)
        if not operation:
            return None
        operation.update(updates)
        operation["updated_at"] = _now()
        return operation

    def get_operation(self, operation_id: str) -> dict[str, Any] | None:
        return self.operations.get(operation_id)

    def update_report(self, report_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        report = self.reports[report_id]
        report.update(updates)
        report["updated_at"] = _now()
        return report

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        return self.reports.get(report_id)

    def get_status(self, report_id: str) -> dict[str, Any] | None:
        report = self.reports.get(report_id)
        if not report:
            return None
        status = report.get("status", "queued")
        return {
            "report_id": report_id,
            "status": status,
            "current_stage": "ready" if status == "ready" else status,
            "progress": 100 if status == "ready" else 10,
            "confirmation_requests": report.get("confirmation_requests", []),
        }

    def find_option(self, report_id: str, option_id: str) -> dict[str, Any] | None:
        report = self.get_report(report_id)
        if not report:
            return None
        for option in report.get("city_options", []):
            if option.get("option_id") == option_id:
                return option
        return None

    def select_option(self, report_id: str, option_id: str) -> dict[str, Any]:
        report = self.reports[report_id]
        for option in report.get("city_options", []):
            option["selected_as_primary"] = option.get("option_id") == option_id
        report["selected_option_id"] = option_id
        report["updated_at"] = _now()
        return report

    def update_readiness_item(
        self,
        report_id: str,
        option_id: str,
        item_id: str,
        status: str,
        note: str | None = None,
    ) -> dict[str, Any] | None:
        option = self.find_option(report_id, option_id)
        if not option:
            return None
        for item in option.get("readiness_items", []):
            if item.get("id") == item_id:
                item["status"] = status
                item["note"] = note
                item["updated_at"] = _now()
                return item
        return None

    def answer_confirmation(
        self,
        report_id: str,
        confirmation_id: str,
        selected_option: str,
        freeform_note: str | None = None,
    ) -> dict[str, Any] | None:
        report = self.reports.get(report_id)
        if not report:
            return None
        for confirmation in report.get("confirmation_requests", []):
            if confirmation.get("confirmation_id") == confirmation_id:
                confirmation["selected_option"] = selected_option
                confirmation["freeform_note"] = freeform_note
                confirmation["status"] = "answered"
                confirmation["answered_at"] = _now()
                return confirmation
        return None

    def add_timeline_version(
        self,
        report_id: str,
        option_id: str,
        timeline_version: dict[str, Any],
        *,
        accepted: bool = False,
    ) -> dict[str, Any] | None:
        option = self.find_option(report_id, option_id)
        if not option:
            return None
        versions = option.setdefault("timeline_versions", [])
        versions.append({**timeline_version, "accepted": accepted, "created_at": _now()})
        if accepted:
            option["timeline"] = timeline_version.get("timeline", option.get("timeline", []))
            option["timeline_version_id"] = timeline_version["timeline_version_id"]
        return timeline_version

    def accept_timeline_version(self, report_id: str, option_id: str, timeline_version_id: str) -> dict[str, Any] | None:
        option = self.find_option(report_id, option_id)
        if not option:
            return None
        for version in option.get("timeline_versions", []):
            is_target = version.get("timeline_version_id") == timeline_version_id
            version["accepted"] = is_target
            if is_target:
                option["timeline"] = version.get("timeline", option.get("timeline", []))
                option["timeline_version_id"] = timeline_version_id
                return version
        return None

    def create_advisor_lead(self, report_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        if report_id not in self.reports:
            return None
        lead_id = f"lead_{uuid4().hex}"
        lead = {
            "lead_id": lead_id,
            "report_id": report_id,
            "status": "new",
            "created_at": _now(),
            **payload,
        }
        self.advisor_leads[lead_id] = lead
        return lead


def _now() -> str:
    return datetime.now(UTC).isoformat()
