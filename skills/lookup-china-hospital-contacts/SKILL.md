---
name: lookup-china-hospital-contacts
description: Use when looking up, verifying, or auditing registration emails, contact persons, appointment routes, phone numbers, WeChat/mini-program paths, or international department contacts for hospitals in Mainland China, especially for foreign patients, international medical centers, VIP clinics, specialty departments, dental implants, oncology, ophthalmology, or medical travel planning.
---

# Lookup China Hospital Contacts

## Purpose

Use this skill to find and verify the best contact path for a China hospital
international department or specialty department. Prioritize registration email,
contact person, appointment phone, WeChat/mini-program route, and evidence that
the contact belongs to the official hospital or affiliated university hospital.
Also verify service billing, direct-billing assumptions, deposit/payment route,
insurance-service page, and claim-document route when those details affect a
medical travel recommendation.

Never treat an email or named contact as verified unless it is published on an
official source or confirmed by an official hospital phone line or official
WeChat account.

For known source examples and the reusable evidence schema, read
`references/source-registry.md` when the target hospital is PUMCH, HKU-Shenzhen
Hospital, Guangdong Provincial People's Hospital, Shanghai International Medical
Center, or when designing ingestion records.

## Source Authority Ranking

Use this authority order when deciding whether a contact is reliable:

1. Official hospital website on the hospital or university domain.
2. Official hospital English site, international department page, VIP clinic
   page, or specialty department page.
3. Official hospital WeChat service account, subscription account, mini-program,
   Alipay life account, or hospital app.
4. Official university, medical school, health commission, or hospital group
   page that links to the hospital.
5. Main switchboard or department phone confirmation from an official page.
6. Insurer provider directory or embassy hospital list as a lead only.
7. Third-party medical tourism pages, directory listings, blogs, maps, or social
   posts as leads only; never final proof.

Reject or downgrade contacts found only on scraped directories, SEO clinic
pages, unverified social media posts, or generic email domains unless the
official hospital source also publishes the same contact.

## Search Workflow

1. Define the target.
   Capture city, hospital name if known, treatment need, specialty department,
   patient language, nationality/residence, and whether the request is planned
   care, urgent care, second opinion, or estimate request.

2. Search official English sources first.
   Try queries such as:
   - `<hospital name> international department email`
   - `<hospital name> international medical center appointment`
   - `<hospital name> contact us English`
   - `<city> <specialty> international hospital appointment email`

3. Search official Chinese sources.
   Use Chinese terms and the city/specialty:
   - `医院 国际部 邮箱`
   - `医院 国际医疗部 预约 邮箱`
   - `医院 外宾门诊 联系方式`
   - `医院 特需门诊 预约 电话`
   - `医院 国际门诊 联系人`
   - `<城市> <专科> 国际部 预约`
   - `<医院名> 联系我们 邮箱`

4. Search within official domains.
   Use `site:` queries against the hospital, university, and hospital group
   domains. Look for pages titled `Contact Us`, `For Patients`, `Departments`,
   `International Medical Center`, `VIP Clinic`, `Appointment Guide`, or Chinese
   equivalents such as `联系我们`, `就医指南`, `预约挂号`, `国际部`, `特需门诊`.

5. Check specialty fit.
   Confirm that the hospital has the relevant specialty department. For example,
   dental implant planning should verify an implant dentistry, stomatology,
   prosthodontics, oral surgery, international dental center, or VIP dental
   service page.

6. Identify the appointment route.
   China hospitals often prefer WeChat, mini-program, app, Alipay, phone, or
   onsite service desk instead of email. Record the official route even when an
   email exists.

7. Verify service billing and insurance handling.
   Record whether the official source describes VIP/IMC billing, direct
   settlement, insurance partners, deposit/payment expectations, invoice
   documents, or claim-document collection. If billing is not explicit, mark
   `service_billing_status` as `needs_confirmation`.

8. Verify contact person claims.
   Accept a contact person only when the official hospital source names them as
   a coordinator, international patient contact, department secretary, case
   manager, doctor, nurse, or service desk lead. If the source lists only a
   doctor, label that person as clinical contact, not registration coordinator.

9. Cross-check before finalizing.
   A contact is high confidence only if at least two official signals agree, for
   example an international department page plus a Contact Us page, or a WeChat
   appointment guide plus the official main switchboard.

## Contact Acceptance Rules

Classify each candidate contact:

- `verified_registration_email`: official source explicitly says the email is
  for appointment, registration, international patients, or the target
  department.
- `official_general_email`: official hospital email exists, but appointment
  usage is not explicit.
- `verified_phone_route`: official source gives a phone number for appointment,
  registration, department inquiries, or international services.
- `verified_wechat_route`: official source directs patients to a WeChat account,
  mini-program, Alipay life account, app, or official appointment portal.
- `verified_billing_route`: official source describes the international/VIP
  service billing, direct settlement, insurance, deposit, or invoice route.
- `unverified_lead`: found on third-party or indirect sources only.
- `rejected`: source is unofficial, stale, inconsistent, or unsafe.

Use these confidence levels:

- `high`: official registration/international department email or contact person
  found, with at least one additional official corroborating signal.
- `medium`: official hospital email or phone is found, but not explicitly tied
  to international registration or the target specialty.
- `low`: only third-party leads or indirect references exist.
- `blocked`: no official contact path found.

## Data To Capture

For every hospital contact lookup, record:

- hospital English and Chinese names
- city and campus/branch
- specialty and department fit
- registration email if found
- contact person and role if found
- appointment phone and main switchboard
- WeChat/mini-program/app/Alipay appointment route
- service billing route, direct billing status, deposit/payment notes,
  insurance partners, and claim-document requirements if found
- official source URLs and page titles
- date checked
- source authority level
- confidence level
- whether the email is general, registration-specific, or unverified
- next verification step

## Output Pattern

Return concise structured evidence before recommendations:

```json
{
  "hospital": "Hospital English name",
  "hospital_chinese": "医院中文名",
  "city": "Guangzhou",
  "campus_or_branch": "Tianhe Campus",
  "service": "Dental implant consultation",
  "department": "International Dental Medical Center / Implant Dentistry",
  "registration_email": null,
  "email_status": "not_found",
  "contact_person": null,
  "contact_person_status": "not_found",
  "appointment_phone": "+86...",
  "main_phone": "+86...",
  "wechat_or_portal_route": "Official account > Outpatient Services > Appointment",
  "service_billing": {
    "service_billing_status": "needs_confirmation",
    "direct_billing_status": "unknown",
    "insurance_partners": [],
    "payment_or_deposit_notes": [],
    "claim_documents": []
  },
  "confidence": "medium",
  "source_records": [
    {
      "url": "https://official-hospital.example/contact",
      "title": "Contact Us",
      "source_type": "official_hospital_website",
      "fields_verified": ["main_phone", "address"]
    }
  ],
  "source_urls": [
    "https://official-hospital.example/contact",
    "https://official-hospital.example/department"
  ],
  "source_authority": "official_hospital_website",
  "date_checked": "YYYY-MM-DD",
  "next_verification_step": "Call the official appointment line to confirm whether the email can handle international registration."
}
```

## Email Verification Template

Use a short message when asking the hospital to confirm the route:

```text
Subject: Appointment route confirmation - [specialty] - international patient

Dear [Hospital/Department],

I would like to confirm the correct appointment route for an international
patient seeking [service] at [department/campus].

Could you please confirm:
1. Is this email accepted for appointment registration?
2. Is there a named coordinator or contact person for international patients?
3. Which phone number, WeChat mini-program, or portal should be used?
4. What documents are required before the first appointment?
5. Are English medical records accepted, or is Chinese translation required?
6. Which billing, deposit, direct settlement, invoice, and claim-document route
   applies to international/self-pay/insured patients?

Thank you.
```

## Safety Rules

- Do not invent a registration email from a contact form, domain pattern, or
  staff name.
- Do not list a contact person unless an official source names the person and
  role.
- Do not promote a third-party broker as the hospital contact.
- Do not treat a hospital's general email as registration-specific unless the
  official page says so.
- Do not infer direct billing, insurance acceptance, deposits, or service fees
  from a general hospital page. Require an official billing/insurance page or
  phone/email confirmation.
- Do not recommend non-refundable travel or treatment booking until the hospital
  appointment route, department fit, required documents, and payment/deposit
  expectations are confirmed.
