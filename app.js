const routes = ["intake", "agent-progress", "compare", "plan", "readiness"];
const API_BASE_URL = window.MEDTOUR_API_BASE_URL || "http://127.0.0.1:8000";
const RMB_PER_SGD = 5.35;

const state = {
  reportId: null,
  operationId: null,
  profileDraftId: null,
  report: null,
  options: [],
  selectedOptionId: null,
  timeline: null,
  costs: null,
  readiness: null,
  costCurrency: "SGD",
  plannerBackend: "adk",
  generationAttempted: false,
  agentProgress: {
    running: false,
    activeStepId: "profile",
    completedStepIds: [],
    failedStepId: null,
    statusMessage: "Waiting to start.",
  },
  auth: {
    authenticated: false,
    user: null,
    session: null,
    challengeId: null,
    email: "",
    devCode: "",
    recoveryCodes: [],
    mode: "email",
    message: "",
    messageType: "info",
  },
  loading: false,
};

let agentProgressTimers = [];

const agentProgressSteps = [
  {
    id: "profile",
    title: "User Profiler Agent",
    icon: "person_search",
    working: "Normalizing medical need, program details, passport country, travel dates, and insurance holder.",
    done: "Profile normalized and missing confirmations identified.",
  },
  {
    id: "medical",
    title: "Medical Consultant Agent",
    icon: "local_hospital",
    working: "Shortlisting China cities, prioritizing hospital international sections and medical fit.",
    done: "City and hospital candidates prepared.",
  },
  {
    id: "parallel",
    title: "City Option Agents",
    icon: "hub",
    working: "Running city planners in parallel for best overall, lowest cost, shortest trip, and strongest resources.",
    done: "Diversified city options generated.",
  },
  {
    id: "insurance",
    title: "Insurance Policy Agent",
    icon: "health_and_safety",
    working: "Checking hospital billing assumptions, pre-authorization, claim documents, and user insurer fit.",
    done: "Insurance policy notes attached to each city plan.",
  },
  {
    id: "timeline",
    title: "Timeline Detail Agent",
    icon: "timeline",
    working: "Building hospital registration, diagnostics, suggested doctor, procedure, discharge, and follow-up steps.",
    done: "Detailed timelines assembled.",
  },
  {
    id: "synthesis",
    title: "Report Synthesis Agent",
    icon: "analytics",
    working: "Ranking options, deduplicating cities, calculating comparison metrics, and preparing the final report.",
    done: "Final report ready for comparison.",
  },
];

const fallbackOptions = [
  {
    option_id: "sample_shanghai",
    city: "Shanghai",
    recommendation_label: "Sample International Plan",
    target_hospital: "Shanghai International Medical Center - International Patient Service",
    medical_purpose: "eye_surgery",
    procedure_subtype: "smile_pro",
    program_details: {
      currentPrescription: "-4.50 both eyes, mild astigmatism",
      contactLensUsage: "soft_lenses",
    },
    recommendation_reason: "Sample data showing detailed international hospital workflow, doctor assignment, and insurance document steps.",
    required_days: 4,
    flight: {
      airline: "Singapore Airlines",
      flight_number: "SQ830",
      departure_airport: "SIN",
      arrival_airport: "PVG",
      departure_time: "2026-08-12T08:00:00+08:00",
      arrival_time: "2026-08-12T13:30:00+08:00",
      estimated_cost: { amount: 520, currency: "SGD" },
    },
    hotel: {
      name: "Shanghai Medical District Hotel",
      address: "Pudong medical district, Shanghai",
      nightly_rate: { amount: 165, currency: "SGD" },
      nights: 3,
      distance_to_hospital: "10-20 min by car",
      foreign_guest_eligible: true,
    },
    cost_breakdown: {
      medical: { amount: 5500, low: 4200, high: 6800, currency: "SGD" },
      flight: { amount: 520, currency: "SGD" },
      hotel: { amount: 495, currency: "SGD" },
      local_transport: { amount: 192, currency: "SGD" },
      meals: { amount: 135, currency: "SGD" },
      visa_and_payment_setup: { amount: 80, currency: "SGD" },
      travel_insurance: { amount: 95, currency: "SGD" },
    },
    total_estimated_cost: { amount: 7017, currency: "SGD" },
    estimated_net_savings: { amount: 2590, currency: "SGD" },
    hospital_visit_protocol: {
      registration_contact: {
        desk: "International patient registration desk",
        email: "intl.service@shanghai-imc-demo.example",
        email_status: "sample_not_verified",
      },
      suggested_doctor: {
        name: "Dr. Chen Minghao (sample)",
        specialty: "Ophthalmology / refractive surgery",
        request_note: "Request a senior refractive-surgery consultant and confirm the named doctor in the appointment reply.",
      },
    },
    insurance_policy: {
      current_holder: "AIA",
      hospital_name: "Shanghai International Medical Center - International Patient Service",
      medical_purpose: "eye_surgery",
      policy_status: "needs_insurer_confirmation",
      summary: "Sample policy review. Confirm pre-authorization, direct billing, and reimbursement documents before booking.",
      hospital_policy: {
        direct_billing: "Limited international direct billing may be available only after insurer pre-authorization.",
        preauthorization_required: true,
        claim_documents: ["itemized invoice", "diagnosis certificate", "doctor report", "payment receipt"],
        common_exclusions: ["elective care without approval", "pre-existing condition exclusions"],
      },
      estimated_premium: { amount: 95, currency: "SGD" },
      suggestions: [
        "Contact AIA with the hospital name and procedure estimate to confirm coverage.",
        "Request written pre-authorization before paying a hospital deposit.",
        "Keep itemized invoices, diagnosis certificate, doctor report, prescriptions, and receipts.",
      ],
    },
    timeline: [
      {
        day: 1,
        date: "2026-08-12",
        title: "Arrival and Pre-registration",
        items: [
          {
            category: "flight",
            title: "Arrival flight",
            start_time: "2026-08-12T08:00:00+08:00",
            end_time: "2026-08-12T13:30:00+08:00",
            location_name: "PVG",
            estimated_cost: { amount: 520, currency: "SGD" },
            confidence_level: "medium",
            details: {},
          },
          {
            category: "hotel",
            title: "Hotel check-in",
            start_time: "2026-08-12T15:30:00+08:00",
            end_time: "2026-08-12T16:00:00+08:00",
            location_name: "Shanghai Medical District Hotel",
            address: "Pudong medical district, Shanghai",
            confidence_level: "medium",
            details: {},
          },
          {
            category: "medical",
            title: "International desk pre-registration email check",
            start_time: "2026-08-12T16:30:00+08:00",
            end_time: "2026-08-12T17:15:00+08:00",
            location_name: "Shanghai International Medical Center - International Patient Service",
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_desk: "International patient registration desk",
              registration_email: "intl.service@shanghai-imc-demo.example",
              registration_email_status: "sample_not_verified",
              suggested_doctor_name: "Dr. Chen Minghao (sample)",
              suggested_doctor_specialty: "Ophthalmology / refractive surgery",
              suggested_doctor_request: "Request a senior refractive-surgery consultant and confirm the named doctor in the appointment reply.",
              hospital_steps: [
                "Email the international desk with passport name, preferred date, SMILE Pro interest, current prescription, and insurance holder.",
                "Attach prior eye reports only after confirming the official email channel.",
                "Ask for appointment confirmation, deposit requirement, interpreter support, and doctor assignment.",
              ],
            },
          },
        ],
      },
      {
        day: 2,
        date: "2026-08-13",
        title: "Registration and Diagnostics",
        items: [
          {
            category: "medical",
            title: "International desk registration and outpatient file setup",
            start_time: "2026-08-13T08:30:00+08:00",
            end_time: "2026-08-13T09:00:00+08:00",
            location_name: "Shanghai International Medical Center - International Patient Service",
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_desk: "International patient registration desk",
              registration_email: "intl.service@shanghai-imc-demo.example",
              registration_email_status: "sample_not_verified",
              suggested_doctor_name: "Dr. Chen Minghao (sample)",
              suggested_doctor_specialty: "Ophthalmology / refractive surgery",
              suggested_doctor_request: "Request a senior refractive-surgery consultant and confirm the named doctor in the appointment reply.",
              hospital_steps: [
                "Show passport, appointment confirmation, insurance card or pre-authorization letter, and payment method.",
                "Create outpatient profile, confirm invoice name for claims, and sign privacy/consent forms.",
              ],
            },
          },
          {
            category: "medical",
            title: "Diagnostics and refractive-surgery suitability tests",
            start_time: "2026-08-13T09:30:00+08:00",
            end_time: "2026-08-13T11:30:00+08:00",
            location_name: "Shanghai International Medical Center - International Patient Service",
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: "intl.service@shanghai-imc-demo.example",
              registration_email_status: "sample_not_verified",
              suggested_doctor_name: "Dr. Chen Minghao (sample)",
              suggested_doctor_specialty: "Ophthalmology / refractive surgery",
              hospital_steps: [
                "Complete vision testing, corneal scan, eye-pressure check, tear-film assessment, and dilation if required.",
                "Confirm soft contact lens pause period and whether test results allow same-trip procedure.",
              ],
            },
          },
          {
            category: "medical",
            title: "Suggested doctor consultation and eligibility confirmation",
            start_time: "2026-08-13T14:00:00+08:00",
            end_time: "2026-08-13T15:30:00+08:00",
            location_name: "Shanghai International Medical Center - International Patient Service",
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: "intl.service@shanghai-imc-demo.example",
              registration_email_status: "sample_not_verified",
              suggested_doctor_name: "Dr. Chen Minghao (sample)",
              suggested_doctor_specialty: "Ophthalmology / refractive surgery",
              suggested_doctor_request: "Ask the international clinic to confirm the named surgeon before final payment.",
              hospital_steps: [
                "Review test results, eligibility, treatment alternatives, procedure risks, and final price.",
                "Confirm whether insurance requires guarantee-of-payment or reimbursement-only handling.",
              ],
            },
          },
        ],
      },
      {
        day: 3,
        date: "2026-08-14",
        title: "Procedure and Recovery",
        items: [
          {
            category: "medical",
            title: "Final consent, deposit, and treatment-room preparation",
            start_time: "2026-08-14T08:45:00+08:00",
            end_time: "2026-08-14T09:30:00+08:00",
            location_name: "Shanghai International Medical Center - International Patient Service",
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: "intl.service@shanghai-imc-demo.example",
              registration_email_status: "sample_not_verified",
              suggested_doctor_name: "Dr. Chen Minghao (sample)",
              suggested_doctor_specialty: "Ophthalmology / refractive surgery",
              hospital_steps: [
                "Reconfirm doctor, eye marking, consent forms, final price, and payment or pre-authorization status.",
                "Ask for post-procedure medicine list and emergency contact route before entering treatment.",
              ],
            },
          },
          {
            category: "medical",
            title: "SMILE Pro procedure window",
            start_time: "2026-08-14T09:30:00+08:00",
            end_time: "2026-08-14T12:00:00+08:00",
            location_name: "Shanghai International Medical Center - International Patient Service",
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: "intl.service@shanghai-imc-demo.example",
              registration_email_status: "sample_not_verified",
              suggested_doctor_name: "Dr. Chen Minghao (sample)",
              suggested_doctor_specialty: "Ophthalmology / refractive surgery",
              hospital_steps: [
                "Complete procedure only after same-day surgeon confirmation and eligibility check.",
                "Rest in clinic observation area until cleared by the medical team.",
              ],
            },
          },
          {
            category: "medical",
            title: "Medication, discharge briefing, and claim documents",
            start_time: "2026-08-14T12:00:00+08:00",
            end_time: "2026-08-14T12:45:00+08:00",
            location_name: "Shanghai International Medical Center - International Patient Service",
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: "intl.service@shanghai-imc-demo.example",
              registration_email_status: "sample_not_verified",
              suggested_doctor_name: "Dr. Chen Minghao (sample)",
              suggested_doctor_specialty: "Ophthalmology / refractive surgery",
              hospital_steps: [
                "Collect eyedrops, written aftercare instructions, diagnosis certificate, itemized invoice, doctor report, and receipts.",
                "Confirm next-day follow-up time and emergency contact instructions.",
              ],
            },
          },
        ],
      },
      {
        day: 4,
        date: "2026-08-15",
        title: "Follow-up and Return Readiness",
        items: [
          {
            category: "medical",
            title: "Follow-up review with assigned doctor or international clinic",
            start_time: "2026-08-15T09:30:00+08:00",
            end_time: "2026-08-15T10:30:00+08:00",
            location_name: "Shanghai International Medical Center - International Patient Service",
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: "intl.service@shanghai-imc-demo.example",
              registration_email_status: "sample_not_verified",
              suggested_doctor_name: "Dr. Chen Minghao (sample)",
              suggested_doctor_specialty: "Ophthalmology / refractive surgery",
              hospital_steps: [
                "Check healing, vision status, medication use, screen-time limits, and flight fitness.",
                "Confirm remote follow-up route after returning home.",
              ],
            },
          },
          {
            category: "readiness",
            title: "Confirm return fitness, invoices, and insurance documents",
            start_time: "2026-08-15T11:00:00+08:00",
            end_time: "2026-08-15T11:30:00+08:00",
            location_name: "Shanghai International Medical Center - International Patient Service",
            confidence_level: "medium",
            details: {
              registration_email: "intl.service@shanghai-imc-demo.example",
              registration_email_status: "sample_not_verified",
              hospital_steps: [
                "Verify all claim documents are stamped or digitally valid.",
                "Confirm whether translated reports are required by the insurer.",
              ],
            },
          },
        ],
      },
    ],
    key_risks: [
      "Official registration email and final doctor name must be confirmed by the hospital.",
      "Procedure eligibility depends on in-person diagnostics.",
      "Insurance pre-authorization may be required before deposit payment.",
    ],
    metadata: { confidence_level: "medium", data_status: "sample" },
  },
];

const programDetailConfigs = {
  eye_surgery: {
    icon: "visibility",
    title: "Eye surgery details",
    subtitle: "Clarify the likely procedure and eye-readiness details.",
    subtypeLabel: "Procedure type",
    subtypeOptions: [
      ["smile_pro", "SMILE / SMILE Pro"],
      ["lasik", "LASIK"],
      ["icl", "ICL lens implant"],
      ["cataract", "Cataract surgery"],
      ["not_sure", "Not sure yet"],
    ],
    fields: [
      {
        id: "currentPrescription",
        label: "Current prescription",
        icon: "visibility",
        placeholder: "e.g. -4.50 both eyes, astigmatism",
      },
      {
        id: "contactLensUsage",
        label: "Contact lens usage",
        icon: "lens",
        type: "select",
        options: [
          ["none", "No contact lenses"],
          ["soft_lenses", "Soft lenses"],
          ["hard_or_ortho_k", "Hard lenses / Ortho-K"],
          ["not_sure", "Not sure"],
        ],
      },
    ],
  },
  dental_care: {
    icon: "dentistry",
    title: "Dental program details",
    subtitle: "Clarify scope, imaging, and whether the work may need multiple visits.",
    subtypeLabel: "Dental procedure",
    subtypeOptions: [
      ["single_implant", "Single implant"],
      ["multiple_implants", "Multiple implants"],
      ["crown_bridge", "Crown / bridge"],
      ["root_canal", "Root canal"],
      ["not_sure", "Not sure yet"],
    ],
    fields: [
      {
        id: "teethCount",
        label: "Number of teeth involved",
        icon: "tag",
        placeholder: "e.g. 1 implant, 3 crowns",
      },
      {
        id: "recentXray",
        label: "Recent X-ray or CBCT",
        icon: "image_search",
        type: "select",
        options: [
          ["yes", "Yes, available"],
          ["no", "No"],
          ["not_sure", "Not sure"],
        ],
      },
    ],
  },
  health_checkup: {
    icon: "monitor_heart",
    title: "Health checkup details",
    subtitle: "Clarify screening focus so the plan can reserve the right tests.",
    subtypeLabel: "Screening package",
    subtypeOptions: [
      ["executive_screening", "Executive screening"],
      ["cardio_screening", "Cardio focus"],
      ["cancer_markers", "Cancer-marker focus"],
      ["women_health", "Women's health"],
      ["not_sure", "Not sure yet"],
    ],
    fields: [
      {
        id: "screeningFocus",
        label: "Main health concern",
        icon: "clinical_notes",
        placeholder: "e.g. heart, cancer markers, full body",
      },
      {
        id: "knownConditions",
        label: "Known conditions",
        icon: "medical_information",
        placeholder: "e.g. hypertension, diabetes, none",
      },
    ],
  },
  medical_aesthetics: {
    icon: "face_retouching_natural",
    title: "Aesthetic program details",
    subtitle: "Clarify treatment area and downtime tolerance.",
    subtypeLabel: "Treatment type",
    subtypeOptions: [
      ["skin_laser", "Skin laser"],
      ["injectables", "Injectables"],
      ["body_contouring", "Body contouring"],
      ["minor_surgery", "Minor surgical procedure"],
      ["not_sure", "Not sure yet"],
    ],
    fields: [
      {
        id: "treatmentArea",
        label: "Treatment area",
        icon: "gesture",
        placeholder: "e.g. face, jawline, abdomen",
      },
      {
        id: "downtimeTolerance",
        label: "Downtime tolerance",
        icon: "hotel",
        type: "select",
        options: [
          ["minimal", "Minimal downtime"],
          ["three_to_five_days", "3-5 days"],
          ["one_week_plus", "1 week or more"],
          ["not_sure", "Not sure"],
        ],
      },
    ],
  },
};

function showRoute(route) {
  const activeRoute = routes.includes(route) ? route : "intake";
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
  document.querySelector(`#view-${activeRoute}`).classList.add("active");
  document.querySelectorAll("[data-route]").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === activeRoute);
  });
  if (location.hash.replace("#", "") !== activeRoute) {
    history.replaceState(null, "", `#${activeRoute}`);
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function setStatus(message, type = "info") {
  const banner = document.querySelector("#appStatus");
  if (!banner) return;
  banner.hidden = !message;
  banner.textContent = message || "";
  banner.dataset.type = type;
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function selectedPlannerBackend() {
  const selected = document.querySelector("[data-planner-backend].selected")?.dataset.plannerBackend;
  return selected || state.plannerBackend || "adk";
}

function setPlannerBackend(backend) {
  state.plannerBackend = backend === "local" ? "local" : "adk";
  document.querySelectorAll("[data-planner-backend]").forEach((button) => {
    const selected = button.dataset.plannerBackend === state.plannerBackend;
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
}

function clearAgentProgressTimers() {
  agentProgressTimers.forEach((timer) => clearTimeout(timer));
  agentProgressTimers = [];
}

function resetAgentProgress(message = agentProgressSteps[0].working) {
  clearAgentProgressTimers();
  state.agentProgress = {
    running: true,
    activeStepId: agentProgressSteps[0].id,
    completedStepIds: [],
    failedStepId: null,
    statusMessage: message,
  };
  renderAgentProgress();
}

function activateAgentStep(stepId, message) {
  const stepIndex = agentProgressSteps.findIndex((step) => step.id === stepId);
  if (stepIndex < 0) return;
  const completedStepIds = agentProgressSteps.slice(0, stepIndex).map((step) => step.id);
  state.agentProgress = {
    ...state.agentProgress,
    running: true,
    activeStepId: stepId,
    completedStepIds,
    failedStepId: null,
    statusMessage: message || agentProgressSteps[stepIndex].working,
  };
  renderAgentProgress();
}

function startAgentProgressSimulation(startIndex = 1) {
  clearAgentProgressTimers();
  agentProgressSteps.slice(startIndex).forEach((step, index) => {
    const timer = setTimeout(() => activateAgentStep(step.id), 900 + index * 1250);
    agentProgressTimers.push(timer);
  });
}

function finishAgentProgress(message = "Final report is ready. Opening the city comparison.") {
  clearAgentProgressTimers();
  state.agentProgress = {
    running: false,
    activeStepId: agentProgressSteps.at(-1).id,
    completedStepIds: agentProgressSteps.map((step) => step.id),
    failedStepId: null,
    statusMessage: message,
  };
  renderAgentProgress();
}

function failAgentProgress(message) {
  clearAgentProgressTimers();
  state.agentProgress = {
    ...state.agentProgress,
    running: false,
    failedStepId: state.agentProgress.activeStepId,
    statusMessage: message,
  };
  renderAgentProgress();
}

function renderAgentProgress() {
  const container = document.querySelector("#agentProgressSteps");
  if (!container) return;
  const completed = new Set(state.agentProgress.completedStepIds || []);
  const failedStepId = state.agentProgress.failedStepId;
  const activeStepId = state.agentProgress.activeStepId;
  const completedCount = completed.size;
  const percent = Math.round((completedCount / agentProgressSteps.length) * 100);

  const bar = document.querySelector("#agentProgressBar");
  const percentLabel = document.querySelector("#agentProgressPercent");
  const message = document.querySelector("#agentProgressMessage");
  const subtitle = document.querySelector("#agentProgressSubtitle");
  if (bar) bar.style.width = `${percent}%`;
  if (percentLabel) percentLabel.textContent = `${percent}%`;
  if (message) message.textContent = state.agentProgress.statusMessage || "Waiting to start.";
  if (subtitle) {
    subtitle.textContent = state.agentProgress.running
      ? "Agents are coordinating your profile, hospitals, insurance, travel, and timeline details."
      : failedStepId
        ? "The agent run needs attention before the report can be shown."
        : "The agent run is complete.";
  }

  container.innerHTML = agentProgressSteps
    .map((step) => {
      const isComplete = completed.has(step.id);
      const isActive = step.id === activeStepId && !failedStepId && !isComplete;
      const isError = step.id === failedStepId;
      const status = isError ? "Error" : isComplete ? "Complete" : isActive ? "Working" : "Queued";
      const body = isComplete ? step.done : step.working;
      return `
        <article class="agent-stage-card ${isComplete ? "complete" : ""} ${isActive ? "active" : ""} ${isError ? "error" : ""}">
          <span class="material-symbols-outlined">${step.icon}</span>
          <div>
            <h2>${step.title}</h2>
            <p>${body}</p>
          </div>
          <span class="agent-stage-status">${status}</span>
        </article>
      `;
    })
    .join("");
}

function setAuthMessage(message, type = "info") {
  state.auth.message = message;
  state.auth.messageType = type;
  renderAuth();
}

function openAuthModal(mode = "email") {
  state.auth.mode = mode;
  const modal = document.querySelector("#authModal");
  if (modal) modal.hidden = false;
  renderAuth();
}

function closeAuthModal() {
  const modal = document.querySelector("#authModal");
  if (modal) modal.hidden = true;
}

function sessionDate(value) {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function renderAuth() {
  const loginButton = document.querySelector("#loginButton");
  if (loginButton) {
    loginButton.textContent = state.auth.authenticated ? state.auth.user?.email || "Account" : "Log in";
  }

  const panel = document.querySelector("#authPanel");
  if (!panel) return;

  const message = state.auth.message
    ? `<div class="auth-message" data-type="${state.auth.messageType}">${escapeHtml(state.auth.message)}</div>`
    : "";

  if (state.auth.authenticated) {
    const recoveryCodes = state.auth.recoveryCodes.length
      ? `
        <div class="recovery-codes">
          <strong>Save these recovery codes before travel</strong>
          <div>${state.auth.recoveryCodes.map((code) => `<code>${escapeHtml(code)}</code>`).join("")}</div>
        </div>
      `
      : "";
    panel.innerHTML = `
      ${message}
      <div class="auth-account">
        <span class="material-symbols-outlined">verified_user</span>
        <div>
          <strong>${escapeHtml(state.auth.user?.email || "Signed in")}</strong>
          <p>Trusted device session valid until ${escapeHtml(sessionDate(state.auth.session?.expires_at))}.</p>
        </div>
      </div>
      <div class="auth-session-grid">
        <div><span>Method</span><strong>${escapeHtml(state.auth.session?.auth_method || "session")}</strong></div>
        <div><span>Recovery codes</span><strong>${state.auth.user?.recovery_codes_remaining ?? 0}</strong></div>
      </div>
      ${recoveryCodes}
      <div class="auth-actions-row">
        <button class="outline-button icon-left" type="button" data-auth-action="register-passkey">
          <span class="material-symbols-outlined">passkey</span>
          Add Passkey
        </button>
        <button class="outline-button" type="button" data-auth-action="logout">Log out</button>
      </div>
    `;
    return;
  }

  if (state.auth.mode === "recovery") {
    panel.innerHTML = `
      ${message}
      <label class="auth-field">
        <span>Email</span>
        <input id="authRecoveryEmail" type="email" autocomplete="email" value="${escapeHtml(state.auth.email)}" placeholder="you@example.com" />
      </label>
      <label class="auth-field">
        <span>Recovery code</span>
        <input id="authRecoveryCode" autocomplete="one-time-code" placeholder="MT-XXXXXX-XXXXXX" />
      </label>
      <label class="auth-check">
        <input id="authRecoveryTrusted" type="checkbox" checked />
        <span>Trust this device for my China trip</span>
      </label>
      <div class="auth-actions-row">
        <button class="primary-button" type="button" data-auth-action="verify-recovery">Sign in</button>
        <button class="outline-button" type="button" data-auth-action="show-email">Use email code</button>
      </div>
    `;
    return;
  }

  panel.innerHTML = `
    ${message}
    <label class="auth-field">
      <span>Email</span>
      <input id="authEmail" type="email" autocomplete="email" value="${escapeHtml(state.auth.email)}" placeholder="you@example.com" />
    </label>
    <label class="auth-check">
      <input id="authTrusted" type="checkbox" checked />
      <span>Trust this device for my China trip</span>
    </label>
    ${
      state.auth.challengeId
        ? `
          <label class="auth-field">
            <span>6-digit code</span>
            <input id="authCode" inputmode="numeric" autocomplete="one-time-code" placeholder="000000" />
          </label>
          <p class="auth-dev-code">Local dev code: <strong>${escapeHtml(state.auth.devCode)}</strong></p>
          <div class="auth-actions-row">
            <button class="primary-button" type="button" data-auth-action="verify-email">Verify code</button>
            <button class="outline-button" type="button" data-auth-action="start-email">Resend</button>
          </div>
        `
        : `
          <button class="primary-button auth-wide" type="button" data-auth-action="start-email">Send email code</button>
        `
    }
    <div class="auth-alt-actions">
      <button class="ghost" type="button" data-auth-action="show-recovery">Use recovery code</button>
    </div>
    <p class="auth-note">No Google, Facebook, WhatsApp, or reCAPTCHA dependency is required for sign in.</p>
  `;
}

async function refreshAuthSession() {
  try {
    const session = await api("/api/v1/auth/session");
    state.auth.authenticated = Boolean(session.authenticated);
    state.auth.user = session.user || null;
    state.auth.session = session.session || null;
    state.auth.message = "";
  } catch (error) {
    console.error(error);
    state.auth.authenticated = false;
    state.auth.user = null;
    state.auth.session = null;
  }
  renderAuth();
}

async function startEmailLogin() {
  const email = document.querySelector("#authEmail")?.value?.trim() || state.auth.email;
  const trusted = Boolean(document.querySelector("#authTrusted")?.checked ?? true);
  if (!email) {
    setAuthMessage("Enter an email address first.", "error");
    return;
  }
  try {
    const result = await api("/api/v1/auth/login/start", {
      method: "POST",
      body: JSON.stringify({ email, trusted_device: trusted }),
    });
    state.auth.email = result.email;
    state.auth.challengeId = result.challenge_id;
    state.auth.devCode = result.dev_code || "";
    setAuthMessage("Enter the code sent to your email. Local dev shows it below.", "success");
  } catch (error) {
    console.error(error);
    setAuthMessage(`Could not start login: ${error.message}`, "error");
  }
}

async function verifyEmailLogin() {
  const code = document.querySelector("#authCode")?.value?.trim() || "";
  const trusted = Boolean(document.querySelector("#authTrusted")?.checked ?? true);
  if (!state.auth.challengeId || !code) {
    setAuthMessage("Enter the login code first.", "error");
    return;
  }
  try {
    const result = await api("/api/v1/auth/login/verify", {
      method: "POST",
      body: JSON.stringify({ challenge_id: state.auth.challengeId, code, trusted_device: trusted }),
    });
    applyAuthResult(result, "Signed in. This device is trusted for your trip.");
  } catch (error) {
    console.error(error);
    setAuthMessage(`Could not verify code: ${error.message}`, "error");
  }
}

async function verifyRecoveryLogin() {
  const email = document.querySelector("#authRecoveryEmail")?.value?.trim() || state.auth.email;
  const recoveryCode = document.querySelector("#authRecoveryCode")?.value?.trim() || "";
  const trusted = Boolean(document.querySelector("#authRecoveryTrusted")?.checked ?? true);
  if (!email || !recoveryCode) {
    setAuthMessage("Enter your email and recovery code.", "error");
    return;
  }
  try {
    const result = await api("/api/v1/auth/recovery/verify", {
      method: "POST",
      body: JSON.stringify({ email, recovery_code: recoveryCode, trusted_device: trusted }),
    });
    applyAuthResult(result, "Signed in with recovery code.");
  } catch (error) {
    console.error(error);
    setAuthMessage(`Could not use recovery code: ${error.message}`, "error");
  }
}

function applyAuthResult(result, message) {
  state.auth.authenticated = true;
  state.auth.user = result.user;
  state.auth.session = result.session;
  state.auth.recoveryCodes = result.recovery_codes || [];
  state.auth.challengeId = null;
  state.auth.devCode = "";
  state.auth.message = message;
  state.auth.messageType = "success";
  renderAuth();
}

async function logout() {
  try {
    await api("/api/v1/auth/logout", { method: "POST" });
  } catch (error) {
    console.error(error);
  }
  state.auth.authenticated = false;
  state.auth.user = null;
  state.auth.session = null;
  state.auth.recoveryCodes = [];
  state.auth.message = "Signed out.";
  state.auth.messageType = "info";
  renderAuth();
}

async function registerPasskey() {
  try {
    const started = await api("/api/v1/auth/passkeys/register/start", { method: "POST" });
    const result = await api("/api/v1/auth/passkeys/register/complete", {
      method: "POST",
      body: JSON.stringify({ challenge_id: started.challenge_id, label: "Current device" }),
    });
    state.auth.user = { ...state.auth.user, passkey_enabled: true };
    state.auth.message = `Passkey registered: ${result.credential.label}.`;
    state.auth.messageType = "success";
    renderAuth();
  } catch (error) {
    console.error(error);
    setAuthMessage(`Could not add passkey: ${error.message}`, "error");
  }
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    credentials: "include",
    ...options,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${detail}`);
  }
  return response.json();
}

function money(value, targetCurrency = null) {
  if (!value) return "N/A";
  const sourceCurrency = normalizeCurrency(value.currency || "SGD");
  const currency = normalizeCurrency(targetCurrency || sourceCurrency);
  const amount = convertAmount(Number(value.amount || 0), sourceCurrency, currency);
  return `${currency} ${amount.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

function normalizeCurrency(currency) {
  return currency === "CNY" ? "RMB" : currency;
}

function convertAmount(amount, fromCurrency, toCurrency) {
  if (fromCurrency === toCurrency) return amount;
  if (fromCurrency === "SGD" && toCurrency === "RMB") return amount * RMB_PER_SGD;
  if (fromCurrency === "RMB" && toCurrency === "SGD") return amount / RMB_PER_SGD;
  return amount;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function textDate(value) {
  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric", year: "numeric" });
}

function timeRange(item) {
  const start = item.start_time?.slice(11, 16) || "";
  const end = item.end_time?.slice(11, 16) || "";
  return start && end ? `${start} - ${end}` : start || end;
}

function iconForCategory(category) {
  return {
    flight: "flight_land",
    hotel: "hotel",
    medical: "local_hospital",
    transport: "directions_car",
    meal: "restaurant",
    tourism: "attractions",
    readiness: "assignment_turned_in",
  }[category] || "event";
}

function hasTimelineHospitalDetails(item) {
  const details = item.details || {};
  return Boolean(
    details.registration_email ||
      details.suggested_doctor_name ||
      details.suggested_doctor_specialty ||
      details.hospital_steps?.length
  );
}

function hospitalDetailTemplate(item, option) {
  const protocol = option?.hospital_visit_protocol || fallbackOptions[0]?.hospital_visit_protocol || {};
  const contact = protocol.registration_contact || {};
  const doctor = protocol.suggested_doctor || {};
  const title = (item.title || "").toLowerCase();
  let hospitalSteps = [
    "Confirm the international desk appointment, registration channel, and required documents.",
    "Ask the hospital to confirm the assigned doctor and whether interpreter support is available.",
  ];

  if (title.includes("email") || title.includes("pre-registration")) {
    hospitalSteps = [
      "Email the international desk with passport name, preferred date, medical purpose, procedure subtype, and insurance holder.",
      "Attach prior reports only after confirming the official hospital email channel.",
      "Ask for appointment confirmation, deposit requirement, interpreter availability, and doctor assignment.",
    ];
  } else if (title.includes("registration") || title.includes("outpatient") || title.includes("file")) {
    hospitalSteps = [
      "Show passport, appointment confirmation, insurance card or guarantee-of-payment letter, and payment method.",
      "Create the outpatient profile, confirm invoice name for insurance claims, and sign consent/privacy forms.",
    ];
  } else if (title.includes("diagnostic") || title.includes("exam") || title.includes("test")) {
    hospitalSteps = [
      "Complete program-specific diagnostics such as imaging, lab tests, scans, or specialist measurements.",
      "Confirm whether results allow the planned procedure/checkup to continue on the same trip.",
    ];
  } else if (title.includes("doctor") || title.includes("consultation") || title.includes("eligibility")) {
    hospitalSteps = [
      "Review results with the assigned doctor or international clinic specialist.",
      "Confirm eligibility, alternatives, risks, final price, treatment timing, and insurance handling.",
    ];
  } else if (title.includes("procedure") || title.includes("treatment") || title.includes("surgery")) {
    hospitalSteps = [
      "Reconfirm doctor, consent forms, final price, payment or pre-authorization status, and treatment-room readiness.",
      "Proceed only after same-day eligibility and safety confirmation by the medical team.",
    ];
  } else if (title.includes("discharge") || title.includes("claim") || title.includes("invoice") || title.includes("document")) {
    hospitalSteps = [
      "Collect doctor report, diagnosis certificate, itemized invoice, prescriptions, payment receipts, and visit summary.",
      "Confirm emergency contact route and whether remote follow-up is available after returning home.",
    ];
  } else if (title.includes("follow-up") || title.includes("review")) {
    hospitalSteps = [
      "Review healing, medication use, warning signs, activity limits, and return-travel fitness.",
      "Confirm remote follow-up route and what to do if symptoms appear after departure.",
    ];
  }

  return {
    registration_desk: contact.desk || "International patient registration desk",
    registration_email: contact.email || "intl.service@shanghai-imc-demo.example",
    registration_email_status: contact.email_status || "sample_not_verified",
    suggested_doctor_name: doctor.name || "Dr. Chen Minghao (sample)",
    suggested_doctor_specialty: doctor.specialty || "Relevant specialist for selected medical program",
    suggested_doctor_request:
      doctor.request_note || "Request the international clinic to confirm the named doctor before final payment.",
    hospital_steps: hospitalSteps,
  };
}

function timelineDaysForDisplay(days, option) {
  return (days || []).map((day) => ({
    ...day,
    items: (day.items || []).map((item) => {
      if (!["medical", "readiness"].includes(item.category) || hasTimelineHospitalDetails(item)) return item;
      return {
        ...item,
        details: {
          ...(item.details || {}),
          ...hospitalDetailTemplate(item, option),
        },
      };
    }),
  }));
}

function renderTimelineDetails(item) {
  const details = item.details || {};
  if (!hasTimelineHospitalDetails(item)) return "";

  const doctorLine = [details.suggested_doctor_name, details.suggested_doctor_specialty].filter(Boolean).join(" · ");
  const status = details.registration_email_status ? ` (${details.registration_email_status.replaceAll("_", " ")})` : "";
  return `
    <div class="timeline-details">
      ${
        details.registration_email
          ? `<div><span class="material-symbols-outlined">alternate_email</span><b>Registration email</b><p>${escapeHtml(details.registration_email)}${escapeHtml(status)}</p></div>`
          : ""
      }
      ${
        doctorLine
          ? `<div><span class="material-symbols-outlined">stethoscope</span><b>Suggested doctor</b><p>${escapeHtml(doctorLine)}</p></div>`
          : ""
      }
      ${
        details.suggested_doctor_request
          ? `<div><span class="material-symbols-outlined">assignment_ind</span><b>Doctor request</b><p>${escapeHtml(details.suggested_doctor_request)}</p></div>`
          : ""
      }
      ${
        details.hospital_steps?.length
          ? `<ul>${details.hospital_steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ul>`
          : ""
      }
    </div>
  `;
}

function riskCount(option) {
  const count = option.key_risks?.length || 0;
  return `${count} ${count === 1 ? "Risk" : "Risks"}`;
}

function confidence(option) {
  return option.metadata?.confidence_level || option.medical_confidence || "medium";
}

function progressForOption(option, index) {
  const savings = Number(option.estimated_net_savings?.amount || 0);
  return Math.max(54, Math.min(92, 62 + index * 6 + Math.round(savings / 1000)));
}

function selectedOption() {
  const options = state.options.length ? state.options : state.generationAttempted ? [] : fallbackOptions;
  return options.find((option) => option.option_id === state.selectedOptionId) || options[0] || null;
}

function renderCities() {
  const cityCards = document.querySelector("#cityCards");
  const options = state.options.length ? state.options : state.generationAttempted ? [] : fallbackOptions;
  if (!options.length) {
    cityCards.innerHTML = `
      <article class="city-card selected">
        <span class="city-label">
          <span class="material-symbols-outlined">error</span>
          No Agent Options
        </span>
        <h2>No city plans returned</h2>
        <div class="hospital-line">
          <strong>The agent run did not produce usable city options.</strong>
          <span>Return to intake and try Agents again, or switch to Local to verify the planner contract.</span>
        </div>
      </article>
    `;
    renderAnalysisTable();
    return;
  }
  cityCards.innerHTML = options
    .map((option, index) => {
      const selected = option.option_id === state.selectedOptionId || (!state.selectedOptionId && index === 0);
      return `
        <article class="city-card ${selected ? "selected" : ""}" tabindex="0" role="button" aria-pressed="${selected}" data-compare-option-id="${option.option_id}">
          <span class="city-label">
            <span class="material-symbols-outlined">${index === 0 ? "star" : "verified"}</span>
            ${option.recommendation_label || "City Option"}
          </span>
          <h2>${option.city}</h2>
          <div class="hospital-line">
            <strong><span class="material-symbols-outlined" style="font-size:16px">local_hospital</span> ${option.target_hospital}</strong>
            <span>${option.recommendation_reason || "International patient planning estimate"}</span>
          </div>
          <div class="mini-divider"></div>
          <div class="metric-row">
            <div><span>Est. Total Cost</span><strong>${money(option.total_estimated_cost)}</strong></div>
            <div><span>Total Duration</span><strong>${option.required_days || "-"} Days</strong></div>
          </div>
          <span class="muted">Est. Savings vs Home</span>
          <strong class="savings-value">${money(option.estimated_net_savings)}</strong>
          <div class="savings-bar"><span style="width:${progressForOption(option, index)}%"></span></div>
          <div class="risk-tags">
            <span>Confidence: ${confidence(option)}</span>
            <span>${riskCount(option)}</span>
          </div>
          <button
            class="${selected ? "primary-button selected" : "outline-button"} select-plan"
            type="button"
            ${selected ? `data-open-plan-option-id="${option.option_id}"` : `data-compare-option-id="${option.option_id}"`}
          >
            ${selected ? "View Timeline" : "Select Plan"}
          </button>
        </article>
      `;
    })
    .join("");
  renderAnalysisTable();
}

function renderAnalysisTable() {
  const table = document.querySelector("#analysisTable");
  const options = state.options.length ? state.options : state.generationAttempted ? [] : fallbackOptions;
  if (!options.length) {
    table.innerHTML = `
      <div class="row header"><div>Metric</div><div>No generated options</div></div>
      <div class="row"><div>Status</div><div>The agent response had no city_options.</div></div>
    `;
    return;
  }
  const headers = options.map((option, index) => `<div>${option.city}${index === 0 ? " ★" : ""}</div>`).join("");
  const row = (label, values) => `
    <div class="row">
      <div>${label}</div>
      ${values.map((value) => `<div>${value}</div>`).join("")}
    </div>
  `;
  table.innerHTML = `
    <div class="row header"><div>Metric</div>${headers}</div>
    <div class="section-row">Medical & Travel</div>
    ${row("Hospital", options.map((option) => option.target_hospital))}
    ${row("Duration", options.map((option) => `${option.required_days || "-"} days`))}
    ${row("Flight", options.map((option) => option.flight ? `${option.flight.flight_number} to ${option.flight.arrival_airport}` : "-"))}
    ${row("Hotel", options.map((option) => option.hotel ? `${option.hotel.name}, ${option.hotel.distance_to_hospital}` : "-"))}
    <div class="section-row">Costs</div>
    ${row("Medical estimate", options.map((option) => money(option.cost_breakdown?.medical)))}
    ${row("Insurance estimate", options.map((option) => money(option.cost_breakdown?.travel_insurance || option.insurance_policy?.estimated_premium)))}
    ${row("Total estimate", options.map((option) => money(option.total_estimated_cost)))}
    ${row("Estimated savings", options.map((option) => money(option.estimated_net_savings)))}
    <div class="section-row">Insurance Readiness</div>
    ${row("Policy review", options.map((option) => option.insurance_policy?.policy_status || "needs confirmation"))}
    ${row("Hospital billing", options.map((option) => option.insurance_policy?.hospital_policy?.direct_billing || "Confirm with hospital"))}
    <div class="section-row">AI Risk Analysis</div>
    ${row("Identified factors", options.map((option) => (option.key_risks || []).join(" ")))}
  `;
}

function renderPlan() {
  const option = selectedOption();
  const rawTimelineDays = state.reportId ? state.timeline?.days || option?.timeline || [] : option?.timeline || [];
  const displaySourceDays = rawTimelineDays.length ? rawTimelineDays : state.generationAttempted ? [] : fallbackOptions[0]?.timeline || [];
  const timelineDays = timelineDaysForDisplay(displaySourceDays, option || fallbackOptions[0]);
  document.querySelector("#sidePlanCity").textContent = option ? `${option.city} Plan` : "Selected Plan";
  document.querySelector("#sidePlanSubtitle").textContent = option
    ? `${option.target_hospital}`
    : "Generate options to choose a city.";
  document.querySelector("#planSubtitle").textContent = option
    ? `Detailed schedule for your care journey in ${option.city}.`
    : "Generate options to render a detailed schedule.";
  renderPlanCitySwitcher(option);
  renderTimeline(timelineDays);
  renderCostCard(state.costs, option);
  renderInsuranceCard(option);
}

function renderPlanCitySwitcher(activeOption) {
  const switcher = document.querySelector("#planCitySwitcher");
  if (!switcher) return;
  const options = state.options.length ? state.options : state.generationAttempted ? [] : fallbackOptions;

  if (!options.length) {
    switcher.innerHTML = `
      <div class="plan-city-empty">
        <span class="material-symbols-outlined">travel_explore</span>
        <span>Generate options to compare city plans.</span>
      </div>
    `;
    return;
  }

  switcher.innerHTML = `
    <span class="switcher-label">City Plans</span>
    <div class="plan-city-options">
      ${options
        .map((option) => {
          const selected = option.option_id === activeOption?.option_id;
          return `
            <button
              class="plan-city-option ${selected ? "selected" : ""}"
              type="button"
              ${selected ? 'aria-current="true"' : `data-option-id="${option.option_id}"`}
            >
              <span>
                <strong>${option.city}</strong>
                <small>${option.required_days || "-"} days &middot; ${money(option.total_estimated_cost)}</small>
              </span>
              <span class="material-symbols-outlined">${selected ? "check_circle" : "chevron_right"}</span>
            </button>
          `;
        })
        .join("")}
    </div>
  `;
}

function renderTimeline(days) {
  const timeline = document.querySelector("#timelineDays");
  if (!days.length) {
    timeline.innerHTML = `<article class="day-card"><h2>No timeline yet</h2><p>Generate options and select a city plan.</p></article>`;
    return;
  }
  timeline.innerHTML = days
    .map(
      (day) => `
        <article class="day-card">
          <h2>Day ${day.day}: ${day.title}</h2>
          <p>${textDate(day.date)}</p>
          <div class="timeline-list">
            ${(day.items || [])
              .map(
                (item) => `
                  <div class="timeline-node ${item.category}">
                    <span class="node-icon material-symbols-outlined">${iconForCategory(item.category)}</span>
                    <div class="node-card ${item.hard_constraint ? "scheduled" : ""}">
                      <div class="node-top">
                        <strong>${item.title}</strong>
                        <time>${timeRange(item)}</time>
                      </div>
                      <p>${item.location_name || ""}</p>
                      ${item.address ? `<p>${item.address}</p>` : ""}
                      ${renderTimelineDetails(item)}
                      <div class="node-tags">
                        ${item.estimated_cost ? `<span>Est. ${money(item.estimated_cost)}</span>` : ""}
                        <span>${item.confidence_level || "medium"} confidence</span>
                        ${item.hard_constraint ? "<span>Medical constraint</span>" : ""}
                      </div>
                    </div>
                  </div>
                `
              )
              .join("")}
          </div>
        </article>
      `
    )
    .join("");
}

function renderCostCard(costs, option) {
  const card = document.querySelector("#costCard");
  const categories = costs?.categories || option?.cost_breakdown || {};
  const total = costs?.total || option?.total_estimated_cost;
  const selectedCurrency = state.costCurrency || "SGD";
  card.innerHTML = `
    <div class="cost-card-top">
      <h2>Est. Costs</h2>
      <div class="currency-tabs" aria-label="Cost currency">
        ${["SGD", "RMB"]
          .map(
            (currency) => `
              <button
                class="${currency === selectedCurrency ? "active" : ""}"
                type="button"
                data-cost-currency="${currency}"
                aria-pressed="${currency === selectedCurrency}"
              >${currency}</button>
            `
          )
          .join("")}
      </div>
    </div>
    <strong class="total-cost">${money(total, selectedCurrency)}</strong>
    <span>Total Estimated Cost</span>
    <dl class="cost-lines">
      ${Object.entries(categories)
        .map(([label, value]) => `<div><dt>${label.replaceAll("_", " ")}</dt><dd>${money(value, selectedCurrency)}</dd></div>`)
        .join("")}
    </dl>
    <p class="info-callout">
      Costs are API estimates for planning. ${selectedCurrency === "RMB" ? `RMB uses an estimate of ${RMB_PER_SGD} RMB per SGD. ` : ""}Confirm hospital, flight, hotel, visa, and payment details before booking.
    </p>
  `;
}

function renderInsuranceCard(option) {
  const card = document.querySelector("#insuranceCard");
  if (!card) return;
  const policy = option?.insurance_policy;
  if (!policy) {
    card.innerHTML = `
      <h2>Insurance Policy</h2>
      <p>Generate and select a city plan to review insurance suggestions.</p>
    `;
    return;
  }

  card.innerHTML = `
    <div class="insurance-card-top">
      <h2>Insurance Policy</h2>
      <span>${escapeHtml(policy.policy_status || "needs review")}</span>
    </div>
    <p>${escapeHtml(policy.summary)}</p>
    <dl class="insurance-lines">
      <div><dt>Current holder</dt><dd>${escapeHtml(policy.current_holder || "Not provided")}</dd></div>
      <div><dt>Hospital billing</dt><dd>${escapeHtml(policy.hospital_policy?.direct_billing || "Confirm with hospital")}</dd></div>
      <div><dt>Estimated premium</dt><dd>${money(policy.estimated_premium)}</dd></div>
    </dl>
    <div class="insurance-section">
      <strong>Suggestions</strong>
      <ul>${(policy.suggestions || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
    <p class="info-callout">Insurance terms vary by policy. Confirm coverage, exclusions, pre-authorization, and claim documents with your insurer and the hospital before booking.</p>
  `;
}

function renderReadiness() {
  const option = selectedOption();
  const readiness = state.readiness;
  document.querySelector("#readinessSubtitle").textContent = option
    ? `Complete these items before traveling to ${option.city}.`
    : "Generate and select a city plan to load readiness tasks.";

  const percent = readiness?.completion_percent || 0;
  const total = readiness?.total_count || 0;
  const completed = readiness?.completed_count || 0;
  const highRisk = readiness?.high_risk_items || [];
  document.querySelector("#readinessSummary").innerHTML = `
    <div class="progress-card">
      <div class="donut" style="background: conic-gradient(var(--primary) 0 ${percent}%, var(--surface-highest) ${percent}% 100%)" aria-label="${percent} percent ready">
        <span>${percent}%</span><small>Ready</small>
      </div>
      <p>${completed} of ${total} items completed</p>
    </div>
    <div class="action-required">
      <div class="alert-head">
        <span class="material-symbols-outlined">warning</span>
        <div>
          <h2>${highRisk.length ? "Action Required" : "No High-Risk Blocks"}</h2>
          <p>${highRisk.length ? "High-priority items are pending that could delay your travel." : "Keep reviewing tasks as details change."}</p>
        </div>
      </div>
      <div class="urgent-row">
        <span class="material-symbols-outlined">assignment_late</span>
        <strong>${highRisk[0]?.title || "No urgent item"}</strong>
        <time>${highRisk[0]?.priority || "ready"}</time>
      </div>
    </div>
  `;

  const sections = readiness?.sections || [];
  document.querySelector("#checklistGrid").innerHTML = sections.length
    ? sections
        .map(
          (section) => `
            <section>
              <h2>${section.title}</h2>
              ${(section.items || [])
                .map((item) => {
                  const done = item.status === "complete";
                  const statusClass = done ? "completed" : item.priority === "high" ? "danger" : "warning";
                  return `
                    <div class="check-item ${statusClass}">
                      <input type="checkbox" ${done ? "checked" : ""} data-readiness-id="${item.id}" aria-label="${item.title}" />
                      <div>
                        <div class="item-title-row"><strong>${item.title}</strong><span>${item.status || "pending"}</span></div>
                        <p>${(item.steps || []).slice(0, 2).join(" ")}</p>
                        <div class="item-footer">
                          <b>Priority: ${item.priority}</b>
                          ${item.helpful_links?.[0] ? `<a href="${item.helpful_links[0].url}" target="_blank" rel="noreferrer">${item.helpful_links[0].title} ↗</a>` : ""}
                        </div>
                      </div>
                    </div>
                  `;
                })
                .join("")}
            </section>
          `
        )
        .join("")
    : `<section><h2>No readiness tasks yet</h2><p>Generate and select a plan first.</p></section>`;
}

function selectedMedicalNeed() {
  return document.querySelector('[data-choice-group="need"].selected')?.dataset.value || "eye_surgery";
}

function renderProgramDetails() {
  const container = document.querySelector("#programDetails");
  if (!container) return;
  const config = programDetailConfigs[selectedMedicalNeed()] || programDetailConfigs.eye_surgery;
  const subtypeOptions = config.subtypeOptions
    .map(([value, label], index) => `<option value="${value}" ${index === 0 ? "selected" : ""}>${label}</option>`)
    .join("");
  const fields = config.fields
    .map((field) => {
      const control =
        field.type === "select"
          ? `
            <select id="programDetail_${field.id}" data-program-detail="${field.id}" aria-label="${field.label}">
              ${(field.options || []).map(([value, label]) => `<option value="${value}">${label}</option>`).join("")}
            </select>
          `
          : `<input id="programDetail_${field.id}" data-program-detail="${field.id}" placeholder="${field.placeholder || ""}" aria-label="${field.label}" />`;
      return `
        <label>
          <span>${field.label}</span>
          <span class="input-shell">
            <span class="material-symbols-outlined">${field.icon || "edit_note"}</span>
            ${control}
          </span>
        </label>
      `;
    })
    .join("");

  container.innerHTML = `
    <div class="program-details-header">
      <span class="material-symbols-outlined">${config.icon}</span>
      <div>
        <strong>${config.title}</strong>
        <p>${config.subtitle}</p>
      </div>
    </div>
    <div class="field-grid">
      <label>
        <span>${config.subtypeLabel}</span>
        <span class="input-shell">
          <span class="material-symbols-outlined">fact_check</span>
          <select id="procedureSubtypeInput" aria-label="${config.subtypeLabel}">
            ${subtypeOptions}
          </select>
        </span>
      </label>
      ${fields}
    </div>
  `;
}

function collectProgramDetails() {
  const details = {};
  document.querySelectorAll("[data-program-detail]").forEach((field) => {
    const value = field.value?.trim?.() ?? field.value;
    if (value) details[field.dataset.programDetail] = value;
  });
  return details;
}

function collectAnswers() {
  const selectedDuration = document.querySelector(".chip.selected");
  const offSeason = document.querySelector("#offSeasonSwitch")?.classList.contains("on");
  const winter = document.querySelector("#winterSwitch")?.classList.contains("on");
  const medicalPurpose = selectedMedicalNeed();
  return {
    medical_purpose: medicalPurpose,
    procedure_subtype: document.querySelector("#procedureSubtypeInput")?.value || "not_sure",
    program_details: collectProgramDetails(),
    nationality: countryCode(document.querySelector("#nationalityInput")?.value || "Singapore"),
    residence_country: countryCode(document.querySelector("#nationalityInput")?.value || "Singapore"),
    departure_city: document.querySelector("#departureCityInput")?.value || "Singapore",
    current_insurance_holder: document.querySelector("#insuranceHolderInput")?.value?.trim() || null,
    date_mode: "range",
    date_range: parseDateRange(document.querySelector("#dateRangeInput")?.value || ""),
    duration_preference: selectedDuration?.dataset.duration || "5_7_days",
    season_flexibility: offSeason ? "offseason_ok" : winter ? "winter_ok" : "depends_on_price",
    budget_tier: "balanced",
    traveler_count: 1,
    hotel_preference: "near_hospital_foreign_guest_eligible",
    tourism_intensity: "light",
  };
}

function countryCode(value) {
  const normalized = value.trim().toLowerCase();
  if (normalized.includes("singapore")) return "SG";
  if (normalized.includes("malaysia")) return "MY";
  if (normalized.includes("united states") || normalized === "usa" || normalized === "us") return "US";
  return value.trim().slice(0, 2).toUpperCase() || "SG";
}

function parseDateRange(value) {
  const match = value.match(/(\w+)\s+(\d{1,2}).*(\w+)\s+(\d{1,2}),\s*(\d{4})/);
  if (!match) return { start: "2026-08-12", end: "2026-08-18" };
  const [, startMonth, startDay, endMonth, endDay, year] = match;
  return {
    start: toIsoDate(startMonth, startDay, year),
    end: toIsoDate(endMonth, endDay, year),
  };
}

function toIsoDate(monthName, day, year) {
  const monthIndex = new Date(`${monthName} 1, ${year}`).getMonth() + 1;
  return `${year}-${String(monthIndex).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

async function generateOptions() {
  const button = document.querySelector("#generateOptionsButton");
  const label = button.querySelector(".button-label");
  const plannerBackend = selectedPlannerBackend();
  try {
    state.loading = true;
    state.generationAttempted = true;
    state.reportId = null;
    state.operationId = null;
    state.report = null;
    state.options = [];
    state.selectedOptionId = null;
    state.timeline = null;
    state.costs = null;
    state.readiness = null;
    button.disabled = true;
    label.textContent = "Generating...";
    setStatus(
      plannerBackend === "adk" ? "Agents are generating multi-city options..." : "Generating multi-city options from backend API...",
      "info"
    );
    if (plannerBackend === "adk") {
      resetAgentProgress();
      showRoute("agent-progress");
    } else {
      showRoute("compare");
    }

    const answers = collectAnswers();
    const draft = await api("/api/v1/intake/normalize", {
      method: "POST",
      body: JSON.stringify({ answers }),
    });
    state.profileDraftId = draft.profile_draft_id;
    if (plannerBackend === "adk") {
      activateAgentStep("medical");
      startAgentProgressSimulation(2);
    }

    const reportRequest = api("/api/v1/reports", {
      method: "POST",
      body: JSON.stringify({
        profile_draft_id: state.profileDraftId,
        generation_mode: "multi_city",
        max_city_options: 4,
        currency: "SGD",
        language: "en",
        run_now: true,
        planner_backend: plannerBackend,
      }),
    });
    const generated = plannerBackend === "adk" ? (await Promise.all([reportRequest, delay(1800)]))[0] : await reportRequest;

    if (generated.status === "failed" || generated.report?.status === "failed" || generated.report?.error) {
      const detail = generated.report?.error?.message || generated.report?.error?.detail || "The planner failed to generate a report.";
      throw new Error(detail);
    }
    const generatedOptions = generated.report.city_options || [];
    if (!generatedOptions.length) {
      throw new Error("The planner returned no city options. Check the agent output contract or backend logs.");
    }
    state.reportId = generated.report_id;
    state.operationId = generated.operation_id;
    state.report = generated.report;
    state.options = generatedOptions;
    state.selectedOptionId = generated.report.recommended_option_id || state.options[0]?.option_id || null;
    persistState();
    renderCities();
    if (plannerBackend === "adk") {
      finishAgentProgress();
      await delay(650);
    }
    showRoute("compare");
    setStatus(`Generated ${state.options.length} city options. Choose a plan to view details.`, "success");
  } catch (error) {
    console.error(error);
    if (plannerBackend === "adk") {
      failAgentProgress(`Agent run stopped: ${error.message}`);
    }
    persistState();
    setStatus(`API error: ${error.message}`, "error");
  } finally {
    state.loading = false;
    button.disabled = false;
    label.textContent = "Generate Options";
  }
}

async function selectOption(optionId) {
  if (!state.reportId || !optionId) {
    setStatus("Generate options before selecting a plan.", "error");
    return;
  }
  if (optionId === state.selectedOptionId && state.timeline && state.costs && state.readiness) {
    showRoute("plan");
    return;
  }
  try {
    await api(`/api/v1/reports/${state.reportId}/options/${optionId}/select`, { method: "POST" });
    state.selectedOptionId = optionId;
    state.timeline = null;
    state.costs = null;
    state.readiness = null;
    renderPlan();
    renderReadiness();
    await loadSelectedPlan();
    persistState();
    renderCities();
    renderPlan();
    renderReadiness();
    showRoute("plan");
  } catch (error) {
    console.error(error);
    setStatus(`Could not select plan: ${error.message}`, "error");
  }
}

async function selectComparisonOption(optionId) {
  if (!state.reportId || !optionId) {
    setStatus("Generate options before selecting a plan.", "error");
    return;
  }
  try {
    if (optionId !== state.selectedOptionId) {
      await api(`/api/v1/reports/${state.reportId}/options/${optionId}/select`, { method: "POST" });
      state.selectedOptionId = optionId;
      state.timeline = null;
      state.costs = null;
      state.readiness = null;
      persistState();
    }
    renderCities();
    const option = selectedOption();
    setStatus(`${option?.city || "City"} selected. Tap View Timeline to open the detailed plan.`, "success");
  } catch (error) {
    console.error(error);
    setStatus(`Could not select city: ${error.message}`, "error");
  }
}

async function loadSelectedPlan() {
  if (!state.reportId || !state.selectedOptionId) return;
  const [timeline, costs, readiness] = await Promise.all([
    api(`/api/v1/reports/${state.reportId}/options/${state.selectedOptionId}/timeline`),
    api(`/api/v1/reports/${state.reportId}/options/${state.selectedOptionId}/costs`),
    api(`/api/v1/reports/${state.reportId}/options/${state.selectedOptionId}/readiness`),
  ]);
  state.timeline = timeline;
  state.costs = costs;
  state.readiness = readiness;
}

async function regenerateTimeline() {
  if (!state.reportId || !state.selectedOptionId) {
    setStatus("Select a plan before regenerating the timeline.", "error");
    return;
  }
  const button = document.querySelector("#regenerateTimelineButton");
  try {
    button.disabled = true;
    button.textContent = "Regenerating...";
    const regenerated = await api(`/api/v1/reports/${state.reportId}/options/${state.selectedOptionId}/timeline/regenerate`, {
      method: "POST",
      body: JSON.stringify({
        base_timeline_version_id: state.timeline?.timeline_version_id || "tlv_1",
        preferences: {
          stay_length_preference: "8_plus_days",
          flight_preference: "avoid_red_eye",
          hotel_budget_tier: "balanced",
          tourism_intensity: "light",
        },
        run_now: true,
        planner_backend: state.plannerBackend || "local",
      }),
    });
    const timelineVersionId = regenerated.timeline.timeline_version_id;
    await api(`/api/v1/reports/${state.reportId}/options/${state.selectedOptionId}/timeline/${timelineVersionId}/accept`, {
      method: "POST",
    });
    state.timeline = { timeline_version_id: timelineVersionId, days: regenerated.timeline.timeline };
    renderPlan();
    setStatus(`Timeline regenerated and accepted: ${timelineVersionId}`, "success");
  } catch (error) {
    console.error(error);
    setStatus(`Could not regenerate timeline: ${error.message}`, "error");
  } finally {
    button.disabled = false;
    button.textContent = "Regenerate Timeline";
  }
}

async function updateReadiness(itemId, checked) {
  if (!state.reportId || !state.selectedOptionId) return;
  try {
    await api(`/api/v1/reports/${state.reportId}/options/${state.selectedOptionId}/readiness/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify({
        status: checked ? "complete" : "pending",
        note: checked ? "Updated from frontend UI" : null,
      }),
    });
    state.readiness = await api(`/api/v1/reports/${state.reportId}/options/${state.selectedOptionId}/readiness`);
    renderReadiness();
  } catch (error) {
    console.error(error);
    setStatus(`Could not update readiness: ${error.message}`, "error");
  }
}

function persistState() {
  localStorage.setItem(
    "medtour_api_state",
    JSON.stringify({
      reportId: state.reportId,
      operationId: state.operationId,
      profileDraftId: state.profileDraftId,
      report: state.report,
      options: state.options,
      selectedOptionId: state.selectedOptionId,
      timeline: state.timeline,
      costs: state.costs,
      readiness: state.readiness,
      costCurrency: state.costCurrency,
      plannerBackend: state.plannerBackend,
      generationAttempted: state.generationAttempted,
    })
  );
}

function restoreState() {
  try {
    const saved = JSON.parse(localStorage.getItem("medtour_api_state") || "null");
    if (!saved) return;
    Object.assign(state, saved);
  } catch {
    localStorage.removeItem("medtour_api_state");
  }
}

function bindInteractions() {
  document.addEventListener("click", (event) => {
    const loginButton = event.target.closest("#loginButton");
    if (loginButton) {
      openAuthModal();
      return;
    }

    const authAction = event.target.closest("[data-auth-action]");
    if (authAction) {
      event.preventDefault();
      const action = authAction.dataset.authAction;
      if (action === "close") closeAuthModal();
      if (action === "show-email") {
        state.auth.mode = "email";
        state.auth.message = "";
        renderAuth();
      }
      if (action === "show-recovery") {
        state.auth.mode = "recovery";
        state.auth.message = "";
        renderAuth();
      }
      if (action === "start-email") startEmailLogin();
      if (action === "verify-email") verifyEmailLogin();
      if (action === "verify-recovery") verifyRecoveryLogin();
      if (action === "register-passkey") registerPasskey();
      if (action === "logout") logout();
      return;
    }

    const authBackdrop = event.target.closest("#authModal");
    if (authBackdrop && event.target === authBackdrop) {
      closeAuthModal();
      return;
    }

    const routeTarget = event.target.closest("[data-route]");
    if (routeTarget) {
      event.preventDefault();
      showRoute(routeTarget.dataset.route);
      return;
    }

    const plannerBackendButton = event.target.closest("[data-planner-backend]");
    if (plannerBackendButton) {
      setPlannerBackend(plannerBackendButton.dataset.plannerBackend);
      persistState();
      return;
    }

    const choice = event.target.closest("[data-choice-group]");
    if (choice) {
      const group = choice.dataset.choiceGroup;
      document.querySelectorAll(`[data-choice-group="${group}"]`).forEach((button) => button.classList.remove("selected"));
      choice.classList.add("selected");
      if (group === "need") renderProgramDetails();
      return;
    }

    const chip = event.target.closest(".chip");
    if (chip) {
      const parent = chip.parentElement;
      parent.querySelectorAll(".chip").forEach((button) => button.classList.remove("selected"));
      chip.classList.add("selected");
      return;
    }

    const switchButton = event.target.closest(".switch");
    if (switchButton) {
      switchButton.classList.toggle("on");
      return;
    }

    const costCurrencyButton = event.target.closest("[data-cost-currency]");
    if (costCurrencyButton) {
      state.costCurrency = costCurrencyButton.dataset.costCurrency;
      persistState();
      renderCostCard(state.costs, selectedOption());
      return;
    }

    const generateButton = event.target.closest("#generateOptionsButton");
    if (generateButton) {
      generateOptions();
      return;
    }

    const openPlanButton = event.target.closest("[data-open-plan-option-id]");
    if (openPlanButton) {
      if (!state.reportId) {
        state.selectedOptionId = openPlanButton.dataset.openPlanOptionId;
        renderCities();
        renderPlan();
        showRoute("plan");
        return;
      }
      selectOption(openPlanButton.dataset.openPlanOptionId);
      return;
    }

    const compareCard = event.target.closest(".city-card[data-compare-option-id]");
    if (compareCard) {
      if (!state.reportId) {
        state.selectedOptionId = compareCard.dataset.compareOptionId;
        renderCities();
        renderPlan();
        return;
      }
      selectComparisonOption(compareCard.dataset.compareOptionId);
      return;
    }

    const selectButton = event.target.closest("[data-option-id]");
    if (selectButton) {
      selectOption(selectButton.dataset.optionId);
      return;
    }

    const regenerateButton = event.target.closest("#regenerateTimelineButton");
    if (regenerateButton) {
      regenerateTimeline();
    }
  });

  document.addEventListener("change", (event) => {
    const checkbox = event.target.closest("[data-readiness-id]");
    if (checkbox) {
      updateReadiness(checkbox.dataset.readinessId, checkbox.checked);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !document.querySelector("#authModal")?.hidden) {
      closeAuthModal();
      return;
    }
    if (event.key !== "Enter" || document.querySelector("#authModal")?.hidden) return;
    if (event.target.closest("#authCode")) {
      event.preventDefault();
      verifyEmailLogin();
    }
    if (event.target.closest("#authRecoveryCode")) {
      event.preventDefault();
      verifyRecoveryLogin();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (!["Enter", " "].includes(event.key)) return;
    const compareCard = event.target.closest(".city-card[data-compare-option-id]");
    if (!compareCard) return;
    event.preventDefault();
    selectComparisonOption(compareCard.dataset.compareOptionId);
  });

  window.addEventListener("hashchange", () => {
    const route = location.hash.replace("#", "");
    if (route === "plan") renderPlan();
    if (route === "readiness") renderReadiness();
    if (route === "agent-progress") renderAgentProgress();
    showRoute(route);
  });
}

restoreState();
setPlannerBackend(state.plannerBackend || "adk");
renderAgentProgress();
renderProgramDetails();
renderCities();
renderPlan();
renderReadiness();
bindInteractions();
showRoute(location.hash.replace("#", "") || "intake");
refreshAuthSession();
