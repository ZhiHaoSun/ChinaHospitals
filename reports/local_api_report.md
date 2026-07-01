# MedTour AI Local API Test Report

Report ID: `rep_d9d83ad6b6904d0da6ad4193512d485a`
Operation ID: `op_d01ae0b7695b4d7eaf8a98c67b25ecb2`
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
- Total estimated cost: SGD 6,840
- Estimated net savings: SGD 2,599
- Flight: SQ830 from SIN to PVG, arrives 2026-08-12T13:30:00+08:00
- Hotel: Shanghai Medical District Hotel, No. 1188 Fangdian Road, Pudong, Shanghai
- Nightly hotel rate: SGD 165 for 5 nights
- Key risks: Final treatment eligibility depends on in-person clinician assessment.; Flight and hotel prices are estimates until live booking confirmation.; Some medical suitability details still need user confirmation.

### Lowest Total Cost: Guangzhou

- Option ID: `opt_guangzhou_lowest_cost`
- Hospital: Guangdong Provincial People's Hospital International Clinic
- Required days: 6
- Total estimated cost: SGD 5,790
- Estimated net savings: SGD 2,200
- Flight: SQ850 from SIN to CAN, arrives 2026-08-12T13:30:00+08:00
- Hotel: Guangzhou Medical District Hotel, No. 106 Zhongshan 2nd Road, Yuexiu, Guangzhou
- Nightly hotel rate: SGD 165 for 5 nights
- Key risks: Final treatment eligibility depends on in-person clinician assessment.; Flight and hotel prices are estimates until live booking confirmation.; Some medical suitability details still need user confirmation.

### Shortest Trip: Beijing

- Option ID: `opt_beijing_shortest_trip`
- Hospital: Peking Union Medical College Hospital International Medical Services
- Required days: 6
- Total estimated cost: SGD 7,090
- Estimated net savings: SGD 2,694
- Flight: SQ802 from SIN to PEK, arrives 2026-08-12T13:30:00+08:00
- Hotel: Beijing Medical District Hotel, No. 1 Shuaifuyuan, Dongcheng, Beijing
- Nightly hotel rate: SGD 165 for 5 nights
- Key risks: Final treatment eligibility depends on in-person clinician assessment.; Flight and hotel prices are estimates until live booking confirmation.; Some medical suitability details still need user confirmation.

### Strongest Medical Resources: Shenzhen

- Option ID: `opt_shenzhen_medical_strength`
- Hospital: University of Hong Kong-Shenzhen Hospital International Medical Center
- Required days: 6
- Total estimated cost: SGD 6,090
- Estimated net savings: SGD 2,314
- Flight: ZH9024 from SIN to SZX, arrives 2026-08-12T13:30:00+08:00
- Hotel: Shenzhen Medical District Hotel, No. 1 Haiyuan 1st Road, Futian, Shenzhen
- Nightly hotel rate: SGD 165 for 5 nights
- Key risks: Final treatment eligibility depends on in-person clinician assessment.; Flight and hotel prices are estimates until live booking confirmation.; Some medical suitability details still need user confirmation.

## Selected Plan Detail

Selected option: `opt_shanghai_best_overall` (Shanghai)

### Cost Breakdown

- Medical: SGD 5,500 (range 4,200-6,800)
- Flight: SGD 520
- Hotel: SGD 825
- Local Transport: SGD 210
- Meals: SGD 225
- Visa And Payment Setup: SGD 80
- Total: SGD 6,840

### Original Timeline

#### Day 1: Arrival and Check-in (2026-08-12)

- 08:00-13:30: Arrival flight at PVG, cost SGD 520
- 14:00-15:00: Airport transfer to hotel at Shanghai, cost SGD 35
- 15:30-16:00: Hotel check-in at Shanghai Medical District Hotel

#### Day 2: Pre-treatment Evaluation (2026-08-13)

- 09:00-11:30: Pre-treatment examination at Shanghai International Medical Center [medical constraint]
- 14:00-15:30: Doctor review and eligibility confirmation at Shanghai International Medical Center [medical constraint]
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 45

#### Day 3: Core Medical Appointment (2026-08-14)

- 09:30-12:00: Procedure or core medical appointment at Shanghai International Medical Center [medical constraint]
- 14:00-18:00: Rest window near hospital at Shanghai Medical District Hotel [medical constraint]
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 45

#### Day 4: Follow-up Review (2026-08-15)

- 09:30-10:30: Follow-up review at Shanghai International Medical Center [medical constraint]
- 11:00-11:30: Confirm return fitness and documents at Shanghai International Medical Center
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 45

#### Day 5: Recovery and Light City Time (2026-08-16)

- 10:30-13:00: Light recovery-friendly sightseeing at Shanghai, cost SGD 45
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 45

#### Day 6: Return Travel (2026-08-17)

- 10:30-11:00: Hotel check-out at Shanghai Medical District Hotel
- 12:00-13:00: Transfer to airport at Shanghai, cost SGD 35
- 15:30-21:00: Return flight at PVG, cost SGD 520


### Regenerated Timeline

- New timeline version: `tlv_462d21c7bda7424f84e97a6e88165cdb`
- Accept status: `accepted`
- Changes: Stay length changed from 6 to 8 days.; Flight preference applied: avoid_red_eye.; Hotel tier preference applied: balanced.

#### Day 1: Arrival and Check-in (2026-08-12)

- 08:00-13:30: Arrival flight at PVG, cost SGD 520
- 14:00-15:00: Airport transfer to hotel at Shanghai, cost SGD 35
- 15:30-16:00: Hotel check-in at Shanghai Medical District Hotel

#### Day 2: Pre-treatment Evaluation (2026-08-13)

- 09:00-11:30: Pre-treatment examination at Shanghai International Medical Center [medical constraint]
- 14:00-15:30: Doctor review and eligibility confirmation at Shanghai International Medical Center [medical constraint]
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 45

#### Day 3: Core Medical Appointment (2026-08-14)

- 09:30-12:00: Procedure or core medical appointment at Shanghai International Medical Center [medical constraint]
- 14:00-18:00: Rest window near hospital at Shanghai Medical District Hotel [medical constraint]
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 45

#### Day 4: Follow-up Review (2026-08-15)

- 09:30-10:30: Follow-up review at Shanghai International Medical Center [medical constraint]
- 11:00-11:30: Confirm return fitness and documents at Shanghai International Medical Center
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 45

#### Day 5: Recovery and Light City Time (2026-08-16)

- 10:30-13:00: Light recovery-friendly sightseeing at Shanghai, cost SGD 45
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 45

#### Day 6: Recovery and Light City Time (2026-08-17)

- 10:30-13:00: Light recovery-friendly sightseeing at Shanghai, cost SGD 45
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 45

#### Day 7: Recovery and Light City Time (2026-08-18)

- 10:30-13:00: Light recovery-friendly sightseeing at Shanghai, cost SGD 45
- 18:00-19:00: Recovery-friendly meals at Shanghai, cost SGD 45

#### Day 8: Return Travel (2026-08-19)

- 10:30-11:00: Hotel check-out at Shanghai Medical District Hotel
- 12:00-13:00: Transfer to airport at Shanghai, cost SGD 35
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

## Advisor Handoff

- Lead ID: `lead_f742b49f5d214d60ae4133e81794b31a`
- Lead status: `new`

## Disclaimers

- This plan is for travel and budgeting support only and is not medical diagnosis.
- Procedure eligibility, final price, and appointment availability must be confirmed by the hospital or licensed clinician.
- Visa and entry policies can change; verify official sources before booking non-refundable travel.
