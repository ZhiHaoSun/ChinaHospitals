"""Hard-written Singapore care benchmarks for savings calculations."""

from __future__ import annotations

from typing import Any


SINGAPORE_MEDICAL_BUDGET_SGD: dict[str, dict[str, int]] = {
    "eye_surgery": {
        "default": 6200,
        "smile_pro": 6500,
        "lasik": 5200,
        "icl": 9000,
        "cataract": 7000,
    },
    "dental_care": {
        "default": 9000,
        "single_implant": 5500,
        "multiple_implants": 14000,
        "crown_bridge": 6500,
        "root_canal": 1800,
    },
    "health_checkup": {
        "default": 2500,
        "executive_screening": 3200,
        "cardio_screening": 2800,
        "cancer_markers": 2200,
        "women_health": 2600,
    },
    "car_t_blood_cancer": {
        "default": 350000,
        "car_t_consult": 12000,
        "b_cell_lymphoma": 360000,
        "multiple_myeloma": 380000,
        "leukemia": 390000,
    },
}


def singapore_budget_estimate_sgd(
    medical_purpose: str | None,
    procedure_subtype: str | None = None,
) -> dict[str, Any]:
    purpose = medical_purpose or "health_checkup"
    subtype = procedure_subtype or "default"
    purpose_budget = SINGAPORE_MEDICAL_BUDGET_SGD.get(purpose, SINGAPORE_MEDICAL_BUDGET_SGD["health_checkup"])
    amount = purpose_budget.get(subtype) or purpose_budget["default"]
    return {
        "amount": amount,
        "currency": "SGD",
        "source": "hard_written_singapore_budget",
        "medical_purpose": purpose,
        "procedure_subtype": subtype,
        "note": "Hard-written Singapore care benchmark used for planning savings calculation.",
    }
