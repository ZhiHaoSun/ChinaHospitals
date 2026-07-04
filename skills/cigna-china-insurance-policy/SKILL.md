---
name: cigna-china-insurance-policy
description: Use when assessing Cigna, Cigna Healthcare, or Cigna Global insurance for China medical travel, expat care, planned treatment, hospital selection, direct billing, pre-authorization, claim documents, outpatient modules, cancer care, evacuation, dental/vision add-ons, or whether a Mainland China hospital plan should be treated as covered, reimbursement-only, or needing confirmation.
---

# Cigna China Insurance Policy

## Purpose

Use this skill to turn Cigna Global China insurance information into cautious
planning guidance for MedTour AI. Do not present this as a binding coverage
determination. Always tell the user that the final answer depends on their
policy wording, issuing entity, plan tier, optional modules, territory, and
Cigna/member-services confirmation.

Primary source checked: https://www.cignaglobal.com/where-we-cover/china

Source status: official Cigna Global / Cigna Healthcare marketing and plan
overview page, not a full policy contract. Accessed 2026-07-04.

## Core China Guidance

- Treat Cigna Global China as relevant mainly for expats, internationally mobile
  users, and users with international medical cover. Do not assume a domestic
  Cigna plan covers planned care in China.
- China hospital choice matters. Cigna describes China healthcare as including
  public, private, and insurance-based systems, with hospital tiers and possible
  language/access issues outside major areas.
- Prefer top-tier hospitals and international departments when matching a China
  treatment plan to Cigna. Still verify whether the exact hospital department is
  in-network, direct-billing eligible, or reimbursement-only.
- Warn that some third-tier or rural facilities may require cash payment.
- Treat Cigna marketing network and claims processing statements as non-binding
  until confirmed against the member's policy and claim requirements.

## Plan Signals From The Source

Use these as planning signals only:

- Cigna Global Health Options may offer worldwide or worldwide-excluding-USA
  cover, depending on selected plan.
- Silver: core inpatient/daypatient hospital cover, private room, full cancer
  care, and a stated annual benefit limit of USD 1,000,000.
- Gold: higher annual benefit limit of USD 2,000,000, inpatient/daypatient
  treatment, private room, full cancer care, and inpatient maternity.
- Platinum: highest tier, described as unlimited overall annual limit with many
  benefits paid in full; includes inpatient/daypatient, private room, full cancer
  care, inpatient maternity, and mental/behavioural health care paid in full.
- Close Care: coverage focused on country of residence plus country of
  nationality; stated annual benefit limit USD 500,000 and condition limit
  USD 250,000.
- Optional modules can include outpatient, evacuation/crisis assistance, health
  and wellbeing, vision, and dental. Never assume dental, vision correction,
  routine checkups, evacuation, or outpatient procedures are included unless the
  selected module and policy confirm it.
- Cigna states that claims are aimed to be processed within 5 working days after
  receiving all necessary documentation. Treat this as a service target, not a
  guarantee.
- Pre-existing conditions may have special exclusions.

## Workflow

1. Identify the exact Cigna product.
   Ask whether the user has Cigna Global, Cigna Healthcare domestic, employer
   group, IGO/NGO, travel, or another Cigna-administered plan. Ask for issuing
   country, policy territory, plan tier, and optional modules.

2. Classify the China care request.
   Separate emergency care from planned medical travel. For planned care, tag
   the request as inpatient, daypatient, outpatient, cancer care, dental,
   vision/eye, health screening, maternity, mental health, evacuation, or other.

3. Match benefits cautiously.
   Inpatient/daypatient and cancer care are stronger signals on Silver/Gold/
   Platinum than elective outpatient, dental, vision correction, or screening.
   Close Care may only fit if China is the user's residence or nationality
   country under the policy.

4. Verify the hospital pathway.
   Ask Cigna whether the exact hospital and international department in Mainland
   China can receive direct billing or guarantee of payment. If not confirmed,
   assume self-pay first and reimbursement later.

5. Require pre-authorization checks before booking.
   For planned treatment, ask Cigna what documents are required, whether medical
   necessity review applies, whether the procedure is excluded, and how long
   review normally takes.

6. Collect claim-document requirements.
   Before travel, request the exact claim checklist. At minimum, plan for member
   ID, pre-authorization or guarantee letter if issued, appointment confirmation,
   diagnosis certificate, doctor report, itemized invoice, official receipt,
   prescriptions, discharge/visit summary, and translations if required.

7. Mark unresolved items in the plan.
   If plan tier, optional modules, territory, hospital network, or pre-auth
   status is unknown, set data_status to `needs_confirmation` and add a blocking
   readiness item before non-refundable booking.

## Questions To Ask Cigna

- Is Mainland China inside this policy's planned-care territory?
- Is this selected China hospital international department in-network,
  guarantee-of-payment eligible, or reimbursement-only?
- Does this plan cover the requested treatment type: inpatient, daypatient,
  outpatient, dental, vision, screening, cancer care, or evacuation?
- Are outpatient, dental, vision, evacuation, health and wellbeing, or maternity
  modules active on this policy?
- Is pre-authorization required before consultation, diagnostics, treatment, or
  admission?
- What documents and medical coding/procedure descriptions are required for
  pre-authorization?
- Are pre-existing condition exclusions, waiting periods, elective-care limits,
  or medical-necessity rules relevant?
- What documents must be collected in China for claims, and do Chinese-language
  documents need certified translation?

## Output Pattern

When producing provider guidance, include:

```json
{
  "provider_key": "cigna",
  "display_name": "Cigna / Cigna Healthcare / Cigna Global",
  "policy_status": "needs_member_services_confirmation",
  "china_source_url": "https://www.cignaglobal.com/where-we-cover/china",
  "source_type": "official_marketing_overview_not_policy_contract",
  "direct_billing_assumption": "possible only after plan, hospital, and guarantee-of-payment confirmation; otherwise assume self-pay and claim",
  "preauthorization_required": true,
  "data_status": "needs_confirmation",
  "confidence_level": "medium"
}
```

## Safety Rules

- Do not say Cigna will cover the treatment unless the member's policy and Cigna
  confirmation explicitly support it.
- Do not infer planned medical tourism coverage from emergency travel coverage.
- Do not infer China coverage from the word "worldwide" until exclusions and
  optional modules are checked.
- Do not treat Cigna's China overview page as a substitute for policy documents.
- Do not recommend non-refundable booking until hospital appointment, Cigna
  pre-authorization/direct-billing status, and claim documents are confirmed.
