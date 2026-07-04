---
name: great-eastern-singapore-china-insurance-policy
description: Use when assessing Great Eastern Singapore, GREAT SupremeHealth, GREAT TotalCare, GREAT TotalCare Plus 2, Great Medical Care Concierge, Health Connect, Certificate of Pre-Authorisation, Letter of Guarantee, overseas medical or surgical treatment, Singaporeans seeking medical care in Mainland China, planned China treatment, emergency China treatment, direct settlement, reimbursement claims, or medical-tourism readiness checks.
---

# Great Eastern Singapore China Insurance Policy

## Purpose

Use this skill to produce cautious, source-backed planning guidance for Great
Eastern Singapore members considering medical care in Mainland China. Do not
present this as a coverage determination. Always require the user's policy
contract, plan schedule, riders, exclusions, benefit limits, and Great Eastern
written confirmation before booking non-refundable travel or treatment.

Primary official sources checked:

- GREAT SupremeHealth:
  https://www.greateasternlife.com/sg/en/personal-insurance/our-products/health-insurance/great-supremehealth-main.html
- Great Medical Care Concierge:
  https://www.greateasternlife.com/sg/en/customer-services/claims/medical-hospitalisation/gmcc.html
- GREAT SupremeHealth and GREAT TotalCare benefit schedule PDF:
  https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-ftrp-imc-cm/health-insurance-/great-supremehealth/april-2026/gels-pdt-pd-gsh-gtc-tob-eng.pdf

Source status: official Great Eastern Singapore product, claims, and benefit
schedule pages, not the full policy contract. Accessed 2026-07-04.

## Decision Rule

For a Singaporean taking planned medical care in China:

- Treat **GREAT SupremeHealth** as a Singapore MediSave-approved Integrated
  Shield Plan signal, not default medical-tourism coverage. Great Eastern
  describes it as complementing MediShield Life for higher ward classes and
  private hospitals.
- Treat **GREAT TotalCare 2** as a supplementary plan that can reduce
  out-of-pocket costs for eligible claims, but do not treat it as worldwide
  planned-care cover by itself.
- Treat **GREAT TotalCare Plus 2** as the key worldwide-coverage signal because
  Great Eastern describes it as a rider attached to Great TotalCare 2 that
  extends medical coverage worldwide, with overseas emergency and overseas
  non-emergency medical or surgical treatment benefits.
- For China planned treatment, confirm the rider is active, classify China as
  non-ASEAN for benefit handling, and check limits, deductibles, co-insurance,
  lifetime limits, and the lower-of-charge rule for non-emergency overseas
  treatment.
- Do not assume Great Medical Care Concierge, Letter of Guarantee, Certificate
  of Pre-Authorisation, or direct settlement applies in China. Great Eastern's
  GMCC FAQ states overseas treatment is not eligible for pre-approval; assume
  self-pay and e-file/manual claim unless Great Eastern confirms otherwise in
  writing.

## Source-Backed Signals

Use these as planning signals only:

- GREAT SupremeHealth is described as a MediSave-approved Integrated Shield
  Plan that consists of MediShield Life and additional private insurance.
- Great Eastern says Integrated Shield Plan private-insurer portions do not
  provide coverage for pre-existing conditions.
- GREAT TotalCare 2 is described as a supplementary plan with added benefits and
  reduced out-of-pocket expenses, subject to plan rules.
- GREAT TotalCare Plus 2 benefit tables include overseas emergency medical or
  surgical treatment and overseas non-emergency medical or surgical treatment.
- GREAT TotalCare Plus 2 overseas non-emergency benefits are split by ASEAN and
  non-ASEAN, with non-emergency charges limited to the lower of reasonable and
  customary charges in Singapore or where treatment is provided.
- Great Eastern describes GMCC as a 24/7 support pathway for coverage questions,
  referrals to panel specialists, and applications for pre-authorisation of
  eligible bills.
- The GMCC FAQ states overseas treatment is not eligible for pre-approval and
  that overseas treatment claims can be submitted by e-filing or manually.
- Great Eastern product pages and benefit schedules are not substitutes for the
  policy contract.

## Workflow

1. Identify the exact Great Eastern product.
   Ask whether the user has GREAT SupremeHealth, GREAT TotalCare 2, GREAT
   TotalCare Plus 2, a corporate plan, travel insurance, or another Great
   Eastern policy. Ask for plan type, rider schedule, insured status, and
   Singapore residency/citizenship details.

2. Classify the China care request.
   Separate emergency care from planned non-emergency care. Tag inpatient
   admission, day surgery/daypatient, outpatient consultation, diagnostics,
   cancer treatment, dental, vision, screening, maternity, rehabilitation,
   evacuation, or second opinion.

3. Match the benefit signal.
   For GREAT SupremeHealth alone, mark China planned care as
   `needs_confirmation`. For GREAT TotalCare Plus 2, check whether overseas
   emergency or overseas non-emergency medical/surgical treatment applies and
   whether China falls under non-ASEAN limits.

4. Verify limits and exclusions.
   Ask Great Eastern to confirm benefit limits, deductible, co-insurance,
   lifetime limits, reasonable-and-customary charge handling, pre-existing
   condition exclusions, waiting periods, and whether outpatient-only care is
   eligible.

5. Verify the payment pathway.
   Because GMCC states overseas treatment is not eligible for pre-approval, do
   not present PAC, LOG, or direct settlement as available for China unless
   Great Eastern confirms a written exception for the named hospital and
   treatment. Default to self-pay then claim.

6. Prepare claim evidence before travel.
   At minimum, plan for policy/member details, appointment confirmation,
   diagnosis certificate, doctor report, itemised invoice, official receipt,
   prescriptions, discharge/visit summary, procedure and diagnosis descriptions,
   proof of payment, and certified translation requirements if Chinese documents
   are used.

7. Mark unresolved items.
   If rider status, covered treatment type, overseas benefit limits, pre-approval
   status, or claim-document requirements are unknown, set data_status to
   `needs_confirmation` and add a blocking readiness item before any
   non-refundable booking.

## Questions To Ask Great Eastern Singapore

- Which Great Eastern product and riders are active: GREAT SupremeHealth, GREAT
  TotalCare 2, GREAT TotalCare Plus 2, corporate medical cover, or travel
  insurance?
- Is planned medical or surgical treatment in Mainland China covered, or only
  overseas emergency treatment?
- Does GREAT TotalCare Plus 2 apply to this treatment, and what non-ASEAN
  annual and lifetime benefit limits apply?
- Are outpatient consultation, diagnostics, medication, cancer treatment, dental,
  vision, screening, or rehabilitation benefits covered for China?
- Does the lower-of-reasonable-and-customary-charge rule apply to the planned
  non-emergency treatment?
- Is any pre-approval, Certificate of Pre-Authorisation, Letter of Guarantee, or
  direct settlement available for this named China hospital despite the GMCC FAQ
  saying overseas treatment is not eligible for pre-approval?
- Which documents, medical reports, cost estimates, diagnosis details, and
  procedure descriptions are required before treatment and for reimbursement?
- Do Chinese-language documents need certified translation or notarisation?

## Output Pattern

When producing provider guidance, include:

```json
{
  "provider_key": "great_eastern",
  "display_name": "Great Eastern Singapore",
  "policy_status": "needs_great_eastern_confirmation",
  "source_type": "official_product_claims_and_benefit_schedule_pages_not_policy_contract",
  "source_urls": [
    "https://www.greateasternlife.com/sg/en/personal-insurance/our-products/health-insurance/great-supremehealth-main.html",
    "https://www.greateasternlife.com/sg/en/customer-services/claims/medical-hospitalisation/gmcc.html",
    "https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-ftrp-imc-cm/health-insurance-/great-supremehealth/april-2026/gels-pdt-pd-gsh-gtc-tob-eng.pdf"
  ],
  "direct_billing_assumption": "overseas treatment is not eligible for GMCC pre-approval by default; assume self-pay then claim unless Great Eastern confirms otherwise",
  "preauthorization_required": true,
  "data_status": "needs_confirmation",
  "confidence_level": "medium"
}
```

## Safety Rules

- Do not say Great Eastern covers China medical care unless the user's policy
  contract and Great Eastern written confirmation support it.
- Do not treat GREAT SupremeHealth alone as planned medical tourism coverage.
- Do not infer China direct billing from Singapore GMCC, panel, PAC, or LOG
  workflows.
- Do not infer overseas non-emergency treatment coverage unless GREAT TotalCare
  Plus 2 or another worldwide rider is active and applicable.
- Do not recommend non-refundable travel or treatment booking until Great
  Eastern confirms benefit scope, claim route, hospital appointment, and claim
  documents.
