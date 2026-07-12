# MedTour AI Local API Test Report

Report ID: `rep_c1a8c6c4acc54ae794bf90df91ec5395`
Operation ID: `op_b50b549cc83e4b9ea5b21a666fe3e10a`
Status: `ready`
Generated options: `4`

## Test Intake

- Medical purpose: eye_surgery
- Procedure subtype: smile_pro
- Nationality: SG
- Departure city: Singapore
- Date range: 2026-08-12 to 2026-08-18
- Duration preference: 5_7_days
- Planner backend: local deterministic API planner

## City Options

### Best Overall: Shanghai

- Option ID: `opt_shanghai_best_overall`
- Hospital: Shanghai International Medical Center
- Required days: 6
- Total estimated cost: SGD 6,013
- Estimated net savings: SGD 187
- Flight: SQ830 from SIN to PVG, arrives 2026-08-12T13:30:00+08:00
- Hotel: Holiday Inn Shanghai Pudong Kangqiao, No. 1088 Xiuyan Road, Pudong New Area, Shanghai
- Nightly hotel rate: SGD 190 for 5 nights
- Key risks: Final treatment eligibility depends on in-person clinician assessment.; Flight and hotel prices are estimates until live booking confirmation.; Insurance coverage and hospital billing policy require insurer confirmation before booking.; Some medical suitability details still need user confirmation.

### Lowest Total Cost: Guangzhou

- Option ID: `opt_guangzhou_lowest_cost`
- Hospital: Guangdong Provincial People's Hospital International Clinic
- Required days: 6
- Total estimated cost: SGD 5,165
- Estimated net savings: SGD 1,035
- Flight: SQ850 from SIN to CAN, arrives 2026-08-12T13:30:00+08:00
- Hotel: The Garden Hotel Guangzhou, 368 Huanshi Dong Road, Yuexiu District, Guangzhou
- Nightly hotel rate: SGD 145 for 5 nights
- Key risks: Final treatment eligibility depends on in-person clinician assessment.; Flight and hotel prices are estimates until live booking confirmation.; Insurance coverage and hospital billing policy require insurer confirmation before booking.; Some medical suitability details still need user confirmation.

### Shortest Trip: Beijing

- Option ID: `opt_beijing_shortest_trip`
- Hospital: Peking Union Medical College Hospital International Medical Services
- Required days: 6
- Total estimated cost: SGD 6,422
- Estimated net savings: SGD 0
- Flight: SQ802 from SIN to PEK, arrives 2026-08-12T13:30:00+08:00
- Hotel: Sunworld Dynasty Hotel Beijing Wangfujing, 50 Wangfujing Avenue, Dongcheng District, Beijing
- Nightly hotel rate: SGD 185 for 5 nights
- Key risks: Final treatment eligibility depends on in-person clinician assessment.; Flight and hotel prices are estimates until live booking confirmation.; Insurance coverage and hospital billing policy require insurer confirmation before booking.; Some medical suitability details still need user confirmation.

### Strongest Medical Resources: Shenzhen

- Option ID: `opt_shenzhen_medical_strength`
- Hospital: University of Hong Kong-Shenzhen Hospital International Medical Center
- Required days: 6
- Total estimated cost: SGD 5,617
- Estimated net savings: SGD 583
- Flight: ZH9024 from SIN to SZX, arrives 2026-08-12T13:30:00+08:00
- Hotel: The Langham Shenzhen, 7888 Shennan Boulevard, Futian District, Shenzhen
- Nightly hotel rate: SGD 175 for 5 nights
- Key risks: Final treatment eligibility depends on in-person clinician assessment.; Flight and hotel prices are estimates until live booking confirmation.; Insurance coverage and hospital billing policy require insurer confirmation before booking.; Some medical suitability details still need user confirmation.

## Selected Plan Detail

Selected option: `opt_shanghai_best_overall` (Shanghai)

### Cost Breakdown

- Medical: SGD 3,900 (range 3,200-4,600)
- Flight: SGD 520
- Hotel: SGD 950
- Local Transport: SGD 168
- Meals: SGD 290
- Visa And Payment Setup: SGD 90
- Travel Insurance: SGD 95
- Total: SGD 6,013

### Original Timeline

#### Day 1: Arrival and Check-in (2026-08-12)

- 08:00-13:30: Arrival flight at PVG, cost SGD 520
- 14:00-15:00: Airport transfer to hotel at Shanghai, cost SGD 48
- 15:30-16:00: Hotel check-in at Holiday Inn Shanghai Pudong Kangqiao

#### Day 2: Pre-treatment Evaluation (2026-08-13)

- 08:30-09:00: International desk registration and outpatient file setup at Shanghai International Medical Center [medical constraint]
- 09:00-09:30: Nurse intake, consent forms, and payment/pre-auth check at Shanghai International Medical Center [medical constraint]
- 09:30-11:30: Diagnostics and program-specific tests at Shanghai International Medical Center [medical constraint]
- 14:00-15:30: Suggested doctor consultation and eligibility confirmation at Shanghai International Medical Center [medical constraint]
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 58

#### Day 3: Core Medical Appointment (2026-08-14)

- 08:45-09:30: Final consent, deposit, and treatment-room preparation at Shanghai International Medical Center [medical constraint]
- 09:30-12:00: Procedure or core medical appointment at Shanghai International Medical Center [medical constraint]
- 12:00-12:45: Medication, discharge briefing, and claim documents at Shanghai International Medical Center [medical constraint]
- 14:00-18:00: Rest window near hospital at Holiday Inn Shanghai Pudong Kangqiao [medical constraint]
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 58

#### Day 4: Follow-up Review (2026-08-15)

- 09:30-10:30: Follow-up review with assigned doctor or international clinic at Shanghai International Medical Center [medical constraint]
- 11:00-11:30: Confirm return fitness, invoices, and insurance documents at Shanghai International Medical Center
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 58

#### Day 5: Recovery and Light City Time (2026-08-16)

- 10:30-13:00: Light recovery-friendly sightseeing at Shanghai, cost SGD 58
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 58

#### Day 6: Return Travel (2026-08-17)

- 10:30-11:00: Hotel check-out at Holiday Inn Shanghai Pudong Kangqiao
- 12:00-13:00: Transfer to airport at Shanghai, cost SGD 48
- 15:30-21:00: Return flight at PVG, cost SGD 520


### Regenerated Timeline

- New timeline version: `tlv_d1bbf9a7487c4b6f948db32342959429`
- Accept status: `accepted`
- Changes: Stay length changed from 6 to 8 days.; Flight preference applied: avoid_red_eye.; Hotel tier preference applied: balanced.

#### Day 1: Arrival and Check-in (2026-08-12)

- 08:00-13:30: Arrival flight at PVG, cost SGD 520
- 14:00-15:00: Airport transfer to hotel at Shanghai, cost SGD 48
- 15:30-16:00: Hotel check-in at Holiday Inn Shanghai Pudong Kangqiao

#### Day 2: Pre-treatment Evaluation (2026-08-13)

- 08:30-09:00: International desk registration and outpatient file setup at Shanghai International Medical Center [medical constraint]
- 09:00-09:30: Nurse intake, consent forms, and payment/pre-auth check at Shanghai International Medical Center [medical constraint]
- 09:30-11:30: Diagnostics and program-specific tests at Shanghai International Medical Center [medical constraint]
- 14:00-15:30: Suggested doctor consultation and eligibility confirmation at Shanghai International Medical Center [medical constraint]
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 58

#### Day 3: Core Medical Appointment (2026-08-14)

- 08:45-09:30: Final consent, deposit, and treatment-room preparation at Shanghai International Medical Center [medical constraint]
- 09:30-12:00: Procedure or core medical appointment at Shanghai International Medical Center [medical constraint]
- 12:00-12:45: Medication, discharge briefing, and claim documents at Shanghai International Medical Center [medical constraint]
- 14:00-18:00: Rest window near hospital at Holiday Inn Shanghai Pudong Kangqiao [medical constraint]
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 58

#### Day 4: Follow-up Review (2026-08-15)

- 09:30-10:30: Follow-up review with assigned doctor or international clinic at Shanghai International Medical Center [medical constraint]
- 11:00-11:30: Confirm return fitness, invoices, and insurance documents at Shanghai International Medical Center
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 58

#### Day 5: Recovery and Light City Time (2026-08-16)

- 10:30-13:00: Light recovery-friendly sightseeing at Shanghai, cost SGD 58
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 58

#### Day 6: Recovery and Light City Time (2026-08-17)

- 10:30-13:00: Light recovery-friendly sightseeing at Shanghai, cost SGD 58
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 58

#### Day 7: Recovery and Light City Time (2026-08-18)

- 10:30-13:00: Light recovery-friendly sightseeing at Shanghai, cost SGD 58
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 58

#### Day 8: Return Travel (2026-08-19)

- 10:30-11:00: Hotel check-out at Holiday Inn Shanghai Pudong Kangqiao
- 12:00-13:00: Transfer to airport at Shanghai, cost SGD 48
- 15:30-21:00: Return flight at PVG, cost SGD 520


## Readiness Checklist

Completion before update: 0%
Updated item: `alipay_setup` -> `complete`

### Confirm visa or visa-free entry status

- Priority: medium
- Status: pending
- Steps: Check the latest Chinese embassy or consulate entry policy for your passport.; Confirm passport validity, blank visa pages, and onward/return ticket requirements.; Prepare hotel booking, hospital appointment proof, and travel insurance documents.; Do not book non-refundable travel until entry status and medical appointment are confirmed.
- Links: Chinese Visa Application Service Center (https://www.visaforchina.cn/); National Immigration Administration of China (https://en.nia.gov.cn/)

### Install and configure Alipay international version

- Priority: high
- Status: pending
- Steps: Install Alipay from the iOS App Store or Google Play before departure.; Register with the same mobile number you will use while traveling.; Link an international Visa, Mastercard, JCB, Diners Club, Discover, or supported card.; Complete identity verification if prompted.; Enable location and notifications for smoother merchant payments.; Bring a backup card and some cash because not every merchant supports foreign cards.
- Links: Alipay international user guide (https://render.alipay.com/p/yuyan/180020010001196791/index.html); Alipay TourCard and payment help (https://www.alipayplus.com/)

### Confirm hospital appointment and required documents

- Priority: high
- Status: pending
- Steps: Confirm appointment date and department.; Ask whether translator or international desk support is available.; Prepare prior test reports and medication list if relevant.
- Links: None

### Confirm insurance coverage and hospital claim requirements

- Priority: high
- Status: pending
- Steps: Add your current insurance holder so the advisor can check policy-specific requirements.; Ask your insurer whether planned overseas treatment in Mainland China is covered before booking.; Request written pre-authorization or guarantee-of-payment instructions for the selected hospital.; Confirm whether outpatient treatment, follow-up visits, and complications are covered.; Keep itemized invoices, medical reports, prescriptions, receipts, and discharge or visit summaries.
- Links: None

### Verify sources and live prices before booking

- Priority: high
- Status: pending
- Steps: Review hospital source, international department, appointment contact, and insurance handling.; Re-check flight fare for exact route, date, cabin, baggage, and refund rules.; Re-check hotel nightly rate, subtotal, taxes, cancellation policy, and foreign-guest eligibility.; Reconcile total estimate against itemized medical, travel, hotel, insurance, and local costs.; Resolve 2 blocking audit items and review 2 warnings before any non-refundable booking.
- Links: None

## Advisor Handoff

- Lead ID: `lead_a23a7d0164e54e63bde8926b050c292e`
- Lead status: `new`

## Disclaimers

- This plan is for travel and budgeting support only and is not medical diagnosis.
- Procedure eligibility, final price, and appointment availability must be confirmed by the hospital or licensed clinician.
- Visa and entry policies can change; verify official sources before booking non-refundable travel.
- Insurance coverage, direct billing, and reimbursement eligibility must be confirmed by the insurer and hospital.
