"""Curated insurance-provider lookup skills for planning agents.

These skills are not a coverage determination. They help the agent ask the
right questions for common international insurers before a patient books care in
China. Production should replace or enrich this data with insurer APIs, policy
documents, and advisor verification.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any


COMMON_PROVIDER_CHECKLIST = [
    "Confirm whether planned outpatient or elective treatment overseas is covered before booking.",
    "Ask whether Mainland China is inside the policy territory for planned care, not only emergencies.",
    "Request written pre-authorization requirements and guarantee-of-payment instructions.",
    "Confirm whether the selected hospital international department is in-network or reimbursement-only.",
    "Ask whether outpatient follow-up, complications, medication, diagnostics, and translation fees are covered.",
    "Request exact claim document requirements and whether Chinese-language documents need certified translation.",
]

COMMON_CLAIM_DOCUMENTS = [
    "passport or member ID copy if requested",
    "insurance card or membership certificate",
    "pre-authorization or guarantee-of-payment letter if issued",
    "doctor referral or appointment confirmation if required",
    "diagnosis certificate",
    "medical report or visit summary",
    "itemized invoice",
    "official payment receipt",
    "prescription list and medication receipt",
    "bank or reimbursement details",
]

COMMON_RISK_FLAGS = [
    "planned elective treatment may be excluded or require prior approval",
    "pre-existing condition limits may apply",
    "network-only policies may not cover the chosen hospital",
    "direct billing may require guarantee-of-payment before admission or treatment",
    "routine health screening, dental, aesthetics, and vision correction are often benefit-specific",
]


INSURANCE_PROVIDER_SKILLS: dict[str, dict[str, Any]] = {
    "cigna": {
        "display_name": "Cigna / Cigna Healthcare / Cigna Global",
        "aliases": ["cigna", "cigna global", "cigna healthcare", "cigna international", "cigna envoy"],
        "typical_user_regions": ["United States", "Singapore", "global expatriate"],
        "policy_lookup_focus": [
            "Check whether the member has a domestic US plan, employer plan, or Cigna Global international medical plan.",
            "For US domestic plans, do not assume planned overseas care is covered unless the plan documents say so.",
            "For Cigna Global-style plans, verify area of coverage, outpatient benefits, planned treatment rules, and direct-pay availability.",
            "Ask Cigna whether the specific China hospital international department can receive a guarantee of payment.",
        ],
        "preauthorization_questions": [
            "Is pre-authorization required for planned outpatient diagnostics, procedure, surgery, dental, eye, or checkup care in Mainland China?",
            "What medical documents and CPT/procedure descriptions are needed before Cigna can review the case?",
            "Can Cigna issue a guarantee of payment to this hospital, or should the user self-pay and claim?",
            "How many business days does pre-authorization typically take for overseas planned care?",
        ],
        "direct_billing_assumption": "possible only if the member plan, hospital, and pre-authorization process support direct pay; otherwise assume self-pay then reimbursement",
        "claim_documents": COMMON_CLAIM_DOCUMENTS,
        "risk_flags": COMMON_RISK_FLAGS,
        "helpful_links": [
            {"title": "Cigna Healthcare member resources", "url": "https://www.cigna.com/"},
            {"title": "Cigna Global", "url": "https://www.cignaglobal.com/"},
        ],
        "agent_notes": [
            "Do not treat the word Cigna alone as enough to determine coverage; ask for plan type and policy territory.",
            "If the user is American, explicitly separate emergency travel coverage from planned medical tourism coverage.",
            "If the user is Singapore-based with an international plan, verify whether Mainland China is in the selected coverage area.",
        ],
    },
    "aia": {
        "display_name": "AIA",
        "aliases": ["aia", "aia singapore", "aia international", "aia healthshield", "aia health"],
        "typical_user_regions": ["Singapore", "Hong Kong", "Malaysia", "Thailand", "regional Asia"],
        "policy_lookup_focus": [
            "Identify the country/region that issued the AIA policy because benefits and panels differ by market.",
            "For Singapore policies, distinguish Integrated Shield/private hospital benefits from travel insurance or corporate medical benefits.",
            "Verify whether planned treatment in Mainland China is covered, and whether it is emergency-only, reimbursement-only, or pre-authorized planned care.",
            "Ask whether the selected China hospital international department is on any AIA panel or requires self-pay reimbursement.",
        ],
        "preauthorization_questions": [
            "Does this AIA plan cover planned overseas outpatient care or only emergency overseas treatment?",
            "Is pre-authorization required before visiting a Mainland China hospital international department?",
            "Does AIA require referral letters, diagnosis, medical necessity review, or cost estimates before approval?",
            "Can AIA provide direct settlement or a letter of guarantee for this hospital, or is reimbursement required?",
        ],
        "direct_billing_assumption": "usually needs market-specific panel/direct-settlement confirmation; assume reimbursement unless AIA confirms direct settlement",
        "claim_documents": COMMON_CLAIM_DOCUMENTS,
        "risk_flags": COMMON_RISK_FLAGS
        + [
            "Singapore Shield-style benefits may not behave like global planned-care coverage",
            "travel insurance riders may cover emergencies but exclude planned treatment abroad",
        ],
        "helpful_links": [
            {"title": "AIA Singapore", "url": "https://www.aia.com.sg/"},
            {"title": "AIA Group", "url": "https://www.aia.com/"},
        ],
        "agent_notes": [
            "Always ask which AIA country issued the policy.",
            "For Singapore users, ask whether the policy is personal health, corporate health, Shield/IP, or travel insurance.",
            "Do not assume a Singapore hospital panel applies to Mainland China hospitals.",
        ],
    },
    "bupa": {
        "display_name": "Bupa / Bupa Global",
        "aliases": ["bupa", "bupa global", "bupa international"],
        "typical_user_regions": ["global expatriate", "Hong Kong", "United Kingdom", "Singapore"],
        "policy_lookup_focus": [
            "Verify area of cover and whether Mainland China planned treatment is inside scope.",
            "Ask if Bupa can arrange direct settlement or guarantee of payment with the hospital international department.",
            "Confirm outpatient, dental, optical, health-screening, and maternity/aesthetic benefit sublimits separately.",
        ],
        "preauthorization_questions": [
            "Which treatments need pre-authorization before travel?",
            "Can Bupa confirm direct settlement with this named hospital department?",
            "Are diagnostics and follow-up visits covered under the same authorization?",
        ],
        "direct_billing_assumption": "possible for some international plans and facilities, but requires plan and provider confirmation",
        "claim_documents": COMMON_CLAIM_DOCUMENTS,
        "risk_flags": COMMON_RISK_FLAGS,
        "helpful_links": [{"title": "Bupa Global", "url": "https://www.bupaglobal.com/"}],
        "agent_notes": ["Treat Bupa country-market and Bupa Global policies separately."],
    },
    "allianz": {
        "display_name": "Allianz / Allianz Care",
        "aliases": ["allianz", "allianz care", "allianz global assistance"],
        "typical_user_regions": ["global expatriate", "United States", "Singapore", "Europe"],
        "policy_lookup_focus": [
            "Distinguish travel insurance/emergency assistance from international health insurance planned-care benefits.",
            "Confirm whether planned treatment in Mainland China needs treatment guarantee or pre-authorization.",
            "Ask whether the hospital international department can coordinate with Allianz Care provider services.",
        ],
        "preauthorization_questions": [
            "Is the user covered by Allianz Care health insurance or Allianz travel insurance?",
            "Is planned overseas treatment covered or excluded?",
            "Can Allianz issue a treatment guarantee to this provider?",
        ],
        "direct_billing_assumption": "depends heavily on product line; travel insurance often differs from Allianz Care international health cover",
        "claim_documents": COMMON_CLAIM_DOCUMENTS,
        "risk_flags": COMMON_RISK_FLAGS,
        "helpful_links": [
            {"title": "Allianz Care", "url": "https://www.allianzcare.com/"},
            {"title": "Allianz Travel Insurance", "url": "https://www.allianztravelinsurance.com/"},
        ],
        "agent_notes": ["Ask product line first; do not infer health coverage from travel-insurance branding."],
    },
    "axa": {
        "display_name": "AXA / AXA Global Healthcare",
        "aliases": ["axa", "axa global healthcare", "axa international"],
        "typical_user_regions": ["global expatriate", "Singapore", "Hong Kong", "Europe"],
        "policy_lookup_focus": [
            "Identify issuing AXA market and whether the policy is local, travel, corporate, or international health.",
            "Check whether Mainland China planned outpatient care is inside territory and benefit limits.",
            "Ask whether the hospital international department supports direct settlement or reimbursement-only handling.",
        ],
        "preauthorization_questions": [
            "Does AXA require pre-approval for this procedure and destination?",
            "Can AXA confirm the hospital's international department as eligible for direct settlement?",
            "Which claim form and medical documents are required after outpatient care?",
        ],
        "direct_billing_assumption": "needs issuing-market and provider-network confirmation",
        "claim_documents": COMMON_CLAIM_DOCUMENTS,
        "risk_flags": COMMON_RISK_FLAGS,
        "helpful_links": [{"title": "AXA Global Healthcare", "url": "https://www.axaglobalhealthcare.com/"}],
        "agent_notes": ["Ask issuing market because AXA benefits differ significantly by country."],
    },
}


GENERIC_PROVIDER_SKILL: dict[str, Any] = {
    "display_name": "Unknown or Other Insurance Provider",
    "aliases": [],
    "typical_user_regions": [],
    "policy_lookup_focus": COMMON_PROVIDER_CHECKLIST,
    "preauthorization_questions": [
        "Does this policy cover planned medical care in Mainland China?",
        "Is the selected hospital international department in-network, direct-billing, or reimbursement-only?",
        "What pre-authorization documents are required before travel?",
        "Which claim documents must be collected before leaving China?",
    ],
    "direct_billing_assumption": "unknown; assume self-pay first until insurer and hospital confirm otherwise",
    "claim_documents": COMMON_CLAIM_DOCUMENTS,
    "risk_flags": COMMON_RISK_FLAGS,
    "helpful_links": [],
    "agent_notes": ["Ask the user for insurer name, issuing country, plan type, member services phone/email, and policy territory."],
}


def lookup_provider_skill(provider_name: str | None) -> dict[str, Any]:
    """Return provider-specific lookup guidance by fuzzy alias match."""

    normalized = _normalize_provider_name(provider_name)
    for provider_key, skill in INSURANCE_PROVIDER_SKILLS.items():
        aliases = [provider_key, *skill.get("aliases", [])]
        if any(alias and alias in normalized for alias in aliases):
            return _skill_result(provider_key, skill, matched=True)
    return _skill_result("unknown", GENERIC_PROVIDER_SKILL, matched=False)


def list_supported_providers() -> list[dict[str, str]]:
    """Return provider names this curated skill file knows about."""

    return [
        {"provider_key": key, "display_name": value["display_name"]}
        for key, value in sorted(INSURANCE_PROVIDER_SKILLS.items())
    ]


def _skill_result(provider_key: str, skill: dict[str, Any], *, matched: bool) -> dict[str, Any]:
    result = deepcopy(skill)
    result["provider_key"] = provider_key
    result["matched"] = matched
    result["metadata"] = {
        "source": "agent_estimate",
        "source_updated_at": date.today().isoformat(),
        "confidence_level": "medium" if matched else "low",
        "data_status": "needs_confirmation",
    }
    return result


def _normalize_provider_name(provider_name: str | None) -> str:
    return (provider_name or "").strip().lower()
