"""ADK multi-agent graph for MedTour AI.

Run with ADK tooling by pointing at this package and using `root_agent`.
The graph uses OpenAI through LiteLLM, so set OPENAI_API_KEY before running.
"""

from __future__ import annotations

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.models.lite_llm import LiteLlm

from medtour_ai.agents.config import get_settings
from medtour_ai.agents.tools import (
    audit_city_option_sources_and_costs,
    estimate_flights,
    estimate_trip_costs,
    get_alipay_international_setup,
    get_hospital_insurance_policy,
    get_hospital_visit_protocol,
    get_today,
    get_visa_entry_guidance,
    lookup_china_hospital_contact_guidance,
    lookup_insurance_provider_policy,
    retrieve_medical_rules,
    search_hospital_city_candidates,
    search_hotels,
)

settings = get_settings()


def _model(name: str | None = None) -> LiteLlm:
    return LiteLlm(model=name or settings.llm_model)


COMMON_OUTPUT_RULES = """
Output rules:
- Return valid JSON only. Do not wrap JSON in Markdown.
- Include source, freshness, confidence_level, and data_status for generated medical, travel, cost, visa, payment, and insurance claims.
- Mark live provider data and official-source checks separately from representative planning estimates.
- Do not provide diagnosis or guarantee treatment eligibility.
- Ask for user confirmation when a decision is uncertain or has multiple reasonable choices.
- Do not request passport number, payment card number, CVV, OTP, or payment password.
- Use the user's preferred currency when provided; otherwise use SGD.
"""


profile_agent = LlmAgent(
    name="user_profiler_agent",
    model=_model(),
    description="Normalizes guided intake answers into a planning profile.",
    instruction=f"""
You are the User Profiler Agent for MedTour AI.

Input is a JSON object of guided intake answers from a web platform. Normalize it
into a compact planning profile with:
- medical purpose and procedure subtype
- adaptive program details such as prescription, teeth count, screening focus,
  treatment area, imaging status, contact lens usage, or downtime tolerance
- nationality, residence country, departure city
- current insurance holder, if provided
- planned date mode and date constraints
- acceptable duration
- season flexibility, including winter/off-season preference
- budget tier, traveler count, hotel preference, tourism intensity
- fields that are user_confirmed, system_default, or needs_confirmation
- confirmation questions only when the missing answer changes plan quality

Use short confirmation questions with at most three choices.

{COMMON_OUTPUT_RULES}

Required JSON keys:
profile, field_status, defaults, confirmation_requests, assumptions.
""",
    tools=[get_today],
    output_key="profile_summary",
)


medical_shortlist_agent = LlmAgent(
    name="medical_city_shortlist_agent",
    model=_model(settings.planner_model),
    description="Finds eligible China city and hospital candidates.",
    instruction=f"""
You are the Medical Consultant Agent.

Use the normalized profile from state key `profile_summary`. Call tools to get:
1. medical planning rules
2. candidate cities and hospitals

Generate a city shortlist for up to four China cities. Each candidate must
explain why it fits the medical purpose, expected care cycle, service language
considerations, appointment uncertainty, hospital insurance handling hints, and
any medical hard constraints.

When evaluating hospitals in China, prefer the hospital's 国际部, international
department, International Medical Center, International Medical Services,
international clinic, VIP clinic, or foreign-patient service desk when one is
available. Treat the international section as the target care pathway, not just
as a note. If a hospital has no clear international section, explain that gap and
lower confidence for international visitor suitability.

Prefer a diversified set:
- high medical strength
- best overall
- lower total cost
- easiest/shortest travel

{COMMON_OUTPUT_RULES}

Required JSON keys:
medical_rules, city_shortlist, medical_hard_constraints, insurance_policy_notes,
confirmation_requests.
""",
    tools=[retrieve_medical_rules, search_hospital_city_candidates],
    output_key="medical_shortlist",
)


def _city_option_agent(name: str, strategy: str, output_key: str) -> LlmAgent:
    return LlmAgent(
        name=name,
        model=_model(settings.planner_model),
        description=f"Generates one city option optimized for {strategy}.",
        instruction=f"""
You are a City Option Planning Agent optimized for: {strategy}.

Use state keys `profile_summary` and `medical_shortlist`. Pick one city from
the shortlist that best matches this strategy. If another option agent might
choose the same city, still optimize for your strategy and clearly explain the
trade-off; the final ranking agent will deduplicate if needed.

For the selected city, call tools to estimate:
- flights with flight number, airline, departure/arrival time, and cost
- foreigner-friendly hotel choice with address, nightly price, nights, and policy
- detailed trip cost breakdown
- visa/entry guidance
- Alipay international setup guidance
- hospital-specific insurance policy, including current insurer fit,
  pre-authorization, direct billing, claim documents, exclusions, and suggested actions
- provider-specific insurance lookup guidance for popular insurers such as
  Cigna, AIA, Bupa, Allianz, and AXA using the user's current insurance holder
- China hospital contact lookup guidance from the lookup-china-hospital-contacts
  skill before trusting any registration email, contact person, appointment
  phone, WeChat route, service billing, direct-billing status, or international
  department appointment pathway
- hospital visit protocol, including international registration desk, official
  registration email status, suggested doctor or doctor-assignment request,
  diagnostics, consultation, procedure, billing/deposit confirmation, discharge,
  and claim-document steps
- add insurance premium estimate to cost_breakdown.travel_insurance and include it
  in total_estimated_cost and estimated_net_savings calculations

Before writing insurance_policy, call `lookup_insurance_provider_policy` with
the user's current insurance holder, then call `get_hospital_insurance_policy`.
Merge both results. Mention provider-specific pre-authorization questions,
direct-billing assumptions, claim documents, and risk flags. If the provider is
unknown or not supported, ask for insurer name, issuing country, plan type, and
policy territory instead of guessing coverage.

Before writing hospital_visit_protocol or any timeline registration email,
contact person, phone, or WeChat/app route, call
`lookup_china_hospital_contact_guidance` with the selected hospital, city,
medical purpose, and target international department/service. Apply the
lookup-china-hospital-contacts skill rules:
- accept registration email only when an official hospital/university source
  explicitly ties it to appointment, registration, international patients, or
  the target department
- mark official general hospital email as official_general_email, not verified
  registration email
- accept contact person only when an official source names the person and role
- prefer official WeChat/mini-program/app/phone routes when the hospital
  appointment guide uses those instead of email
- use seed_official_sources from the lookup tool only as source-backed leads;
  refresh before non-refundable booking and preserve date_checked/source_records
- record service_billing, direct_billing_status, insurance_partners,
  payment_or_deposit_notes, and claim_documents; mark missing billing evidence
  as needs_confirmation instead of guessing
- include contact_lookup_guidance and contact_verification_status in
  audit_inputs

Choose the hospital's 国际部 / international section whenever available. The
target_hospital value should name the international section or international
patient pathway, not only the parent hospital. Preserve any international visitor
policy, service language, appointment desk, direct-billing, and insurance
coverage notes from the shortlist. Only use a standard domestic department when
no credible international section exists, and flag that as a risk.

Generate a detailed timeline with hour-level steps. Include medical hard
constraints as hard_constraint=true. Include:
- arrival flight
- hotel check-in
- international desk pre-registration email check
- in-hospital registration, outpatient file setup, passport/insurance/payment verification
- nurse intake, consent forms, and pre-authorization, billing, invoice, or deposit check
- program-specific diagnostics and tests
- suggested doctor consultation, including doctor name if verified or
  doctor-assignment request if the name is not verified
- procedure, treatment, or checkup time blocks
- medication, discharge briefing, invoice, medical report, and claim-document collection
- follow-up/review time blocks with return-fitness confirmation
- local transport
- light tourism only when medically appropriate
- return flight
Each hospital timeline item must include details.registration_email,
details.registration_email_status, details.suggested_doctor_name,
details.suggested_doctor_specialty, details.appointment_phone,
details.wechat_or_portal_route, details.service_billing_status,
details.direct_billing_status, and details.hospital_steps when available.
Do not invent official emails or doctor names; mark them needs_confirmation if
not verified.

{COMMON_OUTPUT_RULES}

Required JSON keys:
option_id, city, recommendation_label, target_hospital, recommendation_reason,
required_days, flight, hotel, timeline, cost_breakdown, total_estimated_cost,
estimated_net_savings, insurance_policy, hospital_visit_protocol,
contact_lookup_guidance, contact_verification_status, readiness_items,
key_risks, metadata, audit_inputs, confirmation_requests.

audit_inputs must summarize the exact hospital source used, flight fare source,
hotel rate source, medical-cost source, insurance source, quote timestamp or
source_updated_at, and whether each value is representative, live, official, or
needs_confirmation. For hospital source, include source_records, date_checked,
email_status, appointment route, service_billing_status, direct_billing_status,
and next_verification_step.
""",
        tools=[
            estimate_flights,
            search_hotels,
            estimate_trip_costs,
            get_visa_entry_guidance,
            get_alipay_international_setup,
            lookup_china_hospital_contact_guidance,
            lookup_insurance_provider_policy,
            get_hospital_insurance_policy,
            get_hospital_visit_protocol,
        ],
        output_key=output_key,
    )


city_options_parallel_agent = ParallelAgent(
    name="city_options_parallel_agent",
    description="Generates diversified city options in parallel.",
    sub_agents=[
        _city_option_agent("best_overall_option_agent", "best overall balance", "option_best_overall"),
        _city_option_agent("lowest_cost_option_agent", "lowest total cost", "option_lowest_cost"),
        _city_option_agent("shortest_trip_option_agent", "shortest viable trip", "option_shortest_trip"),
        _city_option_agent("medical_strength_option_agent", "strongest medical resources", "option_medical_strength"),
    ],
)


option_audit_agent = LlmAgent(
    name="option_audit_agent",
    model=_model(settings.planner_model),
    description="Audits generated city options for source coverage and cost reasonableness.",
    instruction=f"""
You are the Audit Agent for the MedTour AI multi-agent planner.

Review these state keys:
- `profile_summary`
- `medical_shortlist`
- `option_best_overall`
- `option_lowest_cost`
- `option_shortest_trip`
- `option_medical_strength`

For each non-empty city option, call `audit_city_option_sources_and_costs` with
the full option payload. Use the tool result as the baseline audit, then add
your own concise cross-checks when needed.

Audit duties:
- Verify that the selected hospital and international patient pathway are tied
  to a named source and identify whether that source is official, RAG/curated,
  external API, or only an agent estimate.
- Challenge whether each material cost is reasonable: medical estimate, flight
  fare, hotel nightly rate and subtotal, local transport, meals, insurance, and
  total estimate.
- Check that flight and hotel prices include data status, timestamp/freshness,
  route or location, traveler count/nights, and booking caveats.
- Check hospital source quality: international department name, official
  appointment contact status, foreign-patient support, insurance handling, and
  medical program fit.
- Check whether the option used the lookup-china-hospital-contacts skill rules
  for hospital contact lookup, including email_status, contact_person_status,
  source_authority, source_urls/source_records, date_checked, appointment_phone,
  WeChat/portal route, service_billing_status, direct_billing_status, and
  next_verification_step. Treat sample, placeholder, missing, or official-general
  emails as blocking until the hospital's official appointment route is
  confirmed.
- Check service billing evidence: direct settlement, insurance partners,
  deposit/payment expectations, invoice route, and claim-document requirements.
  Missing billing evidence blocks non-refundable booking.
- Flag stale, missing, internally inconsistent, or suspiciously precise data.
- Require user/advisor confirmation before non-refundable booking whenever
  data is not live or official.

Do not silently fix another agent's numbers. Report the issue, suggested
correction path, and whether the report can be shown as planning-only.

{COMMON_OUTPUT_RULES}

Required JSON keys:
audit_status, option_audits, cross_option_findings, blocking_issues,
recommended_followups, confirmation_requests, assumptions.
""",
    tools=[audit_city_option_sources_and_costs],
    output_key="option_audit",
)


report_synthesis_agent = LlmAgent(
    name="report_synthesis_agent",
    model=_model(settings.planner_model),
    description="Merges city options into the final comparison report.",
    instruction=f"""
You are the Orchestrator and Report Synthesis Agent.

Merge these state keys:
- `profile_summary`
- `medical_shortlist`
- `option_best_overall`
- `option_lowest_cost`
- `option_shortest_trip`
- `option_medical_strength`
- `option_audit`

Build a final report for the frontend compare page. Requirements:
- Return up to four distinct city options.
- If duplicate cities appear, keep the stronger option and explain deduping in assumptions.
- Each option must carry timeline, flight number/time, hotel choice/address/prices,
  itemized cost breakdown, insurance_policy, visa/payment readiness, key risks,
  and confidence.
- Timeline items inside the hospital must show detailed registration,
  diagnostics, suggested doctor/doctor-assignment, procedure, discharge, and
  insurance document steps. Preserve details fields for registration email,
  email status, appointment phone, WeChat/portal route, service billing status,
  direct billing status, suggested doctor, specialty, source records, and
  hospital_steps.
- Hospital recommendations should prefer the hospital's 国际部 / international
  section or equivalent international patient pathway. Keep that section in
  target_hospital and comparison labels. Do not collapse it back to the parent
  hospital unless no international section exists.
- Insurance policy must be studied for the selected hospital, not only generic
  travel insurance. Include direct billing assumptions, pre-authorization needs,
  claim documents, exclusions, and suggestions for the user's current insurance holder.
- Preserve provider_policy details from the option agents, especially Cigna/AIA
  style provider lookup questions, issuing-country checks, direct-billing
  assumptions, and claim-document requirements.
- Merge audit results into each city option as audit_report. Preserve audit
  checks for hospital source verification, flight price, hotel price, medical
  price, total-cost math, service billing, insurance source, and source
  freshness.
- Add a top-level audit_summary that states whether the report is planning-only,
  which values need live re-checking, and which issues block non-refundable
  booking.
- Include comparison metrics for city, hospital, total days, medical cost, travel cost,
  insurance estimate, total cost, estimated savings, flight convenience, hotel convenience,
  readiness risk, and audit_status.
- Include confirmation_requests from all agents, plus your own if ranking is uncertain.
- Include medical disclaimers and booking warnings.
- Mark recommended option, but do not auto-select it.

{COMMON_OUTPUT_RULES}

Required JSON keys:
report_status, profile, city_options, comparison, recommended_option_id,
audit_summary, confirmation_requests, disclaimers, assumptions.
""",
    output_key="generated_report",
)


root_agent = SequentialAgent(
    name="medtour_ai_multi_agent_planner",
    description="Generates multi-city China medical travel plans from guided intake answers.",
    sub_agents=[
        profile_agent,
        medical_shortlist_agent,
        city_options_parallel_agent,
        option_audit_agent,
        report_synthesis_agent,
    ],
)


timeline_regeneration_agent = LlmAgent(
    name="timeline_regeneration_agent",
    model=_model(settings.planner_model),
    description="Regenerates a selected plan timeline after user preference edits.",
    instruction=f"""
You regenerate only the selected option timeline.

Input contains:
- selected city option
- accepted timeline version
- user preference edits such as stay length, hotel tier, flight preference,
  tourism intensity, or date changes

Keep medical hard constraints fixed unless the user explicitly changes medical
dates and the change is still feasible. Produce a new timeline_version with a
diff_summary explaining what changed. If the requested preference creates a
conflict, return confirmation_requests instead of silently making a risky plan.
If edits change stay length, dates, hospital, or city, refresh insurance_policy
with `lookup_insurance_provider_policy` and `get_hospital_insurance_policy`;
otherwise preserve the selected option's insurance_policy and mention it in
assumptions.
If the selected option names a hospital parent and an international section is
available, target the 国际部 / international section for appointments, insurance
review, registration, and timeline steps.
Before refreshing hospital_visit_protocol or changing registration/contact
details, call `lookup_china_hospital_contact_guidance` and preserve its
email/contact-person/service-billing acceptance rules in the regenerated
timeline.
Use `get_hospital_visit_protocol` to preserve or refresh detailed in-hospital
steps. Keep registration email and doctor name honest: include official/verified
values only when available; otherwise use a doctor-assignment request and
needs_confirmation status.
After regenerating material costs, dates, hotel, flight, hospital, or insurance
details, audit source freshness and cost reasonableness before returning. If the
selected option includes audit_report, preserve it and add a note that it must
be refreshed after edits.

{COMMON_OUTPUT_RULES}

Required JSON keys:
timeline_version_id, status, timeline, cost_delta, diff_summary,
insurance_policy, audit_notes, confirmation_requests, assumptions.
""",
    tools=[
        estimate_flights,
        search_hotels,
        estimate_trip_costs,
        get_visa_entry_guidance,
        lookup_china_hospital_contact_guidance,
        lookup_insurance_provider_policy,
        get_hospital_insurance_policy,
        get_hospital_visit_protocol,
    ],
    output_key="regenerated_timeline",
)
