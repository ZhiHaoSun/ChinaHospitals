"""Tool functions exposed to ADK agents.

These functions are deterministic adapters with stable return shapes. In MVP
they return curated estimates; production implementations should call Google
Places, travel providers, exchange-rate APIs, policy sources, and the RAG
retrieval service described in tech_design.md.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from medtour_ai.agents.insurance_provider_skills import (
    list_supported_providers,
    lookup_provider_skill,
)


CITY_MEDICAL_DATA: dict[str, dict[str, Any]] = {
    "Shanghai": {
        "hospital": "Shanghai International Medical Center",
        "strengths": ["international service", "ophthalmology", "premium checkup"],
        "medical_cost_sgd": {"eye_surgery": (4200, 6800), "dental_care": (3500, 9000), "health_checkup": (900, 2600)},
        "airport": "PVG",
        "registration_contact": {
            "desk": "International patient registration desk",
            "email": "Confirm official email with hospital before sending records",
            "email_status": "needs_confirmation",
        },
    },
    "Guangzhou": {
        "hospital": "Guangdong Provincial People's Hospital International Clinic",
        "strengths": ["value", "direct flights", "dental"],
        "medical_cost_sgd": {"eye_surgery": (3300, 5600), "dental_care": (2800, 7800), "health_checkup": (700, 2100)},
        "airport": "CAN",
        "registration_contact": {
            "desk": "International clinic registration desk",
            "email": "Confirm official email with hospital before sending records",
            "email_status": "needs_confirmation",
        },
    },
    "Beijing": {
        "hospital": "Peking Union Medical College Hospital International Medical Services",
        "strengths": ["complex cases", "top-tier specialists", "health checkup"],
        "medical_cost_sgd": {"eye_surgery": (4300, 7200), "dental_care": (3800, 9800), "health_checkup": (1100, 3200)},
        "airport": "PEK",
        "registration_contact": {
            "desk": "International Medical Services appointment and registration desk",
            "email": "Confirm official email with hospital before sending records",
            "email_status": "needs_confirmation",
        },
    },
    "Shenzhen": {
        "hospital": "University of Hong Kong-Shenzhen Hospital International Medical Center",
        "strengths": ["short trip", "Hong Kong access", "consumer medical care"],
        "medical_cost_sgd": {"eye_surgery": (3600, 5900), "dental_care": (3000, 8200), "health_checkup": (800, 2300)},
        "airport": "SZX",
        "registration_contact": {
            "desk": "International Medical Center registration desk",
            "email": "Confirm official email with hospital before sending records",
            "email_status": "needs_confirmation",
        },
    },
}

HOSPITAL_INSURANCE_POLICIES: dict[str, dict[str, Any]] = {
    "Shanghai International Medical Center": {
        "direct_billing": "Limited international direct billing may be available only after insurer pre-authorization.",
        "preauthorization_required": True,
        "claim_documents": ["itemized invoice", "diagnosis certificate", "doctor report", "payment receipt"],
        "common_exclusions": ["elective procedures without medical necessity", "pre-existing condition exclusions", "routine travel disruption without medical rider"],
    },
    "Guangdong Provincial People's Hospital International Clinic": {
        "direct_billing": "Most overseas patients should expect self-pay first and submit reimbursement after discharge.",
        "preauthorization_required": True,
        "claim_documents": ["itemized invoice", "outpatient record", "payment receipt", "translated medical summary if requested"],
        "common_exclusions": ["cosmetic or elective care", "unapproved outpatient procedures", "missing referral or pre-authorization"],
    },
    "Peking Union Medical College Hospital International Medical Services": {
        "direct_billing": "International service desk may support insurer coordination, but written guarantee of payment is usually needed.",
        "preauthorization_required": True,
        "claim_documents": ["guarantee of payment if available", "itemized invoice", "medical report", "prescription list"],
        "common_exclusions": ["experimental treatment", "non-emergency overseas care without approval", "pre-existing conditions"],
    },
    "University of Hong Kong-Shenzhen Hospital International Medical Center": {
        "direct_billing": "Check whether the policy covers Mainland China care separately from Hong Kong network benefits.",
        "preauthorization_required": True,
        "claim_documents": ["itemized invoice", "medical certificate", "payment receipt", "cross-border care authorization"],
        "common_exclusions": ["network-only policies", "elective care outside approved territory", "follow-up visits not authorized"],
    },
}


def retrieve_medical_rules(medical_purpose: str, procedure_subtype: str | None = None) -> dict[str, Any]:
    """Return planning rules for a medical purpose.

    Production: replace this with a RAG retrieval call over pgvector chunks.
    """

    subtype = procedure_subtype or "not_sure"
    rules = {
        "eye_surgery": {
            "typical_days": 5,
            "hard_constraints": [
                "Pre-op eye exam must happen before surgery.",
                "Follow-up review should happen the day after surgery.",
                "Avoid red-eye arrival immediately before examination.",
                "Avoid intense sightseeing, swimming, and long screen sessions after surgery.",
            ],
            "required_user_confirmations": ["recent_eye_power", "contact_lens_usage"],
        },
        "dental_care": {
            "typical_days": 7,
            "hard_constraints": [
                "Implant and crown work may require multiple visits.",
                "Final feasibility depends on dentist review and imaging.",
                "Soft-food planning is recommended after invasive procedures.",
            ],
            "required_user_confirmations": ["single_or_multiple_teeth", "has_recent_xray"],
        },
        "health_checkup": {
            "typical_days": 4,
            "hard_constraints": [
                "Fasting is usually required before morning blood tests.",
                "Some scans may require separate scheduling windows.",
            ],
            "required_user_confirmations": ["screening_focus", "existing_conditions"],
        },
        "medical_aesthetics": {
            "typical_days": 6,
            "hard_constraints": [
                "Avoid aggressive tourism immediately after procedures.",
                "Procedure suitability requires in-person clinician review.",
            ],
            "required_user_confirmations": ["procedure_area", "downtime_tolerance"],
        },
    }
    selected = rules.get(medical_purpose, rules["health_checkup"])
    return {"medical_purpose": medical_purpose, "procedure_subtype": subtype, **selected}


def search_hospital_city_candidates(
    medical_purpose: str,
    nationality: str,
    departure_city: str,
    budget_tier: str = "balanced",
) -> dict[str, Any]:
    """Return candidate China cities with hospital and strength metadata."""

    candidates = []
    for city, data in CITY_MEDICAL_DATA.items():
        cost_range = data["medical_cost_sgd"].get(medical_purpose, (1000, 3000))
        candidates.append(
            {
                "city": city,
                "hospital": data["hospital"],
                "airport": data["airport"],
                "strengths": data["strengths"],
                "medical_cost_sgd_range": {"low": cost_range[0], "high": cost_range[1]},
                "supports_international_patients": True,
                "budget_fit": budget_tier,
                "departure_city": departure_city,
                "nationality": nationality,
                "insurance_policy_hint": {
                    "direct_billing": HOSPITAL_INSURANCE_POLICIES.get(data["hospital"], {}).get(
                        "direct_billing",
                        "Confirm hospital direct billing before booking.",
                    ),
                    "preauthorization_required": HOSPITAL_INSURANCE_POLICIES.get(data["hospital"], {}).get(
                        "preauthorization_required",
                        True,
                    ),
                },
            }
        )
    return {"candidates": candidates}


def get_hospital_visit_protocol(
    hospital_name: str,
    medical_purpose: str,
    procedure_subtype: str | None = None,
    program_details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return detailed in-hospital visit steps for timeline generation.

    Production should replace provisional contacts with verified hospital
    directory/RAG data and never invent clinician names or registration emails.
    """

    data = next(
        (city_data for city_data in CITY_MEDICAL_DATA.values() if city_data["hospital"] == hospital_name),
        {},
    )
    contact = data.get(
        "registration_contact",
        {
            "desk": "International patient registration desk",
            "email": "Confirm official email with hospital before sending records",
            "email_status": "needs_confirmation",
        },
    )
    subtype = procedure_subtype or "not_sure"
    details = program_details or {}
    doctor_by_purpose = {
        "eye_surgery": {
            "name": "To be assigned by the international clinic",
            "specialty": "Ophthalmology / refractive surgery",
            "request_note": "Request a senior refractive-surgery consultant; confirm the named doctor in the appointment reply.",
        },
        "dental_care": {
            "name": "To be assigned by the international clinic",
            "specialty": "Oral implantology / restorative dentistry",
            "request_note": "Request a senior implantology or restorative dentistry consultant based on X-ray/CBCT review.",
        },
        "health_checkup": {
            "name": "To be assigned by the international clinic",
            "specialty": "Health management / internal medicine",
            "request_note": "Request a physician reviewer for the chosen screening package and existing conditions.",
        },
        "medical_aesthetics": {
            "name": "To be assigned by the international clinic",
            "specialty": "Dermatology / aesthetic medicine",
            "request_note": "Request a licensed specialist for the treatment area and downtime tolerance.",
        },
    }
    diagnostic_titles = {
        "eye_surgery": "Vision testing, corneal scan, eye-pressure check, and dilation if required",
        "dental_care": "Oral exam, panoramic X-ray/CBCT review, bite assessment, and treatment staging",
        "health_checkup": "Fasting blood draw, imaging, ECG, ultrasound, and package-specific screening",
        "medical_aesthetics": "Skin/area assessment, contraindication screening, photography consent, and treatment design",
    }
    procedure_titles = {
        "eye_surgery": f"{subtype.replace('_', ' ').title()} procedure window or final ophthalmology treatment",
        "dental_care": f"{subtype.replace('_', ' ').title()} treatment session or first-stage dental procedure",
        "health_checkup": "Doctor report review, abnormal-result triage, and follow-up test coordination",
        "medical_aesthetics": f"{subtype.replace('_', ' ').title()} treatment session with post-care briefing",
    }
    return {
        "hospital_name": hospital_name,
        "medical_purpose": medical_purpose,
        "procedure_subtype": subtype,
        "registration_contact": contact,
        "suggested_doctor": doctor_by_purpose.get(medical_purpose, doctor_by_purpose["health_checkup"]),
        "program_details": details,
        "in_hospital_steps": {
            "pre_registration": [
                "Email the international desk with passport name, preferred date, medical purpose, subtype, and insurance holder.",
                "Attach prior reports, medication list, and relevant images or prescriptions only after confirming the official email.",
                "Ask for appointment confirmation, deposit requirement, interpreter availability, and doctor assignment.",
            ],
            "registration": [
                "Show passport, appointment confirmation, insurance card or guarantee-of-payment letter, and payment method.",
                "Create or retrieve outpatient profile, sign consent/privacy forms, and confirm invoice name for claims.",
            ],
            "diagnostics": [diagnostic_titles.get(medical_purpose, diagnostic_titles["health_checkup"])],
            "consultation": [
                "Review results with suggested doctor or assigned specialist.",
                "Confirm eligibility, alternatives, risks, final price, and whether treatment can proceed on the planned day.",
            ],
            "procedure": [procedure_titles.get(medical_purpose, procedure_titles["health_checkup"])],
            "discharge": [
                "Collect doctor report, diagnosis certificate, itemized invoice, prescriptions, receipts, and follow-up instructions.",
                "Confirm emergency contact route and whether remote follow-up is available after return travel.",
            ],
        },
        "metadata": {
            "source": "agent_estimate",
            "source_updated_at": date.today().isoformat(),
            "confidence_level": "medium",
            "data_status": "needs_confirmation",
        },
    }


def estimate_flights(departure_city: str, destination_city: str, date_hint: str | None = None) -> dict[str, Any]:
    """Return representative flight choices for planning estimates."""

    airport = CITY_MEDICAL_DATA.get(destination_city, CITY_MEDICAL_DATA["Shanghai"])["airport"]
    flight_numbers = {
        "Shanghai": "SQ830",
        "Guangzhou": "SQ850",
        "Beijing": "SQ802",
        "Shenzhen": "ZH9024",
    }
    base_prices = {"Shanghai": 520, "Guangzhou": 430, "Beijing": 610, "Shenzhen": 460}
    return {
        "date_hint": date_hint,
        "recommended": {
            "airline": "Singapore Airlines" if departure_city.lower().startswith("singapore") else "Full-service carrier",
            "flight_number": flight_numbers.get(destination_city, "TBD"),
            "departure_airport": "SIN" if departure_city.lower().startswith("singapore") else departure_city,
            "arrival_airport": airport,
            "departure_time": "08:00",
            "arrival_time": "13:30",
            "estimated_cost_sgd": base_prices.get(destination_city, 500),
            "notes": "Representative planning estimate; confirm live fare before booking.",
        }
    }


def search_hotels(destination_city: str, hospital_name: str, budget_tier: str = "balanced") -> dict[str, Any]:
    """Return foreigner-friendly hotel estimates near the hospital."""

    nightly = {"budget": 95, "balanced": 165, "premium": 310}.get(budget_tier, 165)
    addresses = {
        "Shanghai": "No. 1188 Fangdian Road, Pudong, Shanghai",
        "Guangzhou": "No. 106 Zhongshan 2nd Road, Yuexiu, Guangzhou",
        "Beijing": "No. 1 Shuaifuyuan, Dongcheng, Beijing",
        "Shenzhen": "No. 1 Haiyuan 1st Road, Futian, Shenzhen",
    }
    return {
        "city": destination_city,
        "hospital_name": hospital_name,
        "hotels": [
            {
                "name": f"{destination_city} Medical District Hotel",
                "address": addresses.get(destination_city, "Central medical district"),
                "nightly_rate_sgd": nightly,
                "distance_to_hospital": "10-20 min by car",
                "foreign_guest_eligible": True,
                "cancellation_policy": "Free cancellation until 48 hours before check-in",
            }
        ],
    }


def estimate_trip_costs(
    medical_purpose: str,
    destination_city: str,
    nights: int,
    budget_tier: str = "balanced",
) -> dict[str, Any]:
    """Return itemized cost estimates in SGD."""

    data = CITY_MEDICAL_DATA.get(destination_city, CITY_MEDICAL_DATA["Shanghai"])
    medical_low, medical_high = data["medical_cost_sgd"].get(medical_purpose, (1000, 3000))
    hotel_rate = {"budget": 95, "balanced": 165, "premium": 310}.get(budget_tier, 165)
    local_transport = 120 + nights * 18
    meals = nights * 45
    visa_and_payment = 80
    medical_mid = round((medical_low + medical_high) / 2)
    total = medical_mid + hotel_rate * nights + local_transport + meals + visa_and_payment
    home_benchmark = round(total * 1.38)
    return {
        "currency": "SGD",
        "medical": {"low": medical_low, "high": medical_high, "amount": medical_mid},
        "hotel": {"amount": hotel_rate * nights, "nightly_rate": hotel_rate, "nights": nights},
        "local_transport": {"amount": local_transport},
        "meals": {"amount": meals},
        "visa_and_payment_setup": {"amount": visa_and_payment},
        "total": {"amount": total},
        "home_country_benchmark": {"amount": home_benchmark},
        "estimated_net_savings": {"amount": home_benchmark - total},
    }


def get_visa_entry_guidance(nationality: str, destination_city: str, stay_days: int) -> dict[str, Any]:
    """Return visa and entry planning guidance.

    Production must validate this against official sources during ingestion.
    """

    visa_free_candidates = {"SG", "MY", "TH", "FR", "DE", "IT", "NL", "ES"}
    likely_visa_free = nationality.upper() in visa_free_candidates and stay_days <= 15
    return {
        "nationality": nationality.upper(),
        "destination_city": destination_city,
        "stay_days": stay_days,
        "status": "likely_visa_free" if likely_visa_free else "needs_visa_or_confirmation",
        "steps": [
            "Check the latest Chinese embassy or consulate entry policy for your passport.",
            "Confirm passport validity, blank visa pages, and onward/return ticket requirements.",
            "Prepare hotel booking, hospital appointment proof, and travel insurance documents.",
            "Do not book non-refundable travel until entry status and medical appointment are confirmed.",
        ],
        "helpful_links": [
            {
                "title": "Chinese Visa Application Service Center",
                "url": "https://www.visaforchina.cn/",
            },
            {
                "title": "National Immigration Administration of China",
                "url": "https://en.nia.gov.cn/",
            },
        ],
        "requires_user_confirmation": not likely_visa_free,
    }


def get_alipay_international_setup(country_or_region: str) -> dict[str, Any]:
    """Return Alipay international setup checklist."""

    return {
        "country_or_region": country_or_region,
        "steps": [
            "Install Alipay from the iOS App Store or Google Play before departure.",
            "Register with the same mobile number you will use while traveling.",
            "Link an international Visa, Mastercard, JCB, Diners Club, Discover, or supported card.",
            "Complete identity verification if prompted.",
            "Enable location and notifications for smoother merchant payments.",
            "Bring a backup card and some cash because not every merchant supports foreign cards.",
        ],
        "helpful_links": [
            {
                "title": "Alipay international user guide",
                "url": "https://render.alipay.com/p/yuyan/180020010001196791/index.html",
            },
            {
                "title": "Alipay TourCard and payment help",
                "url": "https://www.alipayplus.com/",
            },
        ],
    }


def get_hospital_insurance_policy(
    hospital_name: str,
    current_insurance_holder: str | None = None,
    medical_purpose: str | None = None,
    nationality: str | None = None,
    stay_days: int | None = None,
) -> dict[str, Any]:
    """Return hospital-specific insurance review guidance.

    Production should replace this with a policy/RAG lookup plus insurer API or
    advisor verification. The result is planning guidance, not coverage advice.
    """

    policy = HOSPITAL_INSURANCE_POLICIES.get(
        hospital_name,
        {
            "direct_billing": "Direct billing is unknown; assume self-pay first until the hospital confirms otherwise.",
            "preauthorization_required": True,
            "claim_documents": ["itemized invoice", "doctor report", "payment receipt"],
            "common_exclusions": ["elective care", "pre-existing conditions", "missing pre-authorization"],
        },
    )
    holder = (current_insurance_holder or "").strip()
    provider_skill = lookup_provider_skill(holder)
    estimated_premium = 95 if (stay_days or 0) <= 7 else 135
    if nationality and nationality.upper() == "US":
        estimated_premium += 35
    if medical_purpose in {"medical_aesthetics", "dental_care"}:
        estimated_premium += 20

    suggestions = [
        "Ask your insurer whether planned overseas treatment in Mainland China is covered before booking.",
        "Request written pre-authorization or guarantee-of-payment instructions for the selected hospital.",
        "Confirm whether outpatient treatment, follow-up visits, and complications are covered.",
        "Keep itemized invoices, medical reports, prescriptions, receipts, and discharge or visit summaries.",
        "Buy a separate travel medical policy if your current policy excludes planned treatment abroad.",
    ]
    provider_questions = [
        f"Ask {provider_skill['display_name']}: {question}"
        for question in provider_skill.get("preauthorization_questions", [])[:4]
    ]
    if holder:
        suggestions.insert(0, f"Contact {holder} with the hospital name and procedure estimate to confirm coverage.")
    else:
        suggestions.insert(0, "Add your current insurance holder so the advisor can check policy-specific requirements.")
    suggestions.extend(provider_questions)

    return {
        "current_holder": holder or None,
        "hospital_name": hospital_name,
        "medical_purpose": medical_purpose,
        "policy_status": "needs_insurer_confirmation",
        "summary": f"{hospital_name} insurance handling should be confirmed before booking; assume pre-authorization is required.",
        "hospital_policy": policy,
        "provider_policy": {
            "provider_key": provider_skill["provider_key"],
            "display_name": provider_skill["display_name"],
            "matched": provider_skill["matched"],
            "policy_lookup_focus": provider_skill["policy_lookup_focus"],
            "direct_billing_assumption": provider_skill["direct_billing_assumption"],
            "preauthorization_questions": provider_skill["preauthorization_questions"],
            "claim_documents": provider_skill["claim_documents"],
            "risk_flags": provider_skill["risk_flags"],
            "agent_notes": provider_skill["agent_notes"],
        },
        "estimated_premium": {"amount": estimated_premium, "currency": "SGD"},
        "suggestions": suggestions,
        "helpful_links": provider_skill.get("helpful_links", []),
        "metadata": {
            "source": "agent_estimate",
            "source_updated_at": date.today().isoformat(),
            "confidence_level": "medium",
            "data_status": "needs_confirmation",
        },
    }


def lookup_insurance_provider_policy(provider_name: str | None = None) -> dict[str, Any]:
    """Return provider-specific lookup guidance for common insurers.

    Use this with the user's current insurance holder before making
    assumptions about China hospital direct billing or reimbursement.
    """

    return {
        "provider_name": provider_name,
        "provider_skill": lookup_provider_skill(provider_name),
        "supported_providers": list_supported_providers(),
    }


def get_today() -> str:
    """Return current local date for prompts that need a planning anchor."""

    return date.today().isoformat()
