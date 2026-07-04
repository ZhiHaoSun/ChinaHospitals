---
name: prudential-singapore-china-insurance-policy
description: Use when assessing Prudential Singapore, PRUShield, PRUExtra, planned overseas medical treatment, China medical travel, Singaporeans seeking medical care in Mainland China, pre-authorisation, electronic Letter of Guarantee, eLOG, reimbursement claims, panel or Extended Panel treatment, overseas admission, direct settlement, or medical-tourism readiness checks.
---

# Prudential Singapore China Insurance Policy

## Purpose

Use this skill to produce cautious, source-backed planning guidance for
Prudential Singapore members considering medical care in Mainland China. Do not
present this as a coverage determination. Always require the user's policy
contract, plan schedule, riders, exclusions, benefit limits, and Prudential
written confirmation before booking non-refundable travel or treatment.

Primary official sources checked:

- PRUShield:
  https://www.prudential.com.sg/products/health-insurance/medical/prushield
- How to submit a claim:
  https://www.prudential.com.sg/claims-and-support/how-to-submit-a-claim
- Pre-authorisation:
  https://www.prudential.com.sg/claims-and-support/pre-authorisation
- PRUShield electronic Letter of Guarantee:
  https://www.prudential.com.sg/claims-and-support/prushield-electronic-letter-of-guarantee-elog

Source status: official Prudential Singapore product, claims, pre-authorisation,
and eLOG pages, not the full policy contract. Accessed 2026-07-04.

## Decision Rule

For a Singaporean taking planned medical care in China:

- Treat **PRUShield** and **PRUExtra** as Singapore health insurance/Integrated
  Shield-style coverage signals, not automatic medical-tourism coverage.
- Prudential's PRUShield page explicitly mentions planned overseas medical
  treatment under PRUShield and directs users to the claims process. Treat this
  as a claim-route signal, not proof of coverage for a specific treatment.
- Do not use Prudential's pre-authorisation pathway for China admission by
  default. Prudential's pre-authorisation page says pre-authorisation is not
  applicable for overseas admission.
- Do not use PRUShield eLOG for China treatment by default. Prudential's eLOG
  page says eLOG is applicable only at listed participating medical institutions
  and excludes overseas treatment.
- For China planned treatment, assume reimbursement/self-pay first unless
  Prudential gives written confirmation of coverage and a specific payment
  arrangement for the named hospital.

## Source-Backed Signals

Use these as planning signals only:

- PRUShield product information includes a section for planned overseas medical
  treatment under PRUShield and directs members to submit a claim.
- Prudential describes PRUShield as yearly renewable, with PRUExtra premiums not
  payable by MediSave.
- Prudential states website information is for reference only and that policy
  documents govern the contract.
- Prudential pre-authorisation is for upcoming hospital stay or day surgery and
  is typically submitted before planned admission or day surgery.
- Prudential's pre-authorisation FAQ says it is not applicable for emergency
  admission, eLOG granted cases, outpatient medical treatments, or overseas
  admission.
- Prudential's eLOG page says eLOG is only applicable at listed participating
  medical institutions and excludes overseas treatment.
- Prudential's claims page asks members to gather supporting documents such as
  medical reports, receipts, and other paperwork for claim submission.

## Workflow

1. Identify the exact Prudential product.
   Ask whether the user has PRUShield, PRUExtra, employer group cover, travel
   insurance, or another Prudential plan. Ask for plan tier, rider schedule,
   insured status, and Singapore residency/citizenship details.

2. Classify the China care request.
   Separate emergency care from planned care. Tag inpatient admission, day
   surgery/daypatient, outpatient consultation, diagnostics, cancer treatment,
   dental, vision, screening, maternity, rehabilitation, evacuation, or second
   opinion.

3. Check the planned overseas treatment route.
   If PRUShield is active, confirm whether the planned China treatment is within
   the policy's planned overseas medical treatment provisions, what limits
   apply, and whether the requested treatment category is eligible.

4. Exclude unavailable Singapore workflows.
   Mark Prudential pre-authorisation and PRUShield eLOG as not applicable to
   China overseas admission unless Prudential issues written contrary guidance.
   Do not infer China direct billing from Singapore panel, Extended Panel,
   pre-authorisation, or eLOG language.

5. Prepare a reimbursement plan.
   Assume the user may need to self-pay the China hospital and submit a claim.
   Ask Prudential for the exact claim form, medical document checklist, invoice
   requirements, proof-of-payment requirements, and currency handling.

6. Verify document and translation requirements.
   At minimum, plan for policy/member details, appointment confirmation,
   diagnosis certificate, medical reports, itemised invoices, official receipts,
   prescriptions, discharge/visit summary, procedure and diagnosis descriptions,
   and translation requirements for Chinese documents.

7. Mark unresolved items.
   If plan type, rider, planned-overseas benefit scope, claim route, document
   requirements, or translation rules are unknown, set data_status to
   `needs_confirmation` and add a blocking readiness item before any
   non-refundable booking.

## Questions To Ask Prudential Singapore

- Which Prudential product and riders are active: PRUShield, PRUExtra, employer
  medical cover, travel insurance, or another Prudential plan?
- Is planned medical or surgical treatment in Mainland China covered under this
  PRUShield policy, or only emergencies?
- Which overseas planned treatment limits, deductibles, co-insurance, exclusions,
  waiting periods, or pre-existing condition rules apply?
- Does the requested treatment type qualify: inpatient, day surgery, outpatient,
  diagnostics, cancer treatment, medication, dental, vision, screening, or
  rehabilitation?
- Since pre-authorisation is not applicable for overseas admission, what written
  review or confirmation can Prudential provide before the user travels?
- Since eLOG excludes overseas treatment, is reimbursement the only payment
  route for the named China hospital?
- Which claim documents, diagnosis details, procedure descriptions, invoices,
  receipts, and payment proofs must be collected in China?
- Do Chinese-language documents need certified translation, notarisation, or
  other authentication for medical claims?

## Output Pattern

When producing provider guidance, include:

```json
{
  "provider_key": "prudential",
  "display_name": "Prudential Singapore",
  "policy_status": "needs_prudential_confirmation",
  "source_type": "official_product_claims_preauthorisation_and_elog_pages_not_policy_contract",
  "source_urls": [
    "https://www.prudential.com.sg/products/health-insurance/medical/prushield",
    "https://www.prudential.com.sg/claims-and-support/how-to-submit-a-claim",
    "https://www.prudential.com.sg/claims-and-support/pre-authorisation",
    "https://www.prudential.com.sg/claims-and-support/prushield-electronic-letter-of-guarantee-elog"
  ],
  "direct_billing_assumption": "pre-authorisation excludes overseas admission and eLOG excludes overseas treatment; assume self-pay then claim unless Prudential confirms otherwise",
  "preauthorization_required": true,
  "data_status": "needs_confirmation",
  "confidence_level": "medium"
}
```

## Safety Rules

- Do not say Prudential covers China medical care unless the user's policy
  contract and Prudential written confirmation support it.
- Do not treat PRUShield or PRUExtra as automatic planned medical tourism
  coverage.
- Do not infer China direct billing from Singapore panel, Extended Panel,
  pre-authorisation, or eLOG workflows.
- Do not use PRUShield eLOG or pre-authorisation as available for overseas
  admission unless Prudential gives written contrary guidance.
- Do not recommend non-refundable travel or treatment booking until Prudential
  confirms benefit scope, claim route, hospital appointment, and claim documents.
