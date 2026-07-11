# China Hospital International Department Source Registry

Use these examples as seed records and ingestion patterns. A seed record is not
automatically bookable: preserve `date_checked`, source URLs, and verification
status, then refresh before customer-facing booking.

## Evidence Schema

Required fields:

- `hospital`, `hospital_chinese`, `city`, `campus_or_branch`
- `international_department_name`
- `official_domains`
- `department_or_service`
- `registration_email`, `email_status`
- `contact_person`, `contact_person_status`
- `appointment_phone`, `main_phone`
- `wechat_or_portal_route`
- `service_billing_status`, `direct_billing_status`
- `insurance_partners`, `payment_or_deposit_notes`, `claim_documents`
- `source_records`, each with `url`, `title`, `source_type`, `fields_verified`
- `confidence`, `date_checked`, `next_verification_step`

## Seed Records Checked 2026-07-11

### Peking Union Medical College Hospital

- Hospital: Peking Union Medical College Hospital
- Chinese name: 北京协和医院
- City: Beijing
- International route: International Medical Services
- Official domain: `pumch.cn`
- Appointment/contact evidence:
  - `https://www.pumch.cn/en.html` lists official campus addresses and phone numbers.
  - `https://www.pumch.cn/en/new_about.html` lists International Medical Services contact details.
- Candidate registration email: `ims@pumch.cn`
- Email status: `verified_registration_email` for International Medical Services, but refresh before use.
- Appointment phone: `+86-10-69156699`
- Main phones: `010-69151188`, `010-69158100`, `010-69153456`
- Billing status: `needs_confirmation`; no direct-settlement rule was verified in this pass.
- Confidence: `high` for international service contact route, `medium` for billing.
- Next step: email/call IMS to confirm target specialty, document requirements, deposit/payment route, and insurance handling.

### The University of Hong Kong-Shenzhen Hospital

- Hospital: The University of Hong Kong-Shenzhen Hospital
- Chinese name: 香港大学深圳医院
- City: Shenzhen
- International route: IMC / International Medical Center
- Official domain: `hku-szh.org`
- Appointment/contact evidence:
  - `https://www.hku-szh.org/en/index.html` exposes the IMC section and patient booking pages.
  - `https://www.hku-szh.org/en/PatientInfo/BookingService/BookingGuidelines/content/post_818462.html` lists WeChat, 91160, English hotline, IMC Shenzhen hotline, and Hong Kong hotline.
- Registration email: `null`
- Email status: `not_found`
- WeChat or portal route: WeChat official account `The University of Hong Kong Shenzhen Hospital` / ID `hkuszh`; 91160 unit page.
- Appointment phone: English general outpatient `0755-86913366`; IMC Shenzhen `0755-86913388`; IMC Hong Kong `+852-67053932`
- Billing status: `needs_confirmation`; IMC insurance pages exist but billing terms must be checked for the selected service.
- Confidence: `high` for appointment route, `medium` for billing.
- Next step: call IMC to confirm specialty availability, language support, deposit, invoice, direct settlement, and claim documents.

### Guangdong Provincial People's Hospital

- Hospital: Guangdong Provincial People's Hospital
- Chinese name: 广东省人民医院
- City: Guangzhou
- International/VIP route: Concord Medical Center
- Official domain: `gdghospital.org.cn`
- Appointment/contact evidence:
  - `https://www.gdghospital.org.cn/en/` lists English navigation, contact information, outpatient appointment, and Concord Medical Center.
  - `https://www.gdghospital.org.cn/en/outpatientservices/index.html` lists official portal, WeChat account, third-party appointment sites, appointment phones, onsite registration, and self-service.
  - `https://www.gdghospital.org.cn/en/CenterIntroduced/index.html` describes Concord Medical Center as a VIP center serving foreigners and lists phone/email.
  - `https://www.gdghospital.org.cn/en/contactus/index.html` lists general hospital phone/address.
- Candidate email: `gdcmc@yahoo.cn`
- Email status: `official_general_email` because it is published by the official Concord Medical Center page, but not explicitly described as appointment registration.
- Appointment phone: Concord Medical Center `(+8620) 83874283`, `(+8620) 87374289-8991`; outpatient appointment `020-83882222`, `020-12320`, `400-6677-400`
- Main phone: `+8620-83827812`
- Billing status: `needs_confirmation`; direct-settlement page exists in navigation, but service-specific terms need confirmation.
- Confidence: `high` for center identity and contact route, `medium` for registration email and billing.
- Next step: confirm whether Concord Medical Center accepts the email for appointment, and request deposit, direct settlement, invoice, and claim-document instructions.

### Shanghai International Medical Center

- Hospital: Shanghai International Medical Center
- Chinese name: 上海国际医学中心
- City: Shanghai
- Status: `blocked`
- Evidence: official source was not reliably verified in this pass; search results were noisy and candidate sites were inaccessible.
- Registration email: `null`
- Email status: `not_found`
- Billing status: `needs_confirmation`
- Confidence: `blocked`
- Next step: manually verify official website/domain, appointment route, registration phone, billing desk, and insurance handling before including in customer-facing output.
