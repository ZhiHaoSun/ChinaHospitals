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
            "For China, distinguish Cigna Global Health Options from Close Care: Close Care is framed around residence plus nationality countries.",
            "Use Cigna's China page only as an official marketing/plan overview, not a policy contract or guarantee of benefits.",
            "Ask Cigna whether the specific China hospital international department can receive a guarantee of payment.",
        ],
        "china_plan_signals": [
            "Cigna describes China healthcare as mixing public, private, and insurance-based systems, with hospital tiers and possible language/access issues outside major areas.",
            "Silver, Gold, and Platinum Global Health Options list inpatient/daypatient hospital cover and full cancer care; annual limits differ by tier.",
            "Optional modules can include outpatient, evacuation and crisis assistance, health and wellbeing, vision, and dental.",
            "Close Care is limited to country of residence plus country of nationality and has lower stated annual and condition limits than the global tiers.",
            "Cigna states claims are aimed to be processed within 5 working days after receiving all necessary documentation; treat this as a target, not a guarantee.",
            "Pre-existing conditions may have special exclusions.",
        ],
        "preauthorization_questions": [
            "Is pre-authorization required for planned outpatient diagnostics, procedure, surgery, dental, eye, or checkup care in Mainland China?",
            "Is Mainland China inside this policy's planned-care territory, and is the selected optional module active for this treatment type?",
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
            {"title": "Cigna Global health insurance in China", "url": "https://www.cignaglobal.com/where-we-cover/china"},
        ],
        "agent_notes": [
            "Do not treat the word Cigna alone as enough to determine coverage; ask for plan type and policy territory.",
            "If the user is American, explicitly separate emergency travel coverage from planned medical tourism coverage.",
            "If the user is Singapore-based with an international plan, verify whether Mainland China is in the selected coverage area.",
            "Do not infer dental, vision, outpatient, evacuation, screening, or planned elective coverage unless the selected plan tier and optional modules confirm it.",
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
            "For AIA HealthShield Gold Max, treat it as a Singapore Integrated Shield Plan signal, not default medical-tourism coverage.",
            "For AIA Platinum International Health, verify whether China is inside worldwide excluding USA coverage and whether the requested treatment category is covered.",
            "For AIA Premier International Medical, verify the employer's selected covered area and whether the named China hospital is panel/cashless or Guarantee-of-Payment eligible.",
            "Ask whether the selected China hospital international department is on any AIA panel or requires self-pay reimbursement.",
        ],
        "singapore_china_plan_signals": [
            "AIA HealthShield Gold Max is described by AIA Singapore as a MediSave-approved Integrated Shield Plan consisting of MediShield Life and private insurance coverage for private or public hospital treatment.",
            "AIA Max VitalHealth Pro references non-AIA preferred providers with pre-authorisation or emergency admission through Accident & Emergency; do not apply that to planned China care without policy confirmation.",
            "AIA Platinum International Health is described as lifetime global medical coverage for Singapore residents and non-residents, with worldwide coverage excluding USA.",
            "AIA Platinum International Health mentions outpatient treatment and accidental dental treatment, but exact benefits and exclusions remain subject to policy contract.",
            "AIA Premier International Medical is corporate cover with covered-area choices: Asia, worldwide excluding USA, or worldwide.",
            "AIA Premier International Medical describes cashless facilities within the panel network and requesting Guarantee of Payment for planned hospital admission within covered area.",
            "AIA product pages state that the precise terms, conditions, and exclusions are specified in the policy contract.",
        ],
        "preauthorization_questions": [
            "Does this AIA plan cover planned overseas outpatient care or only emergency overseas treatment?",
            "Is Mainland China inside the policy's covered area, and is the selected benefit/rider active for this treatment type?",
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
            {
                "title": "AIA HealthShield Gold Max",
                "url": "https://www.aia.com.sg/en/our-products/health/medical-insurance/aia-healthshield-gold-max",
            },
            {
                "title": "AIA Platinum International Health",
                "url": "https://www.aia.com.sg/en/our-products/health/medical-insurance/aia-platinum-international-health",
            },
            {
                "title": "AIA Premier International Medical",
                "url": "https://www.aia.com.sg/en/our-products/corporate-international-medical/aia-premier-international-medical",
            },
            {"title": "AIA Singapore Form Library", "url": "https://www.aia.com.sg/en/help-support/form-library"},
            {"title": "AIA Group", "url": "https://www.aia.com/"},
        ],
        "agent_notes": [
            "Always ask which AIA country issued the policy.",
            "For Singapore users, ask whether the policy is personal health, corporate health, Shield/IP, or travel insurance.",
            "Do not assume a Singapore hospital panel applies to Mainland China hospitals.",
            "Do not infer direct billing in China from Singapore preferred-provider language; require the exact hospital and department to be confirmed by AIA.",
            "For Singaporean medical tourism, add a blocking readiness item until AIA confirms covered area, pre-authorization, direct billing or reimbursement path, and claim documents.",
        ],
    },
    "great_eastern": {
        "display_name": "Great Eastern Singapore",
        "aliases": [
            "great eastern",
            "great eastern life",
            "greateastern",
            "ge",
            "great supremehealth",
            "great totalcare",
            "great totalcare plus",
            "gmcc",
        ],
        "typical_user_regions": ["Singapore"],
        "policy_lookup_focus": [
            "Identify whether the member has GREAT SupremeHealth, GREAT TotalCare 2, GREAT TotalCare Plus 2, corporate medical cover, travel insurance, or another Great Eastern plan.",
            "Treat GREAT SupremeHealth as a Singapore Integrated Shield Plan signal, not default medical-tourism coverage.",
            "For planned care in China, verify whether GREAT TotalCare Plus 2 or another worldwide rider is active and whether the requested treatment is eligible.",
            "Classify China as non-ASEAN when checking GREAT TotalCare Plus 2 overseas non-emergency treatment limits and rules.",
            "Use Great Eastern product and benefit pages as official guidance, not policy contracts or guarantees of benefits.",
            "Ask Great Eastern whether the specific China hospital and treatment must be handled as reimbursement-only.",
        ],
        "singapore_china_plan_signals": [
            "GREAT SupremeHealth is described as a MediSave-approved Integrated Shield Plan consisting of MediShield Life and private insurance coverage.",
            "GREAT TotalCare 2 is described as supplementary coverage that can reduce out-of-pocket expenses for eligible claims.",
            "GREAT TotalCare Plus 2 is described as a rider attached to Great TotalCare 2 that extends medical coverage worldwide.",
            "GREAT TotalCare Plus 2 benefit tables include overseas emergency medical or surgical treatment and overseas non-emergency medical or surgical treatment.",
            "Overseas non-emergency treatment is split by ASEAN and non-ASEAN, and China should be treated as non-ASEAN for planning checks.",
            "Great Eastern's GMCC FAQ says overseas treatment is not eligible for pre-approval, with overseas treatment claims submitted by e-filing or manually.",
            "Product and benefit schedule pages state that terms, conditions, limits, exclusions, and policy contracts govern coverage.",
        ],
        "preauthorization_questions": [
            "Is GREAT TotalCare Plus 2 or another worldwide rider active on this policy?",
            "Is planned medical or surgical treatment in Mainland China covered, or only overseas emergency treatment?",
            "Which non-ASEAN benefit limits, deductibles, co-insurance, lifetime limits, and lower-of-charge rules apply?",
            "Can Great Eastern provide any written confirmation before travel if GMCC pre-approval is not available for overseas treatment?",
            "Is the named China hospital direct-settlement eligible, or should the user self-pay and submit an e-file/manual claim?",
        ],
        "direct_billing_assumption": "overseas treatment is not eligible for Great Eastern PAC/pre-approval per GMCC FAQ; assume self-pay then e-file/manual claim unless Great Eastern confirms otherwise",
        "claim_documents": COMMON_CLAIM_DOCUMENTS,
        "risk_flags": COMMON_RISK_FLAGS
        + [
            "GREAT SupremeHealth alone is Singapore Integrated Shield-style coverage, not default medical-tourism cover",
            "GREAT TotalCare Plus 2 rider and plan type must be active for worldwide non-emergency treatment signals",
            "PAC/direct settlement workflow excludes overseas treatment unless Great Eastern confirms otherwise",
        ],
        "helpful_links": [
            {
                "title": "GREAT SupremeHealth",
                "url": "https://www.greateasternlife.com/sg/en/personal-insurance/our-products/health-insurance/great-supremehealth-main.html",
            },
            {
                "title": "Great Medical Care Concierge",
                "url": "https://www.greateasternlife.com/sg/en/customer-services/claims/medical-hospitalisation/gmcc.html",
            },
            {
                "title": "GREAT SupremeHealth and GREAT TotalCare benefit schedule",
                "url": "https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-ftrp-imc-cm/health-insurance-/great-supremehealth/april-2026/gels-pdt-pd-gsh-gtc-tob-eng.pdf",
            },
        ],
        "agent_notes": [
            "Do not infer China planned-care coverage from GREAT SupremeHealth alone.",
            "For China, ask specifically whether the member has GREAT TotalCare Plus 2 and what non-ASEAN limits apply.",
            "Do not present GMCC, Letter of Guarantee, or Certificate of Pre-Authorisation as available overseas unless Great Eastern confirms a written exception.",
            "Route payment planning to reimbursement-first until Great Eastern confirms a direct-settlement arrangement for the named China hospital.",
            "Add a blocking readiness item until Great Eastern confirms rider status, benefit limits, payment path, and claim documents.",
        ],
    },
    "prudential": {
        "display_name": "Prudential Singapore",
        "aliases": [
            "prudential",
            "prudential singapore",
            "prushield",
            "pru shield",
            "pruextra",
            "pru extra",
            "pru",
        ],
        "typical_user_regions": ["Singapore"],
        "policy_lookup_focus": [
            "Identify whether the member has PRUShield, PRUExtra, employer medical cover, travel insurance, or another Prudential plan.",
            "Treat PRUShield and PRUExtra as Singapore health insurance/Integrated Shield-style signals, not automatic medical-tourism coverage.",
            "For planned care in China, use Prudential's planned overseas medical treatment claim route as a signal that the policy must be checked, not a guarantee of benefits.",
            "Do not rely on Prudential pre-authorisation for overseas admission because the official FAQ says it is not applicable.",
            "Do not rely on PRUShield eLOG for China treatment because the official eLOG page excludes overseas treatment and applies to listed Singapore participating institutions.",
            "Ask Prudential for exact claim documents, translation requirements, and any written review available before travel.",
        ],
        "singapore_china_plan_signals": [
            "PRUShield product information mentions planned overseas medical treatment and directs users to submit a claim.",
            "PRUShield is yearly renewable and PRUExtra premiums cannot be paid by MediSave.",
            "Prudential's pre-authorisation page says pre-authorisation is not applicable for overseas admission.",
            "Prudential's eLOG page says eLOG is only applicable at listed participating medical institutions and excludes overseas treatment.",
            "Prudential's claims page asks members to gather supporting documents such as medical reports, receipts, and other paperwork.",
            "Prudential website content is reference information and policy documents govern the contract.",
        ],
        "preauthorization_questions": [
            "Is planned medical or surgical treatment in Mainland China covered under this PRUShield policy, or only emergencies?",
            "Which planned overseas treatment benefit limits, deductibles, co-insurance, exclusions, and pre-existing condition rules apply?",
            "If pre-authorisation is not applicable for overseas admission, can Prudential provide written coverage review before travel?",
            "If eLOG excludes overseas treatment, is reimbursement the only available payment route for the named China hospital?",
            "What claim forms, medical reports, invoices, receipts, payment proofs, and translations are required for China treatment?",
        ],
        "direct_billing_assumption": "PRUShield planned overseas treatment should be treated as reimbursement/claim route; pre-authorisation excludes overseas admission and eLOG excludes overseas treatment",
        "claim_documents": COMMON_CLAIM_DOCUMENTS,
        "risk_flags": COMMON_RISK_FLAGS
        + [
            "pre-authorisation is not applicable to overseas admission",
            "eLOG excludes overseas treatment and only applies to listed Singapore participating medical institutions",
            "planned overseas treatment must be verified through claims and policy documents",
        ],
        "helpful_links": [
            {"title": "PRUShield", "url": "https://www.prudential.com.sg/products/health-insurance/medical/prushield"},
            {
                "title": "Prudential Singapore claims",
                "url": "https://www.prudential.com.sg/claims-and-support/how-to-submit-a-claim",
            },
            {
                "title": "Prudential pre-authorisation",
                "url": "https://www.prudential.com.sg/claims-and-support/pre-authorisation",
            },
            {
                "title": "PRUShield eLOG",
                "url": "https://www.prudential.com.sg/claims-and-support/prushield-electronic-letter-of-guarantee-elog",
            },
        ],
        "agent_notes": [
            "Do not infer China planned-care coverage from PRUShield or PRUExtra branding alone.",
            "For China admission, mark Prudential pre-authorisation and PRUShield eLOG as unavailable unless Prudential provides written contrary guidance.",
            "Route payment planning to reimbursement-first until Prudential confirms a direct-settlement exception for the named China hospital.",
            "Ask Prudential whether Chinese medical documents need certified translation or other authentication before claim submission.",
            "Add a blocking readiness item until Prudential confirms planned overseas benefit scope, claim path, and documents.",
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
