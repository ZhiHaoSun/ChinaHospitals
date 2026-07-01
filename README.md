# MedTour AI

MedTour AI is a prototype web app for planning medical travel to China. It helps a user enter medical travel preferences, generate multi-city hospital plans, compare options, inspect a detailed hospital timeline, review insurance guidance, and track readiness tasks before travel.

## Tech Stack

### Frontend

- Static HTML/CSS/JavaScript app:
  - `index.html`
  - `styles.css`
  - `app.js`
- No frontend build step is required.
- The UI talks to the backend through `API_BASE_URL`, defaulting to `http://127.0.0.1:8000`.
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

### Multi-Agent Graph

The ADK planner is structured as:

1. User Profiler Agent
2. Medical City Shortlist Agent
3. Parallel City Option Agents:
   - Best overall
   - Lowest cost
   - Shortest trip
   - Strongest medical resources
4. Report Synthesis Agent

The agents prefer hospital international departments, international medical centers, international clinics, or equivalent foreign-patient pathways when recommending China hospitals.

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
  - Medical aesthetics
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

- User Profiler Agent
- Medical Consultant Agent
- City Option Agents
- Insurance Policy Agent
- Timeline Detail Agent
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

## Production Replacement Points

- Replace in-memory stores with persistent storage.
- Replace curated hospital/travel estimates with real APIs and RAG-backed hospital policy retrieval.
- Replace local email-code auth with a real email provider.
- Add durable background jobs for long-running agent generation.
- Add structured streaming/progress events from the backend instead of frontend-simulated agent progress.
