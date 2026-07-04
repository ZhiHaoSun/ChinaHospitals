---
name: aia-singapore-china-insurance-policy
description: Use when assessing AIA Singapore insurance for a Singaporean or Singapore resident seeking medical care in Mainland China, including AIA HealthShield Gold Max, AIA Max VitalHealth, AIA Platinum International Health, AIA Premier International Medical, corporate international medical cover, planned overseas treatment, pre-authorisation, guarantee of payment, direct billing, reimbursement claims, covered area, emergency-only versus planned-care handling, or medical-tourism readiness checks.
---

# AIA Singapore China Insurance Policy

## Purpose

Use this skill to produce cautious, source-backed planning guidance for AIA
Singapore members considering medical care in Mainland China. Do not present
this as a coverage determination. Always require the user's policy contract,
plan schedule, riders, covered area, exclusions, and AIA written confirmation
before booking non-refundable travel or treatment.

Primary official sources checked:

- AIA Singapore HealthShield Gold Max:
  https://www.aia.com.sg/en/our-products/health/medical-insurance/aia-healthshield-gold-max
- AIA Singapore Platinum International Health:
  https://www.aia.com.sg/en/our-products/health/medical-insurance/aia-platinum-international-health
- AIA Singapore Premier International Medical:
  https://www.aia.com.sg/en/our-products/corporate-international-medical/aia-premier-international-medical
- AIA Singapore Form Library / service requests:
  https://www.aia.com.sg/en/help-support/form-library

Source status: official AIA Singapore product pages and service pages, not full
policy contracts. Accessed 2026-07-04.

## Decision Rule

For a Singaporean taking planned medical care in China:

- Treat **AIA HealthShield Gold Max** as a Singapore Integrated Shield Plan
  signal, not a default medical-tourism policy. Its product page describes a
  MediSave-approved Integrated Shield Plan for private or public hospital
  treatment, with AIA Max VitalHealth add-ons and pre-authorisation language.
  Do not assume elective/planned China treatment is covered.
- Treat **AIA Platinum International Health** as the stronger individual-policy
  candidate for planned care abroad because AIA describes it as lifetime global
  medical coverage, world-class healthcare worldwide, and notes worldwide
  coverage excluding USA. Still verify exclusions, covered area, and whether
  planned treatment in China is covered.
- Treat **AIA Premier International Medical** as the strongest corporate/group
  international medical signal. AIA describes covered-area options including
  Asia, worldwide excluding USA, and worldwide; cashless facilities within panel
  networks; and a 24/7 member service centre for Guarantee of Payment for
  planned hospital admission within the covered area.

## Source-Backed Signals

Use these as planning signals only:

- HealthShield Gold Max is an Integrated Shield Plan consisting of MediShield
  Life plus private insurance coverage for private or public hospital treatment.
- HealthShield Gold Max advertises annual claim limits up to S$2 million,
  lifetime coverage, pre/post-hospitalisation support, and AIA Max VitalHealth
  Pro add-ons. AIA Max VitalHealth Pro references non-AIA preferred providers
  with pre-authorisation or emergency admission through Accident & Emergency.
- HealthShield add-ons include Emergency Care Pro and Cancer Care Pro, but these
  need exact rider and policy wording checks before applying them to China.
- Platinum International Health is described as global medical coverage for
  Singapore residents and non-residents, including outpatient treatment and
  accidental dental treatment. AIA states worldwide coverage excludes USA.
- Premier International Medical is corporate international medical cover with
  covered-area choices: Asia, worldwide excluding USA, or worldwide.
- Premier International Medical states cashless facilities are available within
  its panel network and that members should contact the 24/7 service centre for
  Guarantee of Payment for planned hospital admission within covered area.
- AIA product pages warn that page content is not a contract of insurance and
  that precise terms, conditions, and exclusions are in the policy contract.

## Workflow

1. Identify the exact AIA Singapore product.
   Ask whether the user has HealthShield Gold Max, AIA Max VitalHealth,
   Platinum International Health, Premier International Medical, corporate
   employee benefits, travel insurance, or another AIA plan.

2. Identify the policy role.
   Ask if the user is policyholder, insured, dependent, employee under group
   cover, Singapore citizen/PR, foreigner resident, or non-resident.

3. Classify the China care request.
   Separate emergency care from planned care. Tag inpatient admission,
   day surgery/daypatient, outpatient consultation, diagnostics, cancer drug
   treatment, CAR-T/cell therapy, dental, eye/vision, screening, maternity,
   evacuation, or second opinion.

4. Match the plan type to China care.
   For HealthShield, assume needs confirmation and likely Singapore-centric
   unless the policy/rider explicitly supports overseas treatment. For Platinum
   International Health, check whether China is inside the worldwide-excluding-
   USA territory and whether the requested care category is covered. For Premier
   International Medical, check whether the employer selected Asia, worldwide
   excluding USA, or worldwide and whether the China hospital is in the panel.

5. Verify hospital network and payment path.
   Ask AIA whether the exact Mainland China hospital and international
   department supports direct billing, cashless facility, Guarantee of Payment,
   or reimbursement-only handling.

6. Require pre-authorisation before planned care.
   Ask AIA for required documents, medical necessity review, cost estimate
   review, whether referral is needed, how long review takes, and whether any
   exclusions or waiting periods apply.

7. Prepare claim evidence before travel.
   At minimum, plan for policy/member details, appointment confirmation,
   pre-authorisation or Guarantee of Payment letter if issued, diagnosis
   certificate, doctor report, medical records, itemised invoice, official
   receipt, prescriptions, discharge/visit summary, and certified translation
   requirements if Chinese documents are used.

8. Mark unresolved items.
   If plan type, rider, covered area, hospital network, pre-authorisation, or
   payment path is unknown, set data_status to `needs_confirmation` and add a
   blocking readiness item before any non-refundable booking.

## Questions To Ask AIA Singapore

- Which AIA product is active: HealthShield Gold Max, Max VitalHealth, Platinum
  International Health, Premier International Medical, corporate benefits, or
  travel insurance?
- Is planned medical care in Mainland China covered, or only emergencies?
- Is China inside the policy's covered area? For Premier International Medical,
  did the employer choose Asia, worldwide excluding USA, or worldwide?
- Is the selected China hospital international department a panel/cashless
  facility or reimbursement-only?
- Can AIA issue a Guarantee of Payment or direct settlement for this planned
  hospital admission/treatment?
- Is pre-authorisation required before consultation, diagnostics, procedure,
  admission, cancer treatment, dental, eye care, or health screening?
- Which documents, diagnosis details, procedure descriptions, and cost estimates
  must be submitted before review?
- Are pre-existing condition exclusions, waiting periods, Singapore residency
  rules, MediShield Life/IP rules, or rider limits relevant?
- Which claim documents must be collected before leaving China, and do Chinese
  documents need certified translation?

## Output Pattern

When producing provider guidance, include:

```json
{
  "provider_key": "aia",
  "display_name": "AIA Singapore",
  "policy_status": "needs_aia_singapore_confirmation",
  "source_type": "official_product_pages_not_policy_contract",
  "source_urls": [
    "https://www.aia.com.sg/en/our-products/health/medical-insurance/aia-healthshield-gold-max",
    "https://www.aia.com.sg/en/our-products/health/medical-insurance/aia-platinum-international-health",
    "https://www.aia.com.sg/en/our-products/corporate-international-medical/aia-premier-international-medical"
  ],
  "direct_billing_assumption": "assume reimbursement unless AIA confirms panel cashless facility or Guarantee of Payment for the named China hospital",
  "preauthorization_required": true,
  "data_status": "needs_confirmation",
  "confidence_level": "medium"
}
```

## Safety Rules

- Do not say AIA covers China medical care unless the user's policy contract and
  AIA written confirmation support it.
- Do not treat HealthShield Gold Max as planned medical tourism coverage by
  default.
- Do not infer China direct billing from Singapore preferred-provider language.
- Do not infer Premier International Medical coverage unless the employer's
  selected covered area includes China and the member is eligible.
- Do not recommend non-refundable travel or treatment booking until AIA
  pre-authorisation, Guarantee of Payment/direct billing status, hospital
  appointment, and claim-document requirements are confirmed.
