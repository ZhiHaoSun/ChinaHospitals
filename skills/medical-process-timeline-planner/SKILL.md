---
name: medical-process-timeline-planner
description: Create evidence-based, patient-facing day-by-day medical process timelines for planned care, medical travel, concierge medicine, or hospital package planning. Use for eye surgery such as cataract or LASIK, tooth or dental implant journeys, CAR-T therapy pathways, premium medical checkups, pre-treatment checklists, recovery calendars, post-surgery follow-up schedules, and questions asking how many days a patient usually needs for checkup, treatment, recovery, and post-procedure review.
---

# Medical Process Timeline Planner

## Overview

Use this skill to turn a planned medical service into a practical calendar: consultation days, required tests, treatment day, recovery window, and follow-up checkpoints. Always frame outputs as planning support, not medical advice.

## Source Standard

For medical facts, prefer current official or medically reviewed sources in this order:

1. The treating hospital's written protocol or patient pathway, when provided.
2. Government, regulator, or national clinical authority sources such as NEI, FDA, NCI, CDC, USPSTF, NHS, or NICE.
3. Specialty societies such as AAO, AAOMS, AAP, ACP, ACS, ASCO, ASTCT, or EBMT.
4. Peer-reviewed guidelines, systematic reviews, or medically reviewed major academic/clinical centers.

If no date is provided by the user, verify that time-sensitive recommendations are current. Name sources and dates in the output when timelines will be used for patient-facing or business materials.

## Reference Router

Read only the procedure file needed for the user's request:

- Eye surgery, cataract, LASIK, refractive surgery: `references/eye-surgery.md`
- Tooth implant, dental implant, sinus lift, bone graft, abutment/crown restoration: `references/tooth-implant.md`
- CAR-T, chimeric antigen receptor T-cell therapy, cellular immunotherapy: `references/car-t.md`
- Premium medical check, executive health screening, preventive checkup package: `references/premium-medical-check.md`

If the user asks for a combined medical travel package, read each relevant procedure file and merge timelines conservatively.

## Safety Boundaries

Do not diagnose, promise eligibility, guarantee outcomes, or replace clinician instructions. Make timelines conditional on surgeon, oncologist, dentist, anesthetist, and hospital protocol.

Flag emergency or urgent escalation instead of normal scheduling for:

- Eye surgery: vision loss, severe or worsening pain, very red eye, flashes/floaters, discharge, trauma, or rapidly worsening symptoms.
- Dental implant: uncontrolled bleeding, fever, spreading swelling, pus, severe pain not improving, numbness, breathing/swallowing difficulty, or implant mobility.
- CAR-T: fever, chills, confusion, seizure, severe headache, low blood pressure symptoms, breathing trouble, fast heart rate, severe vomiting/diarrhea, bleeding, or any sudden neurologic change.
- Medical checkup: chest pain, stroke symptoms, severe shortness of breath, fainting, severe abdominal pain, uncontrolled bleeding, or other acute symptoms.

## Timeline Workflow

1. Identify the procedure variant and patient context: age, sex at birth when relevant, diagnosis, surgery type, dental bone graft need, CAR-T product/pathway, travel origin, comorbidities, medications, and target hospital.
2. Select the matching reference file and baseline template.
3. Convert relative days into a readable itinerary. Use `Day 0` for the treatment event, infusion, surgery, or checkup start date.
4. Split the plan into `Before arrival`, `On-site care`, `Treatment day`, `Recovery`, `Follow-up`, and `Return-travel considerations`.
5. Add uncertainty ranges where protocols vary, for example "usually 24-48 hours" or "often 3-9 months for osseointegration."
6. Include required questions for the care team when a timeline depends on local protocol.
7. Cite the source basis in plain language. If source data conflicts, explain the conflict and default to the treating institution's protocol.

## Output Shape

For patient or medical-travel planning, use a compact table:

| Timing | Usual activity | Purpose | Planning notes |
| --- | --- | --- | --- |

Then add:

- `Typical minimum stay`: conservative estimate, with separate outpatient and high-risk versions if needed.
- `Cannot miss`: appointments or monitoring that should not be skipped.
- `Ask the hospital`: open protocol-dependent questions.
- `Urgent signs`: concise red flags.

## Evidence Notes

When generating a plan, include a short `Source basis` section:

- Name the highest-quality sources used.
- State the publication, review, or access date if available.
- Say where the patient's hospital protocol must override generic timelines.
- Call out assumptions such as uncomplicated cataract surgery, single-tooth implant without grafting, outpatient CAR-T pathway, or average-risk preventive screening.
