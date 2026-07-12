# MedTour AI

MedTour AI is a working prototype web app for planning medical travel to China. It helps a user enter medical travel preferences, generate multi-city hospital plans, compare options, inspect a detailed hospital timeline, review insurance and billing guidance, draft registration emails, and track readiness tasks before travel.

The project currently has:

- A deployed Vercel web prototype: `https://traechinahospital1355.vercel.app/`
- A local static UI for development: `http://127.0.0.1:5173`
- A local FastAPI backend: `http://127.0.0.1:8000`
- A working multi-agent planning flow using Google ADK, LiteLLM, and OpenAI models.
- A deterministic local planner for demos, fallback behavior, and fast UI testing.
- Pydantic schema enforcement and normalization for generated report outputs.
- Embedded hospital-contact lookup guidance for China hospital international departments.
- City-specific travel and cost estimates for Shanghai, Guangzhou, Beijing, and Shenzhen.

## Current Progress

The prototype supports the main product journey end to end:

1. Intake form captures medical purpose, procedure details, nationality, departure city, date range, duration, budget tier, insurance holder, and planner backend.
2. The API normalizes the intake into a profile draft.
3. Users can generate medical travel options through either:
   - `local`: deterministic planner for stable demos and fallback behavior.
   - `adk`: multi-agent planner for AI-generated city options and audit output.
4. The comparison view renders city-by-city options with hospitals, estimated total costs, savings, hotels, flights, risk counts, and confidence signals.
5. The plan view renders a detailed daily timeline, cost card, insurance policy section, hospital contact details, registration email links, flight/hotel search links, and readiness tasks.
6. The readiness view tracks operational tasks such as visa checks, Alipay setup, appointment confirmation, insurance review, and claim-document preparation.
7. The app can export a selected plan to PDF.

The deployed Vercel interface has been hardened for serverless behavior. Since Vercel Python functions do not guarantee durable in-memory state across requests, the frontend can now render a selected plan from the generated browser-side report snapshot when a later report lookup is unavailable. This keeps **View Timeline** and plan inspection usable on the deployed site.

The multi-agent system is currently working. It includes staged progress for profile normalization, medical rules, parallel city planning, hospital contact lookup, travel and budget estimation, insurance review, timeline construction, source/cost audit, and report synthesis.

## Tech Stack

### Frontend

- Static HTML/CSS/JavaScript app:
  - `index.html`
  - `styles.css`
  - `app.js`
- No frontend build step is required.
- The UI talks to the backend through `API_BASE_URL`, defaulting to `http://127.0.0.1:8000`.
- On Vercel, API routes are served through the Python function entrypoint in `api/index.py`.
- Main frontend views:
  - Intake
  - Multi-agent progress
  - Multi-city comparison
  - Plan detail timeline
  - Readiness checklist

### Backend

- Python FastAPI service in `medtour_ai/api/main.py`.
- Pydantic models in `medtour_ai/agents/schemas.py`.
- In-memory development stores:
  - `InMemoryReportStore`
  - `InMemoryAuthStore`
- CORS is configured for local development origins such as:
  - `http://localhost:5173`
  - `http://127.0.0.1:5173`
  - `http://localhost:8000`
  - `http://127.0.0.1:8000`

### Planning Engines

The app supports two planner backends:

- `local`: deterministic local planner in `medtour_ai/services/planner.py`.
- `adk`: Google ADK multi-agent graph in `medtour_ai/agents/agent.py`, run through `medtour_ai/services/adk_runner.py`.

The ADK path uses:

- Google ADK workflow agents
- LiteLLM
- OpenAI models via `OPENAI_API_KEY`
- `orjson`, required by the LiteLLM/OpenAI runtime stack in this project environment.

If the ADK/OpenAI path fails in a deployed environment, the API can fall back to the local deterministic planner and attach fallback metadata/disclaimers to the report.

### Multi-Agent Graph

The ADK planner is structured around:

1. Profile Normalizer Agent
2. Medical Rules Agent
3. Parallel City Option Agents:
   - Best overall
   - Lowest cost
   - Shortest trip
   - Strongest medical resources
4. Hospital Contact Lookup Agent
5. Travel & Budget Agent
6. Insurance Policy Agent
7. Timeline Detail Agent
8. Source & Cost Audit Agent
9. Report Synthesis Agent

The agents prefer hospital international departments, international medical centers, international clinics, or equivalent foreign-patient pathways when recommending China hospitals.

## Hospital Contact Lookup

Hospital contact lookup is supported by the embedded skill file:

```text
skills/lookup-china-hospital-contacts/SKILL.md
```

The skill guides agents to look for and classify:

- International department or international medical center name
- Registration email
- Appointment phone
- Main hospital phone
- WeChat, mini-program, app, or official portal route
- Billing desk and service-billing notes
- Direct billing or reimbursement assumptions
- Claim document requirements
- Official source records and confidence labels

Seed source guidance is stored in:

```text
skills/lookup-china-hospital-contacts/references/source-registry.md
```

The planner uses confidence labels and `needs_confirmation` flags when contact, billing, or insurance data is incomplete.

## Cost Model Progress

The local planner now uses city-specific assumptions instead of one generic travel estimate. Cost data varies by:

- Medical purpose and city
- Flight estimate
- Hotel nightly rate by city and budget tier
- Airport transfer
- Daily local transport
- Daily meals
- Visa and payment setup
- Travel insurance estimate

Current supported city profiles include:

- Shanghai
- Guangzhou
- Beijing
- Shenzhen

The generated total estimate now includes flight, medical cost, hotel, local transport, meals, visa/payment setup, and travel insurance. The report artifacts in `reports/local_api_report.json` and `reports/local_api_report.md` are regenerated from the local API smoke flow.

## Setup

Create and install the Python environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Create local environment config:

```bash
cp .env.example .env
```

For the ADK agent backend, set:

```bash
OPENAI_API_KEY=...
```

Run the backend:

```bash
.venv/bin/uvicorn medtour_ai.api.main:app --host 127.0.0.1 --port 8000
```

Serve the static frontend from the repository root:

```bash
.venv/bin/python -m http.server 5173
```

Then open:

```text
http://127.0.0.1:5173
```

## User Flow

### 1. Intake

The user starts in the intake view and selects:

- Medical need:
  - Eye surgery
  - Dental care
  - Health checkup
  - CAR-T / blood cancer consultation
- Dynamic procedure details based on medical need
- Nationality / residence
- Departure city
- Current insurance holder
- Travel date range
- Duration
- Winter/off-season flexibility
- Planner backend:
  - `Agents`
  - `Local`

When the user taps **Generate Options**, the frontend posts intake answers to:

```text
POST /api/v1/intake/normalize
```

### 2. Agent Progress

If the user selects **Agents**, the app opens the multi-agent progress view.

The view shows staged progress for:

- Profile Normalizer Agent
- Medical Rules Agent
- Parallel City Option Agents
- Hospital Contact Lookup Agent
- Travel & Budget Agent
- Insurance Policy Agent
- Timeline Detail Agent
- Source & Cost Audit Agent
- Report Synthesis Agent

The report is generated through:

```text
POST /api/v1/reports
```

with:

```json
{
  "planner_backend": "adk"
}
```

If the user selects **Local**, the app skips the progress view and generates through the deterministic local planner.

### 3. Multi-City Comparison

The compare view shows generated city cards and a comparison table.

Each city card includes:

- City
- Recommended hospital or international section
- Estimated cost
- Required days
- Estimated savings
- Risk count
- Confidence

The user can select a city card. The selected card becomes highlighted, and its button changes to **View Timeline**.

### 4. Plan Detail

The plan detail view shows the selected city plan.

It includes:

- City switcher for moving between generated plans
- Detailed timeline
- Hospital procedure steps
- Registration email / international desk details when available
- Suggested doctor or doctor-assignment guidance
- Cost card
- Currency switch between SGD and RMB
- Insurance policy card
- Registration email `mailto:` link with a generated email template
- Flight number links to Google search
- Hotel and key-term links to Google search
- Source records and contact lookup evidence

Hospital timeline items include details such as:

- International desk pre-registration
- Outpatient registration
- Nurse intake
- Consent forms
- Diagnostics
- Doctor consultation
- Procedure window
- Medication and discharge briefing
- Claim document collection
- Follow-up review

### 5. Readiness Checklist

The readiness view tracks pre-trip tasks such as:

- Visa or visa-free entry confirmation
- Alipay setup
- Hospital appointment confirmation
- Insurance policy review
- Claim document preparation

Checklist status updates are sent through:

```text
PATCH /api/v1/reports/{report_id}/options/{option_id}/readiness/items/{item_id}
```

On the deployed Vercel prototype, readiness can also update locally from the browser-side plan snapshot if the in-memory report is not available on a later serverless request.

## Authentication Flow

The prototype includes local-development authentication:

- Email-code login
- Recovery code login
- Passkey registration stub
- Trusted-device session cookie

Auth endpoints are in `medtour_ai/api/main.py`, backed by `InMemoryAuthStore`.

## Important API Endpoints

```text
GET  /api/v1/health
GET  /api/v1/planner/config
GET  /api/v1/intake/schema
POST /api/v1/intake/normalize
POST /api/v1/reports
GET  /api/v1/reports/{report_id}
GET  /api/v1/reports/{report_id}/options
POST /api/v1/reports/{report_id}/options/{option_id}/select
GET  /api/v1/reports/{report_id}/options/{option_id}/timeline
POST /api/v1/reports/{report_id}/options/{option_id}/timeline/regenerate
GET  /api/v1/reports/{report_id}/options/{option_id}/costs
GET  /api/v1/reports/{report_id}/options/{option_id}/readiness
```

## Development Notes

- The frontend contains fallback sample data for first-load UI preview only.
- After generation is attempted, fallback test data is suppressed so agent/local planner errors are visible.
- ADK output is normalized by the API to tolerate common model-output shapes, including Markdown-wrapped JSON and incomplete money values like `TBD`.
- The local planner is useful for UI development because it does not require model credentials.
- The API validates generated report shape with Pydantic before returning usable city options.
- The frontend uses a browser-side plan snapshot to keep deployed plan views usable in stateless serverless environments.
- The ADK path requires `OPENAI_API_KEY`; `/api/v1/planner/config` reports whether the agent backend is available.
- `reports/local_api_report.json` and `reports/local_api_report.md` are generated smoke-test artifacts from `scripts/render_test_report.py`.

## Production Replacement Points

- Replace in-memory stores with persistent storage.
- Replace curated hospital/travel estimates with real APIs and RAG-backed hospital policy retrieval.
- Replace local email-code auth with a real email provider.
- Add durable background jobs for long-running agent generation.
- Add structured streaming/progress events from the backend instead of frontend-simulated agent progress.
- Add production observability for agent events, model failures, source audit quality, and cost-estimate freshness.
