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
        "strengths": ["international service", "ophthalmology", "premium checkup", "hematology referral"],
        "medical_cost_sgd": {
            "eye_surgery": (3200, 4600),
            "dental_care": (3500, 9000),
            "health_checkup": (900, 2600),
            "car_t_blood_cancer": (115000, 165000),
        },
        "airport": "PVG",
        "registration_contact": {
            "desk": "International patient registration desk",
            "email": "international.appointments@shanghai-imc.example.cn",
            "email_status": "sample_contact_verify_with_hospital",
        },
    },
    "Guangzhou": {
        "hospital": "Guangdong Provincial People's Hospital International Clinic",
        "strengths": ["value", "direct flights", "dental", "hematology"],
        "medical_cost_sgd": {
            "eye_surgery": (2800, 4200),
            "dental_care": (2800, 7800),
            "health_checkup": (700, 2100),
            "car_t_blood_cancer": (98000, 145000),
        },
        "airport": "CAN",
        "registration_contact": {
            "desk": "International clinic registration desk",
            "email": "internationalclinic@gdph.example.cn",
            "email_status": "sample_contact_verify_with_hospital",
        },
    },
    "Beijing": {
        "hospital": "Peking Union Medical College Hospital International Medical Services",
        "strengths": ["complex cases", "top-tier specialists", "health checkup", "hematology oncology"],
        "medical_cost_sgd": {
            "eye_surgery": (3500, 5000),
            "dental_care": (3800, 9800),
            "health_checkup": (1100, 3200),
            "car_t_blood_cancer": (125000, 180000),
        },
        "airport": "PEK",
        "registration_contact": {
            "desk": "International Medical Services appointment and registration desk",
            "email": "ims.appointment@pumch.example.cn",
            "email_status": "sample_contact_verify_with_hospital",
        },
    },
    "Shenzhen": {
        "hospital": "University of Hong Kong-Shenzhen Hospital International Medical Center",
        "strengths": ["short trip", "Hong Kong access", "consumer medical care", "cross-border oncology review"],
        "medical_cost_sgd": {
            "eye_surgery": (3000, 4400),
            "dental_care": (3000, 8200),
            "health_checkup": (800, 2300),
            "car_t_blood_cancer": (105000, 155000),
        },
        "airport": "SZX",
        "registration_contact": {
            "desk": "International Medical Center registration desk",
            "email": "imc.appointments@hku-szh.example.cn",
            "email_status": "sample_contact_verify_with_hospital",
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
        "car_t_blood_cancer": {
            "typical_days": 28,
            "hard_constraints": [
                "CAR-T eligibility requires hematology-oncology review and prior treatment records.",
                "Leukapheresis, cell manufacturing, lymphodepletion, infusion, and monitoring may happen across separate windows.",
                "Cytokine release syndrome and neurotoxicity monitoring plans must be confirmed before treatment.",
                "A caregiver, translation support, and emergency contact pathway are strongly recommended.",
            ],
            "required_user_confirmations": ["diagnosis", "prior_treatments", "recent_labs_and_imaging", "caregiver_plan"],
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
            "email": "international.appointments@example-hospital.cn",
            "email_status": "sample_contact_verify_with_hospital",
        },
    )
    subtype = procedure_subtype or "not_sure"
    details = program_details or {}
    doctor_by_purpose = {
        "eye_surgery": {
            "name": "Dr. Li Xiaoran",
            "specialty": "Cornea and refractive surgery consultant",
            "request_note": "Request the international clinic to confirm Dr. Li Xiaoran or assign an equivalent senior refractive-surgery consultant before deposit payment.",
        },
        "dental_care": {
            "name": "Dr. Zhou Wenhao",
            "specialty": "Oral implantology and restorative dentistry consultant",
            "request_note": "Request the international clinic to confirm Dr. Zhou Wenhao or assign an equivalent senior implantology consultant after X-ray/CBCT review.",
        },
        "health_checkup": {
            "name": "Dr. Wang Meilin",
            "specialty": "Health management and internal medicine reviewer",
            "request_note": "Request the international clinic to confirm Dr. Wang Meilin or assign an equivalent physician reviewer for the chosen screening package.",
        },
        "car_t_blood_cancer": {
            "name": "Dr. Chen Rui",
            "specialty": "Hematology-oncology and cellular therapy consultant",
            "request_note": "Request the international clinic to confirm a hematology-oncology consultant experienced with CAR-T eligibility review before sending deposits or original records.",
        },
    }
    diagnostic_titles = {
        "eye_surgery": "Vision testing, corneal scan, eye-pressure check, and dilation if required",
        "dental_care": "Oral exam, panoramic X-ray/CBCT review, bite assessment, and treatment staging",
        "health_checkup": "Fasting blood draw, imaging, ECG, ultrasound, and package-specific screening",
        "car_t_blood_cancer": "Hematology-oncology consult, pathology review, bone marrow/flow cytometry review, infectious disease screening, and CAR-T eligibility assessment",
    }
    procedure_titles = {
        "eye_surgery": f"{subtype.replace('_', ' ').title()} procedure window or final ophthalmology treatment",
        "dental_care": f"{subtype.replace('_', ' ').title()} treatment session or first-stage dental procedure",
        "health_checkup": "Doctor report review, abnormal-result triage, and follow-up test coordination",
        "car_t_blood_cancer": f"{subtype.replace('_', ' ').title()} planning: leukapheresis, bridging therapy review, lymphodepletion, infusion, and inpatient monitoring",
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
    if medical_purpose == "car_t_blood_cancer":
        home_benchmark = round(medical_mid * 2.7 + (total - medical_mid))
    elif medical_purpose == "eye_surgery":
        home_benchmark = round(max(total + 850, medical_mid * 1.58))
    else:
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


def audit_city_option_sources_and_costs(option: dict[str, Any]) -> dict[str, Any]:
    """Audit one generated city option for source coverage and cost reasonableness.

    This is a deterministic safety rail for the multi-agent flow. It does not
    replace live provider verification, but it forces every generated option to
    expose which hospital, flight, hotel, and cost claims still need checking.
    """

    city = str(option.get("city") or "").strip()
    hospital = str(option.get("target_hospital") or option.get("hospital") or "").strip()
    flight = option.get("flight") or {}
    hotel = option.get("hotel") or {}
    cost_breakdown = option.get("cost_breakdown") or {}
    total_cost = option.get("total_estimated_cost") or {}
    metadata = option.get("metadata") or {}

    checks: list[dict[str, Any]] = []

    def add_check(
        check_id: str,
        category: str,
        status: str,
        finding: str,
        evidence: list[str],
        suggested_action: str,
    ) -> None:
        checks.append(
            {
                "check_id": check_id,
                "category": category,
                "status": status,
                "finding": finding,
                "evidence": evidence,
                "suggested_action": suggested_action,
            }
        )

    known_hospital = any(data["hospital"] == hospital for data in CITY_MEDICAL_DATA.values())
    if known_hospital:
        add_check(
            "hospital_source",
            "hospital_source",
            "warn",
            "Hospital appears in curated planning data, but official hospital source verification is still required.",
            [hospital, f"city={city}", "source=curated_mvp_dataset"],
            "Verify the international department, appointment desk, foreign-patient policy, and official contact details against the hospital website or RAG source before booking.",
        )
    else:
        add_check(
            "hospital_source",
            "hospital_source",
            "needs_confirmation",
            "Selected hospital was not matched to the curated hospital dataset.",
            [hospital or "missing_hospital", f"city={city or 'missing_city'}"],
            "Retrieve official hospital source data before presenting this option as bookable.",
        )

    expected_flight = {"Shanghai": 520, "Guangzhou": 430, "Beijing": 610, "Shenzhen": 460}.get(city)
    flight_amount = _amount(flight.get("estimated_cost"))
    if flight_amount is None:
        add_check(
            "flight_price",
            "flight_price",
            "needs_confirmation",
            "Flight estimate is missing a numeric amount.",
            [str(flight)],
            "Refresh flight pricing from a live flight provider and include fare timestamp, cabin, baggage, and refund constraints.",
        )
    elif expected_flight and expected_flight * 0.55 <= flight_amount <= expected_flight * 1.75:
        add_check(
            "flight_price",
            "flight_price",
            "pass",
            "Flight estimate is within the expected representative planning range.",
            [f"estimated={flight_amount}", f"representative_baseline={expected_flight}", "source=agent_estimate"],
            "Confirm live fare before booking and mark source as external_api when refreshed.",
        )
    else:
        add_check(
            "flight_price",
            "flight_price",
            "warn",
            "Flight estimate is outside the representative planning range or no route baseline exists.",
            [f"estimated={flight_amount}", f"representative_baseline={expected_flight or 'none'}"],
            "Re-check the flight provider quote, date, route, baggage, and traveler count.",
        )

    nightly_rate = _amount(hotel.get("nightly_rate"))
    nights = int(hotel.get("nights") or 0)
    hotel_total = _amount(cost_breakdown.get("hotel"))
    if nightly_rate is None:
        add_check(
            "hotel_price",
            "hotel_price",
            "needs_confirmation",
            "Hotel nightly rate is missing a numeric amount.",
            [str(hotel)],
            "Refresh hotel pricing from a hotel provider and include foreign-guest eligibility and cancellation policy.",
        )
    elif 60 <= nightly_rate <= 450:
        add_check(
            "hotel_price",
            "hotel_price",
            "pass",
            "Hotel nightly estimate is within the expected foreigner-friendly planning range.",
            [f"nightly_rate={nightly_rate}", f"nights={nights}", "source=agent_estimate"],
            "Confirm live nightly rate, taxes, deposit rules, and foreign-guest eligibility before booking.",
        )
    else:
        add_check(
            "hotel_price",
            "hotel_price",
            "warn",
            "Hotel nightly estimate is outside the expected planning range.",
            [f"nightly_rate={nightly_rate}", f"nights={nights}"],
            "Re-check hotel tier, medical-district distance, and booking inventory.",
        )
    if nightly_rate is not None and nights and hotel_total is not None:
        expected_hotel_total = nightly_rate * nights
        variance = abs(hotel_total - expected_hotel_total)
        add_check(
            "hotel_total_math",
            "cost_math",
            "pass" if variance <= max(25, expected_hotel_total * 0.03) else "warn",
            "Hotel total matches nightly rate times nights." if variance <= max(25, expected_hotel_total * 0.03) else "Hotel total does not match nightly rate times nights.",
            [f"nightly_rate={nightly_rate}", f"nights={nights}", f"hotel_total={hotel_total}", f"expected_total={expected_hotel_total}"],
            "Fix the hotel subtotal or explain taxes/fees separately.",
        )

    medical_amount = _amount(cost_breakdown.get("medical"))
    medical_range = CITY_MEDICAL_DATA.get(city, {}).get("medical_cost_sgd", {})
    purpose = option.get("medical_purpose")
    expected_range = medical_range.get(purpose) if purpose else None
    if medical_amount is None:
        add_check(
            "medical_cost",
            "medical_cost",
            "needs_confirmation",
            "Medical cost estimate is missing a numeric amount.",
            [f"medical_purpose={purpose or 'missing'}"],
            "Retrieve or confirm the hospital package/consultation estimate and include source freshness.",
        )
    elif expected_range and expected_range[0] <= medical_amount <= expected_range[1]:
        add_check(
            "medical_cost",
            "medical_cost",
            "pass",
            "Medical estimate sits within the curated procedure range for this city.",
            [f"estimated={medical_amount}", f"range={expected_range[0]}-{expected_range[1]}", "source=curated_mvp_dataset"],
            "Confirm final clinical eligibility, package inclusions, and exclusions with the hospital.",
        )
    else:
        add_check(
            "medical_cost",
            "medical_cost",
            "warn",
            "Medical estimate could not be matched to the expected city/procedure range.",
            [f"estimated={medical_amount}", f"medical_purpose={purpose or 'missing'}", f"expected_range={expected_range or 'none'}"],
            "Verify the procedure subtype, hospital quote, and whether diagnostics, medications, and follow-up are included.",
        )

    subtotal = sum(
        amount
        for amount in (_amount(value) for value in cost_breakdown.values())
        if amount is not None
    )
    total_amount = _amount(total_cost)
    if total_amount is None:
        add_check(
            "total_cost_math",
            "cost_math",
            "needs_confirmation",
            "Total estimated cost is missing a numeric amount.",
            [f"subtotal={subtotal}"],
            "Recalculate total from itemized costs before ranking this option.",
        )
    else:
        variance = abs(total_amount - subtotal)
        add_check(
            "total_cost_math",
            "cost_math",
            "pass" if variance <= max(50, subtotal * 0.03) else "warn",
            "Total cost is consistent with itemized cost breakdown." if variance <= max(50, subtotal * 0.03) else "Total cost differs from itemized cost breakdown.",
            [f"total={total_amount}", f"itemized_subtotal={subtotal}", f"variance={round(variance, 2)}"],
            "Reconcile itemized categories, insurance premium, and total estimate before final ranking.",
        )

    data_status = metadata.get("data_status")
    add_check(
        "source_freshness",
        "source_freshness",
        "warn" if data_status != "real_time" else "pass",
        "Most planning data is not marked as real-time.",
        [
            f"source={metadata.get('source', 'missing')}",
            f"source_updated_at={metadata.get('source_updated_at', 'missing')}",
            f"data_status={data_status or 'missing'}",
        ],
        "For bookable recommendations, refresh hospital, flight, hotel, visa, and insurance data from official or live external sources.",
    )

    blocking_statuses = {"fail", "needs_confirmation"}
    overall_status = "needs_confirmation" if any(check["status"] in blocking_statuses for check in checks) else "passed_with_warnings"
    if all(check["status"] == "pass" for check in checks):
        overall_status = "passed"

    return {
        "option_id": option.get("option_id"),
        "city": city,
        "target_hospital": hospital,
        "audit_status": overall_status,
        "checks": checks,
        "blocking_issues": [check for check in checks if check["status"] in blocking_statuses],
        "warnings": [check for check in checks if check["status"] == "warn"],
        "metadata": {
            "source": "agent_estimate",
            "source_updated_at": date.today().isoformat(),
            "confidence_level": "medium",
            "data_status": "needs_confirmation",
        },
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
    if medical_purpose in {"car_t_blood_cancer", "dental_care"}:
        estimated_premium += 20
    if medical_purpose == "car_t_blood_cancer":
        estimated_premium += 180

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


def _amount(value: Any) -> float | None:
    if isinstance(value, dict):
        value = value.get("amount")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
