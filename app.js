const routes = ["intake", "agent-progress", "compare", "plan", "readiness"];
const APP_BUILD_ID = "20260715-insurance-i18n";
const isLocalHost = ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
const API_BASE_URL = window.MEDTOUR_API_BASE_URL || (isLocalHost ? "http://127.0.0.1:8000" : "");
const RMB_PER_SGD = 5.35;
const SUPPORTED_LANGUAGES = ["en", "zh-Hans", "id"];
const SINGAPORE_MEDICAL_BUDGET_SGD = {
  eye_surgery: { default: 6200, smile_pro: 6500, lasik: 5200, icl: 9000, cataract: 7000 },
  dental_care: { default: 9000, single_implant: 5500, multiple_implants: 14000, crown_bridge: 6500, root_canal: 1800 },
  health_checkup: { default: 2500, executive_screening: 3200, cardio_screening: 2800, cancer_markers: 2200, women_health: 2600 },
  car_t_blood_cancer: { default: 350000, car_t_consult: 12000, b_cell_lymphoma: 360000, multiple_myeloma: 380000, leukemia: 390000 },
};

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
  language: "en",
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

const UI_TEXT = {
  en: {
    "intake.title": "Plan Your Medical Journey",
    "intake.subtitle": "Let us help you find the best destinations, clinics, and travel options tailored to your needs.",
    "intake.language.title": "Language",
    "intake.language.label": "Preferred language",
    "intake.medicalNeed.title": "What is your medical need?",
    "intake.medicalNeed.eye_surgery": "Eye Surgery",
    "intake.medicalNeed.dental_care": "Dental Implants",
    "intake.medicalNeed.health_checkup": "Health Checkups",
    "intake.medicalNeed.car_t_blood_cancer": "CAR-T Blood Cancer",
    "intake.origin.title": "Where are you traveling from?",
    "intake.origin.nationality": "Nationality / Residence",
    "intake.origin.nationalityAria": "Nationality or residence",
    "intake.origin.departureCity": "Departure City",
    "intake.origin.insuranceHolder": "Current Insurance Holder",
    "intake.origin.insurancePlaceholder": "e.g. AIA, Prudential, Cigna",
    "intake.travelDates.title": "When do you plan to travel?",
    "intake.travelDates.estimatedDates": "Estimated Dates",
    "intake.travelDates.duration": "Estimated Duration",
    "intake.travelDates.duration_3_4": "3-4 days",
    "intake.travelDates.duration_5_7": "5-7 days",
    "intake.travelDates.duration_8_plus": "8+ days",
    "intake.preferences.title": "Preferences & Flexibility",
    "intake.preferences.winterTitle": "Winter Travel",
    "intake.preferences.winterBody": "I prefer traveling during winter months.",
    "intake.preferences.winterAria": "Winter travel enabled",
    "intake.preferences.offSeasonTitle": "Off-Season Flexibility",
    "intake.preferences.offSeasonBody": "I'm flexible to travel during off-peak seasons for better rates.",
    "intake.preferences.offSeasonAria": "Off season disabled",
    "agentProgress.label": "Multi-Agent System",
    "agentProgress.title": "Generating Care Plans",
    "agentProgress.currentWork": "Current Agent Work",
    "agentProgress.complete": "Complete",
    "compare.breadcrumb.costEstimates": "Cost Estimates",
    "compare.breadcrumb.specialty": "Ophthalmology",
    "compare.title": "Multi-City Comparison",
    "compare.subtitle": "Based on your profile and travel preferences, we analyzed top medical centers across China. Prices include estimated hospital fees, flights from Singapore, hotels, and local accommodations.",
    "compare.adjust": "Adjust Parameters",
    "compare.analysisTitle": "Side-by-Side Analysis",
    "compare.tableAria": "City plan comparison",
    "compare.metric": "Metric",
    "compare.noAgentOptions": "No Agent Options",
    "compare.noPlansTitle": "No city plans returned",
    "compare.noPlansBody": "The agent run did not produce usable city options.",
    "compare.noPlansHint": "Return to intake and try Agents again, or switch to Local to verify the planner contract.",
    "compare.cityOption": "City Option",
    "compare.internationalEstimate": "International patient planning estimate",
    "compare.totalCost": "Est. Total Cost",
    "compare.duration": "Total Duration",
    "compare.days": "Days",
    "compare.savings": "Est. Savings vs Home",
    "compare.confidence": "Confidence",
    "compare.riskSingular": "Risk",
    "compare.riskPlural": "Risks",
    "compare.viewTimeline": "View Timeline",
    "compare.selectPlan": "Select Plan",
    "compare.sectionMedicalTravel": "Medical & Travel",
    "compare.sectionCosts": "Costs",
    "compare.sectionInsurance": "Insurance Readiness",
    "compare.sectionRisk": "AI Risk Analysis",
    "compare.hospital": "Hospital",
    "compare.flight": "Flight",
    "compare.hotel": "Hotel",
    "compare.medicalEstimate": "Medical estimate",
    "compare.insuranceEstimate": "Insurance estimate",
    "compare.totalEstimate": "Total estimate",
    "compare.estimatedSavings": "Estimated savings",
    "compare.policyReview": "Policy review",
    "compare.hospitalBilling": "Hospital billing",
    "compare.identifiedFactors": "Identified factors",
    "compare.noGeneratedOptions": "No generated options",
    "compare.noCityOptionsStatus": "The agent response had no city_options.",
    "plan.backCompare": "Compare Cities",
    "plan.selectedPlan": "Selected Plan",
    "plan.cityPlan": "{city} Plan",
    "plan.chooseCity": "Generate options to choose a city.",
    "plan.navSummary": "Plan Summary",
    "plan.navMedical": "Medical Plan",
    "plan.navTimeline": "Timeline",
    "plan.navCosts": "Cost Breakdown",
    "plan.navReadiness": "Readiness",
    "plan.title": "Itinerary Timeline",
    "plan.subtitleSelected": "Detailed schedule for your care journey in {city}.",
    "plan.subtitleDefault": "Generate options to render a detailed schedule.",
    "plan.exportPdf": "Export PDF",
    "plan.regenerate": "Regenerate Timeline",
    "plan.noTimelineTitle": "No timeline yet",
    "plan.noTimelineBody": "Generate options and select a city plan.",
    "plan.day": "Day",
    "plan.estimated": "Est.",
    "plan.mediumConfidence": "medium confidence",
    "plan.medicalConstraint": "Medical constraint",
    "plan.cityPlans": "City Plans",
    "plan.compareCityPlans": "Generate options to compare city plans.",
    "plan.costTitle": "Est. Costs",
    "plan.totalEstimatedCost": "Total Estimated Cost",
    "plan.costNote": "Costs are API estimates for planning. {currencyNote}Confirm hospital, flight, hotel, visa, and payment details before booking.",
    "plan.rmbNote": "RMB uses an estimate of {rate} RMB per SGD. ",
    "plan.insuranceTitle": "Insurance Policy",
    "plan.noInsurance": "Generate and select a city plan to review insurance suggestions.",
    "plan.insurance.currentHolder": "Current holder",
    "plan.insurance.providerGuidance": "Provider guidance",
    "plan.insurance.match": " match",
    "plan.insurance.lookupNeeded": " lookup needed",
    "plan.insurance.hospitalBilling": "Hospital billing",
    "plan.insurance.preauthorization": "Pre-authorization",
    "plan.insurance.requiredLikely": "Required or likely required",
    "plan.insurance.notFlagged": "Not flagged",
    "plan.insurance.directBillingAssumption": "Direct billing assumption",
    "plan.insurance.estimatedPremium": "Estimated premium",
    "plan.insurance.providerChecklist": "Provider checklist",
    "plan.insurance.preauthQuestions": "Pre-authorization questions",
    "plan.insurance.claimDocuments": "Claim documents",
    "plan.insurance.risksExclusions": "Risks and exclusions",
    "plan.insurance.suggestions": "Suggestions",
    "plan.insurance.helpfulLinks": "Helpful links",
    "plan.insurance.notProvided": "Not provided",
    "plan.insurance.needsReview": "Needs review",
    "plan.insurance.needsInsurerConfirmation": "Needs insurer confirmation",
    "plan.insurance.confirmHospital": "Confirm with hospital",
    "plan.insurance.defaultDirectBilling": "Assume self-pay first until insurer and hospital confirm otherwise.",
    "plan.insurance.defaultProviderChecklist": "Ask for insurer name, issuing country, plan type, member services contact, and policy territory.",
    "plan.insurance.defaultPreauthQuestions": "Confirm overseas planned-care coverage, direct billing, reimbursement route, and claim limits before payment.",
    "plan.insurance.defaultClaimDocuments": "Collect itemized invoice, official receipt, diagnosis or medical report, prescriptions, and claim forms.",
    "plan.insurance.defaultRisks": "Coverage exclusions, pre-existing conditions, and missing pre-authorization must be checked with the insurer.",
    "plan.insurance.defaultSuggestions": "Confirm coverage, payment route, invoices, and claim documents with your insurer and the hospital.",
    "plan.insurance.termsNote": "Insurance terms vary by policy. Confirm coverage, exclusions, pre-authorization, and claim documents with your insurer and the hospital before booking.",
    "intake.actions.agents": "Agents",
    "intake.actions.local": "Local",
    "intake.actions.saveDraft": "Save Draft",
    "intake.actions.generate": "Generate Options",
    "intake.actions.generating": "Generating...",
    "status.agentUnavailable": "Agent planner is not configured on this deployment. Local planner selected.",
    "status.agentUnavailableTitle": "Agent planner is not configured on this deployment",
    "status.useAgentsTitle": "Use the multi-agent planner",
    "status.agentRunning": "Agents are generating multi-city options...",
    "status.localRunning": "Generating multi-city options from backend API...",
    "status.generated": "Generated {count} city options. Choose a plan to view details.",
    "agent.waiting": "Waiting to start.",
    "agent.ready": "Final report is ready. Opening the city comparison.",
    "agent.stopped": "Agent run stopped: {message}",
    "agent.subtitle.running": "Agents are coordinating your profile, hospitals, insurance, travel, and timeline details.",
    "agent.subtitle.failed": "The agent run needs attention before the report can be shown.",
    "agent.subtitle.complete": "The agent run is complete.",
    "agent.status.error": "Error",
    "agent.status.complete": "Complete",
    "agent.status.working": "Working",
    "agent.status.queued": "Queued",
  },
  "zh-Hans": {
    "intake.title": "规划您的跨境医疗行程",
    "intake.subtitle": "我们会根据您的需求，帮您筛选合适的目的地、医院和出行方案。",
    "intake.language.title": "语言",
    "intake.language.label": "首选语言",
    "intake.medicalNeed.title": "您的医疗需求是什么？",
    "intake.medicalNeed.eye_surgery": "眼科手术",
    "intake.medicalNeed.dental_care": "牙科种植",
    "intake.medicalNeed.health_checkup": "健康体检",
    "intake.medicalNeed.car_t_blood_cancer": "CAR-T 血液肿瘤",
    "intake.origin.title": "您从哪里出发？",
    "intake.origin.nationality": "国籍 / 居住地",
    "intake.origin.nationalityAria": "国籍或居住地",
    "intake.origin.departureCity": "出发城市",
    "intake.origin.insuranceHolder": "当前保险公司",
    "intake.origin.insurancePlaceholder": "例如 AIA、Prudential、Cigna",
    "intake.travelDates.title": "您计划什么时候出行？",
    "intake.travelDates.estimatedDates": "预计日期",
    "intake.travelDates.duration": "预计停留时长",
    "intake.travelDates.duration_3_4": "3-4 天",
    "intake.travelDates.duration_5_7": "5-7 天",
    "intake.travelDates.duration_8_plus": "8 天以上",
    "intake.preferences.title": "偏好与灵活度",
    "intake.preferences.winterTitle": "冬季出行",
    "intake.preferences.winterBody": "我更倾向于在冬季月份出行。",
    "intake.preferences.winterAria": "已启用冬季出行",
    "intake.preferences.offSeasonTitle": "淡季灵活度",
    "intake.preferences.offSeasonBody": "我可以接受淡季出行，以获得更好的价格。",
    "intake.preferences.offSeasonAria": "未启用淡季灵活度",
    "agentProgress.label": "多智能体系统",
    "agentProgress.title": "正在生成医疗方案",
    "agentProgress.currentWork": "当前智能体工作",
    "agentProgress.complete": "完成",
    "compare.breadcrumb.costEstimates": "费用估算",
    "compare.breadcrumb.specialty": "眼科",
    "compare.title": "多城市对比",
    "compare.subtitle": "根据您的档案和出行偏好，我们分析了中国多个优质医疗中心。价格包含预计医院费用、从新加坡出发的航班、酒店和本地安排。",
    "compare.adjust": "调整参数",
    "compare.analysisTitle": "并排分析",
    "compare.tableAria": "城市方案对比",
    "compare.metric": "指标",
    "compare.noAgentOptions": "没有智能体方案",
    "compare.noPlansTitle": "未返回城市方案",
    "compare.noPlansBody": "智能体运行未生成可用的城市方案。",
    "compare.noPlansHint": "请返回问诊页重试智能体，或切换到本地规划器以验证规划合约。",
    "compare.cityOption": "城市方案",
    "compare.internationalEstimate": "国际患者规划估算",
    "compare.totalCost": "预计总费用",
    "compare.duration": "总时长",
    "compare.days": "天",
    "compare.savings": "相对本地预计节省",
    "compare.confidence": "置信度",
    "compare.riskSingular": "风险",
    "compare.riskPlural": "风险",
    "compare.viewTimeline": "查看时间线",
    "compare.selectPlan": "选择方案",
    "compare.sectionMedicalTravel": "医疗与出行",
    "compare.sectionCosts": "费用",
    "compare.sectionInsurance": "保险准备度",
    "compare.sectionRisk": "AI 风险分析",
    "compare.hospital": "医院",
    "compare.flight": "航班",
    "compare.hotel": "酒店",
    "compare.medicalEstimate": "医疗估算",
    "compare.insuranceEstimate": "保险估算",
    "compare.totalEstimate": "总费用估算",
    "compare.estimatedSavings": "预计节省",
    "compare.policyReview": "保单审核",
    "compare.hospitalBilling": "医院账单",
    "compare.identifiedFactors": "已识别因素",
    "compare.noGeneratedOptions": "没有生成方案",
    "compare.noCityOptionsStatus": "智能体响应中没有 city_options。",
    "plan.backCompare": "对比城市",
    "plan.selectedPlan": "已选方案",
    "plan.cityPlan": "{city} 方案",
    "plan.chooseCity": "生成方案后选择城市。",
    "plan.navSummary": "方案概览",
    "plan.navMedical": "医疗方案",
    "plan.navTimeline": "时间线",
    "plan.navCosts": "费用明细",
    "plan.navReadiness": "准备清单",
    "plan.title": "行程时间线",
    "plan.subtitleSelected": "{city} 医疗行程的详细安排。",
    "plan.subtitleDefault": "生成方案后显示详细日程。",
    "plan.exportPdf": "导出 PDF",
    "plan.regenerate": "重新生成时间线",
    "plan.noTimelineTitle": "暂无时间线",
    "plan.noTimelineBody": "请先生成方案并选择城市。",
    "plan.day": "第",
    "plan.estimated": "估算",
    "plan.mediumConfidence": "中等置信度",
    "plan.medicalConstraint": "医疗约束",
    "plan.cityPlans": "城市方案",
    "plan.compareCityPlans": "生成方案以对比城市。",
    "plan.costTitle": "预计费用",
    "plan.totalEstimatedCost": "预计总费用",
    "plan.costNote": "费用为 API 规划估算。{currencyNote}预订前请确认医院、航班、酒店、签证和支付细节。",
    "plan.rmbNote": "人民币按 1 SGD ≈ {rate} RMB 估算。",
    "plan.insuranceTitle": "保险政策",
    "plan.noInsurance": "生成并选择城市方案后查看保险建议。",
    "plan.insurance.currentHolder": "当前保险公司",
    "plan.insurance.providerGuidance": "保险公司指引",
    "plan.insurance.match": " 匹配",
    "plan.insurance.lookupNeeded": " 需要查询",
    "plan.insurance.hospitalBilling": "医院账单",
    "plan.insurance.preauthorization": "预授权",
    "plan.insurance.requiredLikely": "需要或很可能需要",
    "plan.insurance.notFlagged": "未标记",
    "plan.insurance.directBillingAssumption": "直付假设",
    "plan.insurance.estimatedPremium": "预计保费",
    "plan.insurance.providerChecklist": "保险公司确认清单",
    "plan.insurance.preauthQuestions": "预授权问题",
    "plan.insurance.claimDocuments": "理赔文件",
    "plan.insurance.risksExclusions": "风险与除外责任",
    "plan.insurance.suggestions": "建议",
    "plan.insurance.helpfulLinks": "参考链接",
    "plan.insurance.notProvided": "未提供",
    "plan.insurance.needsReview": "需要审核",
    "plan.insurance.needsInsurerConfirmation": "需要保险公司确认",
    "plan.insurance.confirmHospital": "与医院确认",
    "plan.insurance.defaultDirectBilling": "在保险公司和医院确认前，先假设需要自费后报销。",
    "plan.insurance.defaultProviderChecklist": "询问保险公司名称、签发国家、计划类型、会员服务联系方式和保单地区。",
    "plan.insurance.defaultPreauthQuestions": "付款前确认海外计划医疗保障、直付、报销路径和理赔限额。",
    "plan.insurance.defaultClaimDocuments": "收集明细发票、正式收据、诊断或医疗报告、处方和理赔表。",
    "plan.insurance.defaultRisks": "需要向保险公司确认除外责任、既往症和缺失预授权等问题。",
    "plan.insurance.defaultSuggestions": "与保险公司和医院确认保障范围、付款路径、发票和理赔文件。",
    "plan.insurance.termsNote": "保险条款因保单而异。预订前请与保险公司和医院确认保障范围、除外责任、预授权和理赔文件。",
    "intake.actions.agents": "智能体",
    "intake.actions.local": "本地",
    "intake.actions.saveDraft": "保存草稿",
    "intake.actions.generate": "生成方案",
    "intake.actions.generating": "生成中...",
    "status.agentUnavailable": "此部署未配置智能体规划器，已选择本地规划器。",
    "status.agentUnavailableTitle": "此部署未配置智能体规划器",
    "status.useAgentsTitle": "使用多智能体规划器",
    "status.agentRunning": "智能体正在生成多城市方案...",
    "status.localRunning": "正在通过后端 API 生成多城市方案...",
    "status.generated": "已生成 {count} 个城市方案。请选择一个方案查看详情。",
    "agent.waiting": "等待开始。",
    "agent.ready": "最终报告已准备好，即将打开城市对比。",
    "agent.stopped": "智能体运行已停止：{message}",
    "agent.subtitle.running": "智能体正在协同处理您的档案、医院、保险、出行和时间线细节。",
    "agent.subtitle.failed": "智能体运行需要处理后才能显示报告。",
    "agent.subtitle.complete": "智能体运行已完成。",
    "agent.status.error": "错误",
    "agent.status.complete": "完成",
    "agent.status.working": "处理中",
    "agent.status.queued": "排队中",
  },
  id: {
    "intake.title": "Rencanakan Perjalanan Medis Anda",
    "intake.subtitle": "Kami membantu menemukan tujuan, klinik, dan opsi perjalanan yang sesuai dengan kebutuhan Anda.",
    "intake.language.title": "Bahasa",
    "intake.language.label": "Bahasa pilihan",
    "intake.medicalNeed.title": "Apa kebutuhan medis Anda?",
    "intake.medicalNeed.eye_surgery": "Operasi Mata",
    "intake.medicalNeed.dental_care": "Implan Gigi",
    "intake.medicalNeed.health_checkup": "Pemeriksaan Kesehatan",
    "intake.medicalNeed.car_t_blood_cancer": "Kanker Darah CAR-T",
    "intake.origin.title": "Dari mana Anda berangkat?",
    "intake.origin.nationality": "Kewarganegaraan / Domisili",
    "intake.origin.nationalityAria": "Kewarganegaraan atau domisili",
    "intake.origin.departureCity": "Kota Keberangkatan",
    "intake.origin.insuranceHolder": "Penyedia Asuransi Saat Ini",
    "intake.origin.insurancePlaceholder": "mis. AIA, Prudential, Cigna",
    "intake.travelDates.title": "Kapan Anda berencana bepergian?",
    "intake.travelDates.estimatedDates": "Perkiraan Tanggal",
    "intake.travelDates.duration": "Perkiraan Durasi",
    "intake.travelDates.duration_3_4": "3-4 hari",
    "intake.travelDates.duration_5_7": "5-7 hari",
    "intake.travelDates.duration_8_plus": "8+ hari",
    "intake.preferences.title": "Preferensi & Fleksibilitas",
    "intake.preferences.winterTitle": "Perjalanan Musim Dingin",
    "intake.preferences.winterBody": "Saya lebih suka bepergian pada bulan musim dingin.",
    "intake.preferences.winterAria": "Perjalanan musim dingin aktif",
    "intake.preferences.offSeasonTitle": "Fleksibilitas Musim Sepi",
    "intake.preferences.offSeasonBody": "Saya fleksibel bepergian di luar musim ramai untuk tarif yang lebih baik.",
    "intake.preferences.offSeasonAria": "Musim sepi tidak aktif",
    "agentProgress.label": "Sistem Multi-Agen",
    "agentProgress.title": "Membuat Rencana Perawatan",
    "agentProgress.currentWork": "Pekerjaan Agen Saat Ini",
    "agentProgress.complete": "Selesai",
    "compare.breadcrumb.costEstimates": "Estimasi Biaya",
    "compare.breadcrumb.specialty": "Oftalmologi",
    "compare.title": "Perbandingan Multi-Kota",
    "compare.subtitle": "Berdasarkan profil dan preferensi perjalanan Anda, kami menganalisis pusat medis unggulan di China. Harga mencakup estimasi biaya rumah sakit, penerbangan dari Singapura, hotel, dan akomodasi lokal.",
    "compare.adjust": "Sesuaikan Parameter",
    "compare.analysisTitle": "Analisis Berdampingan",
    "compare.tableAria": "Perbandingan rencana kota",
    "compare.metric": "Metrik",
    "compare.noAgentOptions": "Tidak Ada Opsi Agen",
    "compare.noPlansTitle": "Tidak ada rencana kota yang dikembalikan",
    "compare.noPlansBody": "Proses agen tidak menghasilkan opsi kota yang dapat digunakan.",
    "compare.noPlansHint": "Kembali ke intake dan coba Agen lagi, atau beralih ke Lokal untuk memeriksa kontrak perencana.",
    "compare.cityOption": "Opsi Kota",
    "compare.internationalEstimate": "Estimasi perencanaan pasien internasional",
    "compare.totalCost": "Estimasi Total Biaya",
    "compare.duration": "Total Durasi",
    "compare.days": "Hari",
    "compare.savings": "Estimasi Hemat vs Negara Asal",
    "compare.confidence": "Keyakinan",
    "compare.riskSingular": "Risiko",
    "compare.riskPlural": "Risiko",
    "compare.viewTimeline": "Lihat Jadwal",
    "compare.selectPlan": "Pilih Rencana",
    "compare.sectionMedicalTravel": "Medis & Perjalanan",
    "compare.sectionCosts": "Biaya",
    "compare.sectionInsurance": "Kesiapan Asuransi",
    "compare.sectionRisk": "Analisis Risiko AI",
    "compare.hospital": "Rumah sakit",
    "compare.flight": "Penerbangan",
    "compare.hotel": "Hotel",
    "compare.medicalEstimate": "Estimasi medis",
    "compare.insuranceEstimate": "Estimasi asuransi",
    "compare.totalEstimate": "Estimasi total",
    "compare.estimatedSavings": "Estimasi penghematan",
    "compare.policyReview": "Tinjauan polis",
    "compare.hospitalBilling": "Penagihan rumah sakit",
    "compare.identifiedFactors": "Faktor teridentifikasi",
    "compare.noGeneratedOptions": "Tidak ada opsi yang dibuat",
    "compare.noCityOptionsStatus": "Respons agen tidak memiliki city_options.",
    "plan.backCompare": "Bandingkan Kota",
    "plan.selectedPlan": "Rencana Terpilih",
    "plan.cityPlan": "Rencana {city}",
    "plan.chooseCity": "Buat opsi untuk memilih kota.",
    "plan.navSummary": "Ringkasan Rencana",
    "plan.navMedical": "Rencana Medis",
    "plan.navTimeline": "Jadwal",
    "plan.navCosts": "Rincian Biaya",
    "plan.navReadiness": "Kesiapan",
    "plan.title": "Jadwal Itinerary",
    "plan.subtitleSelected": "Jadwal detail untuk perjalanan perawatan Anda di {city}.",
    "plan.subtitleDefault": "Buat opsi untuk menampilkan jadwal detail.",
    "plan.exportPdf": "Ekspor PDF",
    "plan.regenerate": "Buat Ulang Jadwal",
    "plan.noTimelineTitle": "Belum ada jadwal",
    "plan.noTimelineBody": "Buat opsi dan pilih rencana kota.",
    "plan.day": "Hari",
    "plan.estimated": "Est.",
    "plan.mediumConfidence": "keyakinan sedang",
    "plan.medicalConstraint": "Batasan medis",
    "plan.cityPlans": "Rencana Kota",
    "plan.compareCityPlans": "Buat opsi untuk membandingkan rencana kota.",
    "plan.costTitle": "Estimasi Biaya",
    "plan.totalEstimatedCost": "Total Estimasi Biaya",
    "plan.costNote": "Biaya adalah estimasi API untuk perencanaan. {currencyNote}Konfirmasi rumah sakit, penerbangan, hotel, visa, dan detail pembayaran sebelum memesan.",
    "plan.rmbNote": "RMB menggunakan estimasi {rate} RMB per SGD. ",
    "plan.insuranceTitle": "Polis Asuransi",
    "plan.noInsurance": "Buat dan pilih rencana kota untuk meninjau saran asuransi.",
    "plan.insurance.currentHolder": "Pemegang saat ini",
    "plan.insurance.providerGuidance": "Panduan penyedia",
    "plan.insurance.match": " cocok",
    "plan.insurance.lookupNeeded": " perlu dicek",
    "plan.insurance.hospitalBilling": "Penagihan rumah sakit",
    "plan.insurance.preauthorization": "Pra-otorisasi",
    "plan.insurance.requiredLikely": "Diperlukan atau kemungkinan diperlukan",
    "plan.insurance.notFlagged": "Tidak ditandai",
    "plan.insurance.directBillingAssumption": "Asumsi direct billing",
    "plan.insurance.estimatedPremium": "Estimasi premi",
    "plan.insurance.providerChecklist": "Checklist penyedia",
    "plan.insurance.preauthQuestions": "Pertanyaan pra-otorisasi",
    "plan.insurance.claimDocuments": "Dokumen klaim",
    "plan.insurance.risksExclusions": "Risiko dan pengecualian",
    "plan.insurance.suggestions": "Saran",
    "plan.insurance.helpfulLinks": "Tautan bantuan",
    "plan.insurance.notProvided": "Belum diberikan",
    "plan.insurance.needsReview": "Perlu ditinjau",
    "plan.insurance.needsInsurerConfirmation": "Perlu konfirmasi asuransi",
    "plan.insurance.confirmHospital": "Konfirmasi dengan rumah sakit",
    "plan.insurance.defaultDirectBilling": "Asumsikan bayar sendiri dulu sampai asuransi dan rumah sakit mengonfirmasi.",
    "plan.insurance.defaultProviderChecklist": "Tanyakan nama asuransi, negara penerbit, jenis paket, kontak layanan anggota, dan wilayah polis.",
    "plan.insurance.defaultPreauthQuestions": "Konfirmasi cakupan perawatan luar negeri terencana, direct billing, jalur reimburse, dan batas klaim sebelum pembayaran.",
    "plan.insurance.defaultClaimDocuments": "Kumpulkan invoice terperinci, kuitansi resmi, diagnosis atau laporan medis, resep, dan formulir klaim.",
    "plan.insurance.defaultRisks": "Pengecualian cakupan, kondisi pra-eksisting, dan pra-otorisasi yang belum ada harus dicek dengan asuransi.",
    "plan.insurance.defaultSuggestions": "Konfirmasi cakupan, jalur pembayaran, invoice, dan dokumen klaim dengan asuransi dan rumah sakit.",
    "plan.insurance.termsNote": "Ketentuan asuransi berbeda menurut polis. Konfirmasi cakupan, pengecualian, pra-otorisasi, dan dokumen klaim dengan asuransi serta rumah sakit sebelum memesan.",
    "intake.actions.agents": "Agen",
    "intake.actions.local": "Lokal",
    "intake.actions.saveDraft": "Simpan Draf",
    "intake.actions.generate": "Buat Opsi",
    "intake.actions.generating": "Membuat...",
    "status.agentUnavailable": "Perencana agen belum dikonfigurasi pada deployment ini. Perencana lokal dipilih.",
    "status.agentUnavailableTitle": "Perencana agen belum dikonfigurasi pada deployment ini",
    "status.useAgentsTitle": "Gunakan perencana multi-agen",
    "status.agentRunning": "Agen sedang membuat opsi multi-kota...",
    "status.localRunning": "Membuat opsi multi-kota dari API backend...",
    "status.generated": "Berhasil membuat {count} opsi kota. Pilih rencana untuk melihat detail.",
    "agent.waiting": "Menunggu mulai.",
    "agent.ready": "Laporan final siap. Membuka perbandingan kota.",
    "agent.stopped": "Proses agen berhenti: {message}",
    "agent.subtitle.running": "Agen sedang mengoordinasikan profil, rumah sakit, asuransi, perjalanan, dan jadwal Anda.",
    "agent.subtitle.failed": "Proses agen perlu ditinjau sebelum laporan dapat ditampilkan.",
    "agent.subtitle.complete": "Proses agen selesai.",
    "agent.status.error": "Error",
    "agent.status.complete": "Selesai",
    "agent.status.working": "Berjalan",
    "agent.status.queued": "Antre",
  },
};

function normalizeLanguage(language) {
  return SUPPORTED_LANGUAGES.includes(language) ? language : "en";
}

function t(key, vars = {}) {
  const language = normalizeLanguage(state.language);
  let text = UI_TEXT[language]?.[key] || UI_TEXT.en[key] || key;
  Object.entries(vars).forEach(([name, value]) => {
    text = text.replaceAll(`{${name}}`, String(value));
  });
  return text;
}

function applyTranslations() {
  const language = normalizeLanguage(state.language);
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-attr]").forEach((element) => {
    element.dataset.i18nAttr.split(";").forEach((entry) => {
      const [attr, key] = entry.split(":");
      if (!attr || !key) return;
      element.setAttribute(attr, t(key));
    });
  });
  const languageSelect = document.querySelector("#languageSelect");
  if (languageSelect) languageSelect.value = language;
  if (!state.agentProgress.running && !state.agentProgress.completedStepIds?.length && !state.agentProgress.failedStepId) {
    state.agentProgress.statusMessage = t("agent.waiting");
  }
}

const agentProgressSteps = [
  {
    id: "profile",
    title: "Profile Normalizer Agent",
    icon: "person_search",
    working: "Normalizing medical purpose, program details, passport country, travel dates, insurance holder, and default assumptions.",
    done: "Profile normalized, missing confirmations identified, and planning inputs prepared.",
  },
  {
    id: "medical",
    title: "Medical Rules Agent",
    icon: "medical_information",
    working: "Checking clinical fit, care-cycle constraints, candidate cities, and hospital international department requirements.",
    done: "Medical constraints and candidate city strategy prepared.",
  },
  {
    id: "parallel",
    title: "Parallel City Option Agents",
    icon: "hub",
    working: "Running city planners in parallel for best overall fit, lowest cost, shortest trip, and strongest hospital resources.",
    done: "Diversified city option drafts generated.",
  },
  {
    id: "hospital-contact",
    title: "Hospital Contact Lookup Agent",
    icon: "contact_phone",
    working: "Looking up international department names, registration routes, appointment phone numbers, email availability, and official source records.",
    done: "Hospital contact and registration evidence attached to each option.",
  },
  {
    id: "travel-costs",
    title: "Travel & Budget Agent",
    icon: "payments",
    working: "Estimating flights, foreigner-eligible hotels, local transport, meals, hospital deposits, and Singapore benchmark savings.",
    done: "Travel costs, medical estimates, and savings math prepared.",
  },
  {
    id: "insurance",
    title: "Insurance Policy Agent",
    icon: "health_and_safety",
    working: "Checking pre-authorization, direct-billing likelihood, deposit expectations, invoices, translations, and claim document needs.",
    done: "Insurance and hospital billing notes attached to each city plan.",
  },
  {
    id: "timeline",
    title: "Timeline Detail Agent",
    icon: "timeline",
    working: "Building day-by-day registration, diagnostics, consultation, procedure, discharge, billing, claims, and follow-up steps.",
    done: "Detailed timelines assembled with operational next steps.",
  },
  {
    id: "audit",
    title: "Source & Cost Audit Agent",
    icon: "fact_check",
    working: "Auditing hospital sources, contact confidence, billing evidence, flight and hotel prices, medical estimates, and total-cost arithmetic.",
    done: "Audit status, warnings, source gaps, and cost checks attached.",
  },
  {
    id: "synthesis",
    title: "Report Synthesis Agent",
    icon: "analytics",
    working: "Ranking options, deduplicating cities, calculating comparison metrics, and preparing the final report.",
    done: "Final report ready for comparison.",
  },
];

const agentProgressTextByLanguage = {
  "zh-Hans": {
    profile: {
      title: "用户档案标准化智能体",
      working: "正在标准化医疗目的、项目详情、护照国家、出行日期、保险公司和默认假设。",
      done: "已完成档案标准化，识别缺失确认项，并准备规划输入。",
    },
    medical: {
      title: "医疗规则智能体",
      working: "正在检查临床适配性、治疗周期限制、候选城市和医院国际部要求。",
      done: "已准备医疗约束和候选城市策略。",
    },
    parallel: {
      title: "并行城市方案智能体",
      working: "正在并行规划最佳综合、最低成本、最短行程和医疗资源最强的城市方案。",
      done: "已生成多样化城市方案草案。",
    },
    "hospital-contact": {
      title: "医院联系信息核验智能体",
      working: "正在查找国际部名称、挂号路径、预约电话、邮箱可用性和官方来源记录。",
      done: "已为每个方案附加医院联系和挂号证据。",
    },
    "travel-costs": {
      title: "出行与预算智能体",
      working: "正在估算机票、可接待外宾酒店、本地交通、餐饮、医院押金和新加坡基准节省。",
      done: "已准备出行成本、医疗估算和节省金额。",
    },
    insurance: {
      title: "保险政策智能体",
      working: "正在检查预授权、直付可能性、押金预期、发票、翻译和理赔文件需求。",
      done: "已为每个城市方案附加保险和医院账单说明。",
    },
    timeline: {
      title: "时间线细化智能体",
      working: "正在构建逐日挂号、检查、会诊、治疗、出院、账单、理赔和复查步骤。",
      done: "已组装包含操作步骤的详细时间线。",
    },
    audit: {
      title: "来源与费用审计智能体",
      working: "正在审计医院来源、联系信息可信度、账单证据、机票酒店价格、医疗估算和总费用计算。",
      done: "已附加审计状态、提醒、来源缺口和费用检查。",
    },
    synthesis: {
      title: "报告合成智能体",
      working: "正在排序方案、合并重复城市、计算对比指标并准备最终报告。",
      done: "最终报告已准备好用于对比。",
    },
  },
  id: {
    profile: {
      title: "Agen Normalisasi Profil",
      working: "Menormalkan tujuan medis, detail program, negara paspor, tanggal perjalanan, penyedia asuransi, dan asumsi default.",
      done: "Profil dinormalkan, konfirmasi yang kurang diidentifikasi, dan input perencanaan disiapkan.",
    },
    medical: {
      title: "Agen Aturan Medis",
      working: "Memeriksa kesesuaian klinis, batasan siklus perawatan, kandidat kota, dan kebutuhan departemen internasional rumah sakit.",
      done: "Batasan medis dan strategi kandidat kota sudah disiapkan.",
    },
    parallel: {
      title: "Agen Opsi Kota Paralel",
      working: "Menjalankan perencana kota secara paralel untuk opsi terbaik, termurah, tersingkat, dan sumber daya medis terkuat.",
      done: "Draf opsi kota yang beragam sudah dibuat.",
    },
    "hospital-contact": {
      title: "Agen Pencarian Kontak Rumah Sakit",
      working: "Mencari nama departemen internasional, alur registrasi, nomor janji temu, ketersediaan email, dan catatan sumber resmi.",
      done: "Bukti kontak dan registrasi rumah sakit ditambahkan ke setiap opsi.",
    },
    "travel-costs": {
      title: "Agen Perjalanan & Anggaran",
      working: "Mengestimasi penerbangan, hotel ramah tamu asing, transportasi lokal, makan, deposit rumah sakit, dan penghematan terhadap benchmark Singapura.",
      done: "Biaya perjalanan, estimasi medis, dan perhitungan penghematan sudah disiapkan.",
    },
    insurance: {
      title: "Agen Polis Asuransi",
      working: "Memeriksa pra-otorisasi, kemungkinan direct billing, ekspektasi deposit, invoice, terjemahan, dan dokumen klaim.",
      done: "Catatan asuransi dan penagihan rumah sakit ditambahkan ke setiap rencana kota.",
    },
    timeline: {
      title: "Agen Detail Jadwal",
      working: "Menyusun langkah harian untuk registrasi, diagnostik, konsultasi, prosedur, pulang, penagihan, klaim, dan tindak lanjut.",
      done: "Jadwal detail dengan langkah operasional sudah disusun.",
    },
    audit: {
      title: "Agen Audit Sumber & Biaya",
      working: "Mengaudit sumber rumah sakit, kepercayaan kontak, bukti penagihan, harga penerbangan dan hotel, estimasi medis, serta aritmetika total biaya.",
      done: "Status audit, peringatan, celah sumber, dan pemeriksaan biaya sudah ditambahkan.",
    },
    synthesis: {
      title: "Agen Sintesis Laporan",
      working: "Memeringkat opsi, menghapus duplikasi kota, menghitung metrik perbandingan, dan menyiapkan laporan akhir.",
      done: "Laporan final siap untuk perbandingan.",
    },
  },
};

function agentStepText(step, field) {
  return agentProgressTextByLanguage[normalizeLanguage(state.language)]?.[step.id]?.[field] || step[field];
}

function firstAgentWorkingMessage() {
  return agentStepText(agentProgressSteps[0], "working");
}

const agentProgressDwellMs = {
  profile: 2600,
  medical: 4200,
  parallel: 4400,
  "hospital-contact": 3800,
  "travel-costs": 3200,
  insurance: 2800,
  timeline: 2600,
  audit: 2400,
  synthesis: 1800,
};

const previewHospitalName = "Guangdong Provincial People's Hospital - Concord Medical Center";
const previewHospitalDesk = "Concord Medical Center international patient registration desk";
const previewRegistrationEmail = "gdcmc@yahoo.cn";
const previewRegistrationEmailStatus = "official_general_email";
const previewAppointmentPhone = "(+8620) 83874283; (+8620) 87374289-8991";
const previewHotelName = "The Garden Hotel Guangzhou";
const previewHotelAddress = "368 Huanshi Dong Road, Yuexiu District, Guangzhou";

const fallbackOptions = [
  {
    option_id: "preview_guangzhou",
    city: "Guangzhou",
    recommendation_label: "Preview International Plan",
    target_hospital: previewHospitalName,
    medical_purpose: "eye_surgery",
    procedure_subtype: "smile_pro",
    program_details: "Current prescription: -4.50 both eyes, mild astigmatism; contact lens usage: soft lenses",
    recommendation_reason: "Preview showing the international hospital workflow, doctor assignment, and insurance document steps.",
    required_days: 4,
    flight: {
      airline: "Singapore Airlines",
      flight_number: "SQ850",
      departure_airport: "SIN",
      arrival_airport: "CAN",
      departure_time: "2026-08-12T08:00:00+08:00",
      arrival_time: "2026-08-12T13:30:00+08:00",
      estimated_cost: { amount: 430, currency: "SGD" },
    },
    hotel: {
      name: previewHotelName,
      address: previewHotelAddress,
      nightly_rate: { amount: 145, currency: "SGD" },
      nights: 3,
      distance_to_hospital: "Same Yuexiu medical district; confirm live route before booking",
      foreign_guest_eligible: true,
    },
    cost_breakdown: {
      medical: { amount: 3500, low: 2800, high: 4200, currency: "SGD" },
      flight: { amount: 430, currency: "SGD" },
      hotel: { amount: 435, nightly_rate: 145, nights: 3, currency: "SGD" },
      local_transport: { amount: 89, currency: "SGD" },
      meals: { amount: 126, currency: "SGD" },
      visa_and_payment_setup: { amount: 80, currency: "SGD" },
      travel_insurance: { amount: 95, currency: "SGD" },
    },
    total_estimated_cost: { amount: 4755, currency: "SGD" },
    home_country_benchmark: { amount: 6500, currency: "SGD" },
    estimated_net_savings: { amount: 1745, currency: "SGD" },
    hospital_visit_protocol: {
      registration_contact: {
        desk: previewHospitalDesk,
        email: previewRegistrationEmail,
        email_status: previewRegistrationEmailStatus,
        appointment_phone: previewAppointmentPhone,
      },
      suggested_doctor: {
        name: "",
        specialty: "Cornea and refractive surgery consultant",
        request_note: "Request the International Patient Service team to assign or confirm a senior refractive-surgery consultant before deposit payment.",
      },
    },
    insurance_policy: {
      current_holder: "AIA",
      hospital_name: previewHospitalName,
      medical_purpose: "eye_surgery",
      policy_status: "needs_insurer_confirmation",
      summary: "Preview policy review. Confirm pre-authorization, direct billing, and reimbursement documents before booking.",
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
            title: "Arrival flight SQ850",
            start_time: "2026-08-12T08:00:00+08:00",
            end_time: "2026-08-12T13:30:00+08:00",
            location_name: "CAN",
            estimated_cost: { amount: 430, currency: "SGD" },
            confidence_level: "medium",
            details: {},
          },
          {
            category: "hotel",
            title: "Hotel check-in",
            start_time: "2026-08-12T15:30:00+08:00",
            end_time: "2026-08-12T16:00:00+08:00",
            location_name: previewHotelName,
            address: previewHotelAddress,
            confidence_level: "medium",
            details: {},
          },
          {
            category: "medical",
            title: "International desk pre-registration email check",
            start_time: "2026-08-12T16:30:00+08:00",
            end_time: "2026-08-12T17:15:00+08:00",
            location_name: previewHospitalName,
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_desk: previewHospitalDesk,
              registration_email: previewRegistrationEmail,
              registration_email_status: previewRegistrationEmailStatus,
              appointment_phone: previewAppointmentPhone,
              suggested_doctor_name: "",
              suggested_doctor_specialty: "Cornea and refractive surgery consultant",
              suggested_doctor_request: "Request the International Patient Service team to assign or confirm a senior refractive-surgery consultant before deposit payment.",
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
            location_name: previewHospitalName,
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_desk: previewHospitalDesk,
              registration_email: previewRegistrationEmail,
              registration_email_status: previewRegistrationEmailStatus,
              appointment_phone: previewAppointmentPhone,
              suggested_doctor_name: "",
              suggested_doctor_specialty: "Cornea and refractive surgery consultant",
              suggested_doctor_request: "Request the International Patient Service team to assign or confirm a senior refractive-surgery consultant before deposit payment.",
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
            location_name: previewHospitalName,
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: previewRegistrationEmail,
              registration_email_status: previewRegistrationEmailStatus,
              appointment_phone: previewAppointmentPhone,
              suggested_doctor_name: "",
              suggested_doctor_specialty: "Cornea and refractive surgery consultant",
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
            location_name: previewHospitalName,
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: previewRegistrationEmail,
              registration_email_status: previewRegistrationEmailStatus,
              appointment_phone: previewAppointmentPhone,
              suggested_doctor_name: "",
              suggested_doctor_specialty: "Cornea and refractive surgery consultant",
              suggested_doctor_request: "Ask the international clinic to assign or confirm the operating surgeon before final payment.",
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
            location_name: previewHospitalName,
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: previewRegistrationEmail,
              registration_email_status: previewRegistrationEmailStatus,
              appointment_phone: previewAppointmentPhone,
              suggested_doctor_name: "",
              suggested_doctor_specialty: "Cornea and refractive surgery consultant",
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
            location_name: previewHospitalName,
            estimated_cost: { amount: 3500, currency: "SGD" },
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: previewRegistrationEmail,
              registration_email_status: previewRegistrationEmailStatus,
              appointment_phone: previewAppointmentPhone,
              suggested_doctor_name: "",
              suggested_doctor_specialty: "Cornea and refractive surgery consultant",
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
            location_name: previewHospitalName,
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: previewRegistrationEmail,
              registration_email_status: previewRegistrationEmailStatus,
              appointment_phone: previewAppointmentPhone,
              suggested_doctor_name: "",
              suggested_doctor_specialty: "Cornea and refractive surgery consultant",
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
            location_name: previewHospitalName,
            hard_constraint: true,
            confidence_level: "medium",
            details: {
              registration_email: previewRegistrationEmail,
              registration_email_status: previewRegistrationEmailStatus,
              appointment_phone: previewAppointmentPhone,
              suggested_doctor_name: "",
              suggested_doctor_specialty: "Cornea and refractive surgery consultant",
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
            location_name: previewHospitalName,
            confidence_level: "medium",
            details: {
              registration_email: previewRegistrationEmail,
              registration_email_status: previewRegistrationEmailStatus,
              appointment_phone: previewAppointmentPhone,
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

const PREVIEW_TEXT = {
  "zh-Hans": {
    "Preview International Plan": "国际患者预览方案",
    "Preview showing the international hospital workflow, doctor assignment, and insurance document steps.":
      "预览国际医院流程、医生分配和保险文件步骤。",
    "Preview policy review. Confirm pre-authorization, direct billing, and reimbursement documents before booking.":
      "预览保单审核。预订前请确认预授权、直付和报销文件要求。",
    "Limited international direct billing may be available only after insurer pre-authorization.":
      "仅在保险公司预授权后，才可能提供有限的国际直付。",
    "itemized invoice": "明细发票",
    "diagnosis certificate": "诊断证明",
    "doctor report": "医生报告",
    "payment receipt": "付款收据",
    "elective care without approval": "未经批准的择期医疗",
    "pre-existing condition exclusions": "既往症除外责任",
    "Current prescription: -4.50 both eyes, mild astigmatism; contact lens usage: soft lenses":
      "当前度数：双眼 -4.50，轻度散光；隐形眼镜使用：软性隐形眼镜",
    "Cornea and refractive surgery consultant": "角膜与屈光手术顾问医生",
    "Arrival and Pre-registration": "抵达与预登记",
    "Registration and Diagnostics": "挂号与检查",
    "Procedure and Recovery": "治疗与恢复",
    "Follow-up and Return Readiness": "复查与返程准备",
    "Arrival flight SQ850": "抵达航班 SQ850",
    "Hotel check-in": "酒店入住",
    "International desk pre-registration email check": "国际部预登记邮箱确认",
    "International desk registration and outpatient file setup": "国际部挂号与门诊档案建立",
    "Diagnostics and refractive-surgery suitability tests": "屈光手术适配性检查",
    "Suggested doctor consultation and eligibility confirmation": "建议医生会诊与适应症确认",
    "Final consent, deposit, and treatment-room preparation": "最终同意书、押金与治疗室准备",
    "SMILE Pro procedure window": "SMILE Pro 手术时段",
    "Medication, discharge briefing, and claim documents": "用药、离院说明与理赔文件",
    "Follow-up review with assigned doctor or international clinic": "指定医生或国际门诊复查",
    "Confirm return fitness, invoices, and insurance documents": "确认返程适宜性、发票和保险文件",
    "Request the International Patient Service team to assign or confirm a senior refractive-surgery consultant before deposit payment.":
      "请国际患者服务团队在支付押金前分配或确认资深屈光手术医生。",
    "Request the International Patient Service team to assign or confirm a senior refractive-surgery consultant before deposit payment.":
      "请国际患者服务团队在支付押金前分配或确认资深屈光手术医生。",
    "Email the international desk with passport name, preferred date, SMILE Pro interest, current prescription, and insurance holder.":
      "向国际部发送护照姓名、期望日期、SMILE Pro 意向、当前度数和保险公司。",
    "Attach prior eye reports only after confirming the official email channel.":
      "仅在确认官方邮箱渠道后再附上既往眼科报告。",
    "Ask for appointment confirmation, deposit requirement, interpreter support, and doctor assignment.":
      "询问预约确认、押金要求、翻译支持和医生分配。",
    "Show passport, appointment confirmation, insurance card or pre-authorization letter, and payment method.":
      "出示护照、预约确认、保险卡或预授权信以及支付方式。",
    "Create outpatient profile, confirm invoice name for claims, and sign privacy/consent forms.":
      "建立门诊档案，确认理赔发票抬头，并签署隐私/知情同意文件。",
    "Complete vision testing, corneal scan, eye-pressure check, tear-film assessment, and dilation if required.":
      "完成视力测试、角膜扫描、眼压检查、泪膜评估，并按需散瞳。",
    "Confirm soft contact lens pause period and whether test results allow same-trip procedure.":
      "确认软性隐形眼镜停戴期，以及检查结果是否允许同次行程手术。",
    "Review test results, eligibility, treatment alternatives, procedure risks, and final price.":
      "复核检查结果、适应症、替代方案、手术风险和最终价格。",
    "Confirm whether insurance requires guarantee-of-payment or reimbursement-only handling.":
      "确认保险是否需要付款保证书，或仅支持报销处理。",
    "Reconfirm doctor, eye marking, consent forms, final price, and payment or pre-authorization status.":
      "再次确认医生、眼部标记、同意书、最终价格，以及支付或预授权状态。",
    "Ask for post-procedure medicine list and emergency contact route before entering treatment.":
      "进入治疗前索取术后用药清单和紧急联系路径。",
    "Complete procedure only after same-day surgeon confirmation and eligibility check.":
      "仅在当天医生确认和适应症检查通过后进行手术。",
    "Rest in clinic observation area until cleared by the medical team.":
      "在诊所观察区休息，直到医疗团队确认可以离开。",
    "Collect eyedrops, written aftercare instructions, diagnosis certificate, itemized invoice, doctor report, and receipts.":
      "领取眼药水、书面护理说明、诊断证明、明细发票、医生报告和收据。",
    "Confirm next-day follow-up time and emergency contact instructions.":
      "确认次日复查时间和紧急联系说明。",
    "Check healing, vision status, medication use, screen-time limits, and flight fitness.":
      "检查恢复情况、视力状态、用药、屏幕使用限制和飞行适宜性。",
    "Confirm remote follow-up route after returning home.": "确认回国后的远程复查路径。",
    "Verify all claim documents are stamped or digitally valid.": "核对所有理赔文件是否盖章或具备数字效力。",
    "Confirm whether translated reports are required by the insurer.": "确认保险公司是否要求报告翻译件。",
    "Official registration email and final doctor name must be confirmed by the hospital.":
      "官方挂号邮箱和最终医生姓名必须由医院确认。",
    "Procedure eligibility depends on in-person diagnostics.": "手术适应症取决于现场检查结果。",
    "Insurance pre-authorization may be required before deposit payment.": "支付押金前可能需要保险预授权。",
    "Contact AIA with the hospital name and procedure estimate to confirm coverage.":
      "联系 AIA，提供医院名称和项目估算以确认保障范围。",
    "Request written pre-authorization before paying a hospital deposit.":
      "支付医院押金前索取书面预授权。",
    "Keep itemized invoices, diagnosis certificate, doctor report, prescriptions, and receipts.":
      "保留明细发票、诊断证明、医生报告、处方和收据。",
  },
  id: {
    "Preview International Plan": "Pratinjau Rencana Internasional",
    "Preview showing the international hospital workflow, doctor assignment, and insurance document steps.":
      "Pratinjau alur rumah sakit internasional, penugasan dokter, dan langkah dokumen asuransi.",
    "Preview policy review. Confirm pre-authorization, direct billing, and reimbursement documents before booking.":
      "Pratinjau tinjauan polis. Konfirmasi pra-otorisasi, direct billing, dan dokumen reimburse sebelum memesan.",
    "Limited international direct billing may be available only after insurer pre-authorization.":
      "Direct billing internasional terbatas mungkin tersedia hanya setelah pra-otorisasi asuransi.",
    "itemized invoice": "invoice terperinci",
    "diagnosis certificate": "sertifikat diagnosis",
    "doctor report": "laporan dokter",
    "payment receipt": "kuitansi pembayaran",
    "elective care without approval": "perawatan elektif tanpa persetujuan",
    "pre-existing condition exclusions": "pengecualian kondisi pra-eksisting",
    "Current prescription: -4.50 both eyes, mild astigmatism; contact lens usage: soft lenses":
      "Resep saat ini: -4.50 kedua mata, astigmatisme ringan; penggunaan lensa kontak: lensa lunak",
    "Cornea and refractive surgery consultant": "Konsultan kornea dan bedah refraktif",
    "Arrival and Pre-registration": "Kedatangan dan Pra-registrasi",
    "Registration and Diagnostics": "Registrasi dan Diagnostik",
    "Procedure and Recovery": "Prosedur dan Pemulihan",
    "Follow-up and Return Readiness": "Kontrol Lanjutan dan Kesiapan Pulang",
    "Arrival flight SQ850": "Penerbangan kedatangan SQ850",
    "Hotel check-in": "Check-in hotel",
    "International desk pre-registration email check": "Cek email pra-registrasi meja internasional",
    "International desk registration and outpatient file setup": "Registrasi meja internasional dan pembuatan berkas rawat jalan",
    "Diagnostics and refractive-surgery suitability tests": "Diagnostik dan tes kelayakan bedah refraktif",
    "Suggested doctor consultation and eligibility confirmation": "Konsultasi dokter yang disarankan dan konfirmasi kelayakan",
    "Final consent, deposit, and treatment-room preparation": "Persetujuan final, deposit, dan persiapan ruang tindakan",
    "SMILE Pro procedure window": "Jadwal prosedur SMILE Pro",
    "Medication, discharge briefing, and claim documents": "Obat, pengarahan pulang, dan dokumen klaim",
    "Follow-up review with assigned doctor or international clinic": "Kontrol dengan dokter yang ditugaskan atau klinik internasional",
    "Confirm return fitness, invoices, and insurance documents": "Konfirmasi kelayakan pulang, invoice, dan dokumen asuransi",
    "Request the International Patient Service team to assign or confirm a senior refractive-surgery consultant before deposit payment.":
      "Minta tim layanan pasien internasional menugaskan atau mengonfirmasi konsultan bedah refraktif senior sebelum pembayaran deposit.",
    "Email the international desk with passport name, preferred date, SMILE Pro interest, current prescription, and insurance holder.":
      "Email meja internasional dengan nama paspor, tanggal pilihan, minat SMILE Pro, resep saat ini, dan penyedia asuransi.",
    "Attach prior eye reports only after confirming the official email channel.":
      "Lampirkan laporan mata sebelumnya hanya setelah kanal email resmi dikonfirmasi.",
    "Ask for appointment confirmation, deposit requirement, interpreter support, and doctor assignment.":
      "Minta konfirmasi janji temu, persyaratan deposit, dukungan penerjemah, dan penugasan dokter.",
    "Show passport, appointment confirmation, insurance card or pre-authorization letter, and payment method.":
      "Tunjukkan paspor, konfirmasi janji temu, kartu asuransi atau surat pra-otorisasi, dan metode pembayaran.",
    "Create outpatient profile, confirm invoice name for claims, and sign privacy/consent forms.":
      "Buat profil rawat jalan, konfirmasi nama invoice untuk klaim, dan tanda tangani formulir privasi/persetujuan.",
    "Complete vision testing, corneal scan, eye-pressure check, tear-film assessment, and dilation if required.":
      "Selesaikan tes penglihatan, pemindaian kornea, cek tekanan mata, penilaian tear film, dan dilatasi bila diperlukan.",
    "Confirm soft contact lens pause period and whether test results allow same-trip procedure.":
      "Konfirmasi masa jeda lensa kontak lunak dan apakah hasil tes memungkinkan prosedur dalam perjalanan yang sama.",
    "Review test results, eligibility, treatment alternatives, procedure risks, and final price.":
      "Tinjau hasil tes, kelayakan, alternatif perawatan, risiko prosedur, dan harga final.",
    "Confirm whether insurance requires guarantee-of-payment or reimbursement-only handling.":
      "Konfirmasi apakah asuransi memerlukan guarantee-of-payment atau hanya reimburse.",
    "Reconfirm doctor, eye marking, consent forms, final price, and payment or pre-authorization status.":
      "Konfirmasi ulang dokter, penandaan mata, formulir persetujuan, harga final, serta status pembayaran atau pra-otorisasi.",
    "Ask for post-procedure medicine list and emergency contact route before entering treatment.":
      "Minta daftar obat pasca-prosedur dan jalur kontak darurat sebelum tindakan.",
    "Complete procedure only after same-day surgeon confirmation and eligibility check.":
      "Lakukan prosedur hanya setelah konfirmasi dokter bedah dan cek kelayakan pada hari yang sama.",
    "Rest in clinic observation area until cleared by the medical team.":
      "Beristirahat di area observasi klinik sampai diizinkan oleh tim medis.",
    "Collect eyedrops, written aftercare instructions, diagnosis certificate, itemized invoice, doctor report, and receipts.":
      "Ambil obat tetes mata, instruksi perawatan tertulis, sertifikat diagnosis, invoice terperinci, laporan dokter, dan kuitansi.",
    "Confirm next-day follow-up time and emergency contact instructions.":
      "Konfirmasi jadwal kontrol besok dan instruksi kontak darurat.",
    "Check healing, vision status, medication use, screen-time limits, and flight fitness.":
      "Periksa pemulihan, status penglihatan, penggunaan obat, batas waktu layar, dan kelayakan terbang.",
    "Confirm remote follow-up route after returning home.": "Konfirmasi jalur kontrol jarak jauh setelah pulang.",
    "Verify all claim documents are stamped or digitally valid.": "Pastikan semua dokumen klaim distempel atau valid secara digital.",
    "Confirm whether translated reports are required by the insurer.": "Konfirmasi apakah laporan terjemahan diperlukan oleh asuransi.",
    "Official registration email and final doctor name must be confirmed by the hospital.":
      "Email registrasi resmi dan nama dokter final harus dikonfirmasi oleh rumah sakit.",
    "Procedure eligibility depends on in-person diagnostics.": "Kelayakan prosedur bergantung pada diagnostik langsung.",
    "Insurance pre-authorization may be required before deposit payment.": "Pra-otorisasi asuransi mungkin diperlukan sebelum pembayaran deposit.",
    "Contact AIA with the hospital name and procedure estimate to confirm coverage.":
      "Hubungi AIA dengan nama rumah sakit dan estimasi prosedur untuk mengonfirmasi cakupan.",
    "Request written pre-authorization before paying a hospital deposit.":
      "Minta pra-otorisasi tertulis sebelum membayar deposit rumah sakit.",
    "Keep itemized invoices, diagnosis certificate, doctor report, prescriptions, and receipts.":
      "Simpan invoice terperinci, sertifikat diagnosis, laporan dokter, resep, dan kuitansi.",
  },
};

const LOCAL_PLANNER_TEXT = {
  "zh-Hans": {
    "Best Overall": "最佳综合",
    "Lowest Total Cost": "最低总费用",
    "Shortest Trip": "最短行程",
    "Strongest Medical Resources": "医疗资源最强",
    "Final treatment eligibility depends on in-person clinician assessment.": "最终治疗适应症取决于现场医生评估。",
    "Flight and hotel prices are estimates until live booking confirmation.": "航班和酒店价格在实时预订确认前均为估算。",
    "Visa or entry eligibility requires official confirmation.": "签证或入境资格需要官方确认。",
    "Insurance coverage and hospital billing policy require insurer confirmation before booking.":
      "保险保障范围和医院账单政策需要在预订前由保险公司确认。",
    "Some medical suitability details still need user confirmation.": "部分医疗适配性细节仍需用户确认。",
    "Arrival and Check-in": "抵达与入住",
    "Pre-treatment Evaluation": "治疗前评估",
    "Core Medical Appointment": "核心医疗预约",
    "Follow-up Review": "复查",
    "Return Travel": "返程",
    "Recovery and Light City Time": "恢复与轻量城市活动",
    "Arrival flight": "抵达航班",
    "Airport transfer to hotel": "机场前往酒店",
    "Hotel check-in": "酒店入住",
    "International desk pre-registration email check": "国际部预登记邮箱确认",
    "International desk registration and outpatient file setup": "国际部挂号与门诊档案建立",
    "Nurse intake, consent forms, and payment/pre-auth check": "护士问诊、同意书与支付/预授权确认",
    "Diagnostics and program-specific tests": "项目相关检查与测试",
    "Suggested doctor consultation and eligibility confirmation": "建议医生会诊与适应症确认",
    "Final consent, deposit, and treatment-room preparation": "最终同意书、押金与治疗室准备",
    "Procedure or core medical appointment": "治疗或核心医疗预约",
    "Medication, discharge briefing, and claim documents": "用药、离院说明与理赔文件",
    "Rest window near hospital": "医院附近休息时段",
    "Follow-up review with assigned doctor or international clinic": "指定医生或国际门诊复查",
    "Confirm return fitness, invoices, and insurance documents": "确认返程适宜性、发票和保险文件",
    "Hotel check-out": "酒店退房",
    "Transfer to airport": "前往机场",
    "Return flight": "返程航班",
    "Light recovery-friendly sightseeing": "轻量恢复友好观光",
    "Flexible city activity block": "灵活城市活动时段",
    "Recovery-friendly meals": "恢复友好餐食",
    "Confirm visa or visa-free entry status": "确认签证或免签入境状态",
    "Install and configure Alipay international version": "安装并配置支付宝国际版",
    "Confirm hospital appointment and required documents": "确认医院预约和所需文件",
    "Confirm insurance coverage and hospital claim requirements": "确认保险保障和医院理赔要求",
    "Verify sources and live prices before booking": "预订前核验来源和实时价格",
    "Confirm appointment date and department.": "确认预约日期和科室。",
    "Ask whether translator or international desk support is available.": "询问是否提供翻译或国际部支持。",
    "Prepare prior test reports and medication list if relevant.": "如适用，准备既往检查报告和用药清单。",
    "Review hospital source, international department, appointment contact, and insurance handling.":
      "核验医院来源、国际部、预约联系方式和保险处理方式。",
    "Re-check flight fare for exact route, date, cabin, baggage, and refund rules.":
      "重新核对确切航线、日期、舱位、行李和退改规则的机票价格。",
    "Re-check hotel nightly rate, subtotal, taxes, cancellation policy, and foreign-guest eligibility.":
      "重新核对酒店每晚价格、小计、税费、取消政策和外宾入住资格。",
    "Reconcile total estimate against itemized medical, travel, hotel, insurance, and local costs.":
      "根据医疗、交通、酒店、保险和本地费用明细复核总估算。",
    "This plan is for travel and budgeting support only and is not medical diagnosis.":
      "本方案仅用于出行和预算支持，不构成医学诊断。",
    "Procedure eligibility, final price, and appointment availability must be confirmed by the hospital or licensed clinician.":
      "项目适应症、最终价格和预约可用性必须由医院或持证医生确认。",
    "Visa and entry policies can change; verify official sources before booking non-refundable travel.":
      "签证和入境政策可能变化；预订不可退款行程前请核验官方来源。",
    "Insurance coverage, direct billing, and reimbursement eligibility must be confirmed by the insurer and hospital.":
      "保险保障、直付和报销资格必须由保险公司和医院确认。",
    "Flight and hotel values are planning estimates, not live booking inventory.":
      "航班和酒店数值是规划估算，不是实时预订库存。",
    "Hotel choices are filtered for foreign-guest eligibility in the local estimate model.":
      "本地估算模型已按外宾入住资格筛选酒店。",
    "Medical timelines preserve pre-treatment, procedure, and follow-up hard constraints.":
      "医疗时间线保留治疗前、治疗和复查的硬性约束。",
    "Insurance policy guidance is estimated from hospital-level rules and requires insurer confirmation.":
      "保险政策建议基于医院层面规则估算，仍需保险公司确认。",
    "Audit checks identify planning-only values that require official or live-source verification before booking.":
      "审计检查会标出预订前需要官方或实时来源核验的规划估算值。",
    "Verify selected hospital international department and official appointment contact.":
      "核验所选医院国际部和官方预约联系方式。",
    "Refresh flight fare from a live provider for the exact travel dates and traveler count.":
      "按确切出行日期和人数从实时供应商刷新机票价格。",
    "Refresh hotel nightly rate, taxes, cancellation terms, and foreign-guest eligibility.":
      "刷新酒店每晚价格、税费、取消条款和外宾入住资格。",
    "Confirm medical package scope, final price, eligibility, and insurance documents with the hospital.":
      "与医院确认医疗套餐范围、最终价格、适应症和保险文件。",
    "international service": "国际服务",
    "ophthalmology": "眼科",
    "premium checkup": "高端体检",
    "hematology referral": "血液科转诊",
    "lower cost": "较低费用",
    "flight access": "航班便利",
    "specialist depth": "专科深度",
    "VIP clinic": "VIP 门诊",
  },
  id: {
    "Best Overall": "Terbaik Secara Keseluruhan",
    "Lowest Total Cost": "Total Biaya Terendah",
    "Shortest Trip": "Perjalanan Tersingkat",
    "Strongest Medical Resources": "Sumber Daya Medis Terkuat",
    "Final treatment eligibility depends on in-person clinician assessment.": "Kelayakan perawatan final bergantung pada evaluasi dokter secara langsung.",
    "Flight and hotel prices are estimates until live booking confirmation.": "Harga penerbangan dan hotel masih estimasi sampai konfirmasi pemesanan langsung.",
    "Visa or entry eligibility requires official confirmation.": "Kelayakan visa atau masuk negara memerlukan konfirmasi resmi.",
    "Insurance coverage and hospital billing policy require insurer confirmation before booking.":
      "Cakupan asuransi dan kebijakan penagihan rumah sakit perlu dikonfirmasi oleh asuransi sebelum pemesanan.",
    "Some medical suitability details still need user confirmation.": "Beberapa detail kesesuaian medis masih perlu dikonfirmasi pengguna.",
    "Arrival and Check-in": "Kedatangan dan Check-in",
    "Pre-treatment Evaluation": "Evaluasi Pra-perawatan",
    "Core Medical Appointment": "Janji Medis Utama",
    "Follow-up Review": "Kontrol Lanjutan",
    "Return Travel": "Perjalanan Pulang",
    "Recovery and Light City Time": "Pemulihan dan Aktivitas Kota Ringan",
    "Arrival flight": "Penerbangan kedatangan",
    "Airport transfer to hotel": "Transfer bandara ke hotel",
    "Hotel check-in": "Check-in hotel",
    "International desk pre-registration email check": "Cek email pra-registrasi meja internasional",
    "International desk registration and outpatient file setup": "Registrasi meja internasional dan pembuatan berkas rawat jalan",
    "Nurse intake, consent forms, and payment/pre-auth check": "Intake perawat, formulir persetujuan, dan cek pembayaran/pra-otorisasi",
    "Diagnostics and program-specific tests": "Diagnostik dan tes khusus program",
    "Suggested doctor consultation and eligibility confirmation": "Konsultasi dokter yang disarankan dan konfirmasi kelayakan",
    "Final consent, deposit, and treatment-room preparation": "Persetujuan final, deposit, dan persiapan ruang tindakan",
    "Procedure or core medical appointment": "Prosedur atau janji medis utama",
    "Medication, discharge briefing, and claim documents": "Obat, arahan pulang, dan dokumen klaim",
    "Rest window near hospital": "Waktu istirahat dekat rumah sakit",
    "Follow-up review with assigned doctor or international clinic": "Kontrol dengan dokter yang ditugaskan atau klinik internasional",
    "Confirm return fitness, invoices, and insurance documents": "Konfirmasi kelayakan pulang, invoice, dan dokumen asuransi",
    "Hotel check-out": "Check-out hotel",
    "Transfer to airport": "Transfer ke bandara",
    "Return flight": "Penerbangan pulang",
    "Light recovery-friendly sightseeing": "Wisata ringan ramah pemulihan",
    "Flexible city activity block": "Blok aktivitas kota fleksibel",
    "Recovery-friendly meals": "Makanan ramah pemulihan",
    "Confirm visa or visa-free entry status": "Konfirmasi status visa atau bebas visa",
    "Install and configure Alipay international version": "Instal dan konfigurasi Alipay versi internasional",
    "Confirm hospital appointment and required documents": "Konfirmasi janji rumah sakit dan dokumen yang diperlukan",
    "Confirm insurance coverage and hospital claim requirements": "Konfirmasi cakupan asuransi dan persyaratan klaim rumah sakit",
    "Verify sources and live prices before booking": "Verifikasi sumber dan harga langsung sebelum memesan",
    "Confirm appointment date and department.": "Konfirmasi tanggal janji dan departemen.",
    "Ask whether translator or international desk support is available.": "Tanyakan apakah penerjemah atau dukungan meja internasional tersedia.",
    "Prepare prior test reports and medication list if relevant.": "Siapkan laporan tes sebelumnya dan daftar obat bila relevan.",
    "Review hospital source, international department, appointment contact, and insurance handling.":
      "Tinjau sumber rumah sakit, departemen internasional, kontak janji temu, dan penanganan asuransi.",
    "Re-check flight fare for exact route, date, cabin, baggage, and refund rules.":
      "Cek ulang tarif penerbangan untuk rute, tanggal, kabin, bagasi, dan aturan refund yang tepat.",
    "Re-check hotel nightly rate, subtotal, taxes, cancellation policy, and foreign-guest eligibility.":
      "Cek ulang tarif hotel per malam, subtotal, pajak, kebijakan pembatalan, dan kelayakan tamu asing.",
    "Reconcile total estimate against itemized medical, travel, hotel, insurance, and local costs.":
      "Cocokkan estimasi total dengan rincian biaya medis, perjalanan, hotel, asuransi, dan lokal.",
    "This plan is for travel and budgeting support only and is not medical diagnosis.":
      "Rencana ini hanya untuk dukungan perjalanan dan anggaran, bukan diagnosis medis.",
    "Procedure eligibility, final price, and appointment availability must be confirmed by the hospital or licensed clinician.":
      "Kelayakan prosedur, harga final, dan ketersediaan janji harus dikonfirmasi oleh rumah sakit atau dokter berlisensi.",
    "Visa and entry policies can change; verify official sources before booking non-refundable travel.":
      "Kebijakan visa dan masuk negara dapat berubah; verifikasi sumber resmi sebelum memesan perjalanan non-refundable.",
    "Insurance coverage, direct billing, and reimbursement eligibility must be confirmed by the insurer and hospital.":
      "Cakupan asuransi, direct billing, dan kelayakan reimburse harus dikonfirmasi oleh asuransi dan rumah sakit.",
    "Flight and hotel values are planning estimates, not live booking inventory.":
      "Nilai penerbangan dan hotel adalah estimasi perencanaan, bukan inventaris pemesanan langsung.",
    "Hotel choices are filtered for foreign-guest eligibility in the local estimate model.":
      "Pilihan hotel difilter untuk kelayakan tamu asing dalam model estimasi lokal.",
    "Medical timelines preserve pre-treatment, procedure, and follow-up hard constraints.":
      "Jadwal medis mempertahankan batasan wajib pra-perawatan, prosedur, dan kontrol.",
    "Insurance policy guidance is estimated from hospital-level rules and requires insurer confirmation.":
      "Panduan polis asuransi diestimasi dari aturan tingkat rumah sakit dan perlu konfirmasi asuransi.",
    "Audit checks identify planning-only values that require official or live-source verification before booking.":
      "Audit menandai nilai perencanaan yang perlu verifikasi resmi atau sumber langsung sebelum pemesanan.",
    "Verify selected hospital international department and official appointment contact.":
      "Verifikasi departemen internasional rumah sakit terpilih dan kontak janji resmi.",
    "Refresh flight fare from a live provider for the exact travel dates and traveler count.":
      "Perbarui tarif penerbangan dari penyedia langsung untuk tanggal dan jumlah pelancong yang tepat.",
    "Refresh hotel nightly rate, taxes, cancellation terms, and foreign-guest eligibility.":
      "Perbarui tarif hotel per malam, pajak, ketentuan pembatalan, dan kelayakan tamu asing.",
    "Confirm medical package scope, final price, eligibility, and insurance documents with the hospital.":
      "Konfirmasi cakupan paket medis, harga final, kelayakan, dan dokumen asuransi dengan rumah sakit.",
    "international service": "layanan internasional",
    "ophthalmology": "oftalmologi",
    "premium checkup": "pemeriksaan premium",
    "hematology referral": "rujukan hematologi",
    "lower cost": "biaya lebih rendah",
    "flight access": "akses penerbangan",
    "specialist depth": "kedalaman spesialis",
    "VIP clinic": "klinik VIP",
  },
};

function isPreviewOption(option) {
  return Boolean(option?.option_id?.startsWith("preview_") || option?.metadata?.data_status === "sample");
}

function isLocalPlannerOption(option) {
  return Boolean(option?.option_id?.startsWith("opt_") && option?.metadata?.source === "agent_estimate");
}

function localizePreviewString(value) {
  if (typeof value !== "string") return value;
  const language = normalizeLanguage(state.language);
  return PREVIEW_TEXT[language]?.[value] || localizeLocalPlannerString(value, language);
}

function localizePreviewValue(value) {
  if (Array.isArray(value)) return value.map(localizePreviewValue);
  if (isObjectValue(value)) {
    return Object.fromEntries(Object.entries(value).map(([key, nestedValue]) => [key, localizePreviewValue(nestedValue)]));
  }
  return localizePreviewString(value);
}

function optionForDisplay(option) {
  return isPreviewOption(option) || isLocalPlannerOption(option) ? localizePreviewValue(option) : option;
}

function localizeLocalPlannerString(value, language = normalizeLanguage(state.language)) {
  const dictionary = LOCAL_PLANNER_TEXT[language] || {};
  if (dictionary[value]) return dictionary[value];
  const reasonMatch = value.match(/^(.+) (balances international medical service, flight access, and predictable planning|is positioned as the lower-cost candidate while keeping international patient support|supports a compact schedule with manageable transfers and hospital access|is selected for stronger specialist depth and hospital reputation)\. Key strengths: (.+)\.$/);
  if (reasonMatch) {
    const [, city, reason, strengths] = reasonMatch;
    const translatedStrengths = strengths
      .split(", ")
      .map((strength) => dictionary[strength] || strength)
      .join(language === "zh-Hans" ? "、" : ", ");
    const translatedReasons = {
      "zh-Hans": {
        "balances international medical service, flight access, and predictable planning":
          `${city} 兼顾国际医疗服务、航班便利和可预期的规划流程`,
        "is positioned as the lower-cost candidate while keeping international patient support":
          `${city} 是较低费用候选城市，同时保留国际患者支持`,
        "supports a compact schedule with manageable transfers and hospital access":
          `${city} 支持紧凑行程，转运和就医交通较易安排`,
        "is selected for stronger specialist depth and hospital reputation":
          `${city} 因更强的专科深度和医院声誉而入选`,
      },
      id: {
        "balances international medical service, flight access, and predictable planning":
          `${city} menyeimbangkan layanan medis internasional, akses penerbangan, dan perencanaan yang lebih terprediksi`,
        "is positioned as the lower-cost candidate while keeping international patient support":
          `${city} diposisikan sebagai kandidat biaya lebih rendah sambil tetap memiliki dukungan pasien internasional`,
        "supports a compact schedule with manageable transfers and hospital access":
          `${city} mendukung jadwal ringkas dengan transfer dan akses rumah sakit yang mudah dikelola`,
        "is selected for stronger specialist depth and hospital reputation":
          `${city} dipilih karena kedalaman spesialis dan reputasi rumah sakit yang lebih kuat`,
      },
    };
    if (language === "zh-Hans") return `${translatedReasons[language][reason]}。主要优势：${translatedStrengths}。`;
    if (language === "id") return `${translatedReasons[language][reason]}. Kekuatan utama: ${translatedStrengths}.`;
  }
  return value.replace(
    /Resolve (\d+) blocking audit items and review (\d+) warnings before any non-refundable booking\./,
    (_match, blocking, warnings) => {
      if (language === "zh-Hans") return `在进行任何不可退款预订前，解决 ${blocking} 个阻断性审计项并查看 ${warnings} 条警告。`;
      if (language === "id") return `Selesaikan ${blocking} item audit penghambat dan tinjau ${warnings} peringatan sebelum pemesanan non-refundable.`;
      return _match;
    }
  );
}

const COST_CATEGORY_LABELS = {
  en: {
    medical: "medical",
    flight: "flight",
    hotel: "hotel",
    local_transport: "local transport",
    meals: "meals",
    visa_and_payment_setup: "visa and payment setup",
    travel_insurance: "travel insurance",
  },
  "zh-Hans": {
    medical: "医疗",
    flight: "航班",
    hotel: "酒店",
    local_transport: "本地交通",
    meals: "餐饮",
    visa_and_payment_setup: "签证与支付设置",
    travel_insurance: "旅行保险",
  },
  id: {
    medical: "medis",
    flight: "penerbangan",
    hotel: "hotel",
    local_transport: "transportasi lokal",
    meals: "makan",
    visa_and_payment_setup: "visa dan pengaturan pembayaran",
    travel_insurance: "asuransi perjalanan",
  },
};

function costCategoryLabel(label) {
  return COST_CATEGORY_LABELS[normalizeLanguage(state.language)]?.[label] || label.replaceAll("_", " ");
}

function insuranceStatusLabel(status) {
  if (!status) return t("plan.insurance.needsReview");
  if (status === "needs_insurer_confirmation") return t("plan.insurance.needsInsurerConfirmation");
  return humanizeKey(status);
}

const programDetailConfigsByLanguage = {
  en: {
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
  car_t_blood_cancer: {
    icon: "bloodtype",
    title: "CAR-T blood cancer details",
    subtitle: "Clarify diagnosis, treatment stage, and whether prior records are ready for review.",
    subtypeLabel: "Treatment focus",
    subtypeOptions: [
      ["car_t_consult", "CAR-T eligibility consult"],
      ["b_cell_lymphoma", "B-cell lymphoma CAR-T"],
      ["multiple_myeloma", "Multiple myeloma CAR-T"],
      ["leukemia", "Leukemia CAR-T"],
      ["not_sure", "Not sure yet"],
    ],
    fields: [
      {
        id: "diagnosis",
        label: "Diagnosis",
        icon: "clinical_notes",
        placeholder: "e.g. DLBCL, multiple myeloma, ALL",
      },
      {
        id: "treatmentStage",
        label: "Treatment stage",
        icon: "biotech",
        type: "select",
        options: [
          ["initial_consult", "Initial CAR-T consult"],
          ["post_chemo_relapse", "Relapse after chemotherapy"],
          ["bridging_therapy", "Bridging therapy needed"],
          ["records_ready", "Records ready for review"],
          ["not_sure", "Not sure"],
        ],
      },
    ],
    },
  },
  "zh-Hans": {
    eye_surgery: {
      icon: "visibility",
      title: "眼科手术详情",
      subtitle: "请说明可能的手术类型和眼部准备情况。",
      subtypeLabel: "手术类型",
      subtypeOptions: [
        ["smile_pro", "SMILE / SMILE Pro"],
        ["lasik", "LASIK"],
        ["icl", "ICL 晶体植入"],
        ["cataract", "白内障手术"],
        ["not_sure", "暂不确定"],
      ],
      fields: [
        {
          id: "currentPrescription",
          label: "当前度数",
          icon: "visibility",
          placeholder: "例如双眼 -4.50，散光",
        },
        {
          id: "contactLensUsage",
          label: "隐形眼镜使用情况",
          icon: "lens",
          type: "select",
          options: [
            ["none", "不戴隐形眼镜"],
            ["soft_lenses", "软性隐形眼镜"],
            ["hard_or_ortho_k", "硬镜 / 角膜塑形镜"],
            ["not_sure", "不确定"],
          ],
        },
      ],
    },
    dental_care: {
      icon: "dentistry",
      title: "牙科项目详情",
      subtitle: "请说明治疗范围、影像资料，以及是否可能需要多次就诊。",
      subtypeLabel: "牙科项目",
      subtypeOptions: [
        ["single_implant", "单颗种植"],
        ["multiple_implants", "多颗种植"],
        ["crown_bridge", "牙冠 / 牙桥"],
        ["root_canal", "根管治疗"],
        ["not_sure", "暂不确定"],
      ],
      fields: [
        {
          id: "teethCount",
          label: "涉及牙齿数量",
          icon: "tag",
          placeholder: "例如 1 颗种植，3 颗牙冠",
        },
        {
          id: "recentXray",
          label: "近期 X 光或 CBCT",
          icon: "image_search",
          type: "select",
          options: [
            ["yes", "有，可提供"],
            ["no", "没有"],
            ["not_sure", "不确定"],
          ],
        },
      ],
    },
    health_checkup: {
      icon: "monitor_heart",
      title: "体检详情",
      subtitle: "请说明筛查重点，便于规划合适的检查项目。",
      subtypeLabel: "体检套餐",
      subtypeOptions: [
        ["executive_screening", "高端综合体检"],
        ["cardio_screening", "心血管重点"],
        ["cancer_markers", "肿瘤标志物重点"],
        ["women_health", "女性健康"],
        ["not_sure", "暂不确定"],
      ],
      fields: [
        {
          id: "screeningFocus",
          label: "主要健康关注",
          icon: "clinical_notes",
          placeholder: "例如心脏、肿瘤标志物、全身体检",
        },
        {
          id: "knownConditions",
          label: "已知疾病",
          icon: "medical_information",
          placeholder: "例如高血压、糖尿病、无",
        },
      ],
    },
    car_t_blood_cancer: {
      icon: "bloodtype",
      title: "CAR-T 血液肿瘤详情",
      subtitle: "请说明诊断、治疗阶段，以及既往病历是否已准备好。",
      subtypeLabel: "治疗重点",
      subtypeOptions: [
        ["car_t_consult", "CAR-T 适应症咨询"],
        ["b_cell_lymphoma", "B 细胞淋巴瘤 CAR-T"],
        ["multiple_myeloma", "多发性骨髓瘤 CAR-T"],
        ["leukemia", "白血病 CAR-T"],
        ["not_sure", "暂不确定"],
      ],
      fields: [
        {
          id: "diagnosis",
          label: "诊断",
          icon: "clinical_notes",
          placeholder: "例如 DLBCL、多发性骨髓瘤、ALL",
        },
        {
          id: "treatmentStage",
          label: "治疗阶段",
          icon: "biotech",
          type: "select",
          options: [
            ["initial_consult", "初次 CAR-T 咨询"],
            ["post_chemo_relapse", "化疗后复发"],
            ["bridging_therapy", "需要桥接治疗"],
            ["records_ready", "病历已准备好审核"],
            ["not_sure", "不确定"],
          ],
        },
      ],
    },
  },
  id: {
    eye_surgery: {
      icon: "visibility",
      title: "Detail operasi mata",
      subtitle: "Jelaskan kemungkinan prosedur dan kesiapan mata Anda.",
      subtypeLabel: "Jenis prosedur",
      subtypeOptions: [
        ["smile_pro", "SMILE / SMILE Pro"],
        ["lasik", "LASIK"],
        ["icl", "Implan lensa ICL"],
        ["cataract", "Operasi katarak"],
        ["not_sure", "Belum yakin"],
      ],
      fields: [
        {
          id: "currentPrescription",
          label: "Resep kacamata saat ini",
          icon: "visibility",
          placeholder: "mis. -4.50 kedua mata, astigmatisme",
        },
        {
          id: "contactLensUsage",
          label: "Penggunaan lensa kontak",
          icon: "lens",
          type: "select",
          options: [
            ["none", "Tidak memakai lensa kontak"],
            ["soft_lenses", "Lensa lunak"],
            ["hard_or_ortho_k", "Lensa keras / Ortho-K"],
            ["not_sure", "Tidak yakin"],
          ],
        },
      ],
    },
    dental_care: {
      icon: "dentistry",
      title: "Detail perawatan gigi",
      subtitle: "Jelaskan cakupan, hasil pencitraan, dan apakah mungkin perlu beberapa kunjungan.",
      subtypeLabel: "Prosedur gigi",
      subtypeOptions: [
        ["single_implant", "Implan tunggal"],
        ["multiple_implants", "Beberapa implan"],
        ["crown_bridge", "Mahkota / bridge"],
        ["root_canal", "Perawatan saluran akar"],
        ["not_sure", "Belum yakin"],
      ],
      fields: [
        {
          id: "teethCount",
          label: "Jumlah gigi yang terlibat",
          icon: "tag",
          placeholder: "mis. 1 implan, 3 mahkota",
        },
        {
          id: "recentXray",
          label: "X-ray atau CBCT terbaru",
          icon: "image_search",
          type: "select",
          options: [
            ["yes", "Ya, tersedia"],
            ["no", "Tidak"],
            ["not_sure", "Tidak yakin"],
          ],
        },
      ],
    },
    health_checkup: {
      icon: "monitor_heart",
      title: "Detail pemeriksaan kesehatan",
      subtitle: "Jelaskan fokus pemeriksaan agar rencana dapat memilih tes yang tepat.",
      subtypeLabel: "Paket pemeriksaan",
      subtypeOptions: [
        ["executive_screening", "Pemeriksaan eksekutif"],
        ["cardio_screening", "Fokus jantung"],
        ["cancer_markers", "Fokus penanda kanker"],
        ["women_health", "Kesehatan wanita"],
        ["not_sure", "Belum yakin"],
      ],
      fields: [
        {
          id: "screeningFocus",
          label: "Kekhawatiran kesehatan utama",
          icon: "clinical_notes",
          placeholder: "mis. jantung, penanda kanker, seluruh tubuh",
        },
        {
          id: "knownConditions",
          label: "Kondisi yang diketahui",
          icon: "medical_information",
          placeholder: "mis. hipertensi, diabetes, tidak ada",
        },
      ],
    },
    car_t_blood_cancer: {
      icon: "bloodtype",
      title: "Detail kanker darah CAR-T",
      subtitle: "Jelaskan diagnosis, tahap pengobatan, dan apakah rekam medis siap ditinjau.",
      subtypeLabel: "Fokus pengobatan",
      subtypeOptions: [
        ["car_t_consult", "Konsultasi kelayakan CAR-T"],
        ["b_cell_lymphoma", "CAR-T limfoma sel B"],
        ["multiple_myeloma", "CAR-T multiple myeloma"],
        ["leukemia", "CAR-T leukemia"],
        ["not_sure", "Belum yakin"],
      ],
      fields: [
        {
          id: "diagnosis",
          label: "Diagnosis",
          icon: "clinical_notes",
          placeholder: "mis. DLBCL, multiple myeloma, ALL",
        },
        {
          id: "treatmentStage",
          label: "Tahap pengobatan",
          icon: "biotech",
          type: "select",
          options: [
            ["initial_consult", "Konsultasi awal CAR-T"],
            ["post_chemo_relapse", "Kambuh setelah kemoterapi"],
            ["bridging_therapy", "Perlu bridging therapy"],
            ["records_ready", "Rekam medis siap ditinjau"],
            ["not_sure", "Tidak yakin"],
          ],
        },
      ],
    },
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

function plannerErrorMessage(error) {
  if (!error) return "The planner failed to generate a report.";
  const message = error.message || error.detail || "The planner failed to generate a report.";
  const validationErrors = Array.isArray(error.validation_errors) ? error.validation_errors : [];
  if (!validationErrors.length) return message;
  const details = validationErrors
    .slice(0, 4)
    .map((item) => `${item.path || "report"}: ${item.message || item.type || "invalid value"}`)
    .join("; ");
  const suffix = validationErrors.length > 4 ? `; +${validationErrors.length - 4} more` : "";
  return `${message} ${details}${suffix}`;
}

function isMissingBackendReportError(error) {
  const message = String(error?.message || error || "");
  return message.includes("404") && message.includes("report_id not found");
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

function setAgentBackendAvailable(available) {
  const agentButton = document.querySelector('[data-planner-backend="adk"]');
  if (!agentButton) return;
  agentButton.disabled = !available;
  agentButton.title = available ? t("status.useAgentsTitle") : t("status.agentUnavailableTitle");
}

async function loadPlannerConfig() {
  try {
    const config = await api("/api/v1/planner/config");
    const adkAvailable = Boolean(config.adk_available);
    setAgentBackendAvailable(adkAvailable);
    if (!adkAvailable && state.plannerBackend === "adk") {
      setPlannerBackend("local");
      persistState();
      setStatus(t("status.agentUnavailable"), "info");
      return;
    }
    if (!state.generationAttempted && ["local", "adk"].includes(config.default_backend)) {
      setPlannerBackend(config.default_backend);
    }
  } catch (error) {
    console.warn("Planner config unavailable", error);
  }
}

function clearAgentProgressTimers() {
  agentProgressTimers.forEach((timer) => clearTimeout(timer));
  agentProgressTimers = [];
}

function resetAgentProgress(message = firstAgentWorkingMessage()) {
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
    statusMessage: message || agentStepText(agentProgressSteps[stepIndex], "working"),
  };
  renderAgentProgress();
}

function startAgentProgressSimulation(startIndex = 1) {
  clearAgentProgressTimers();
  let nextDelay = agentProgressDwellMs[agentProgressSteps[startIndex - 1]?.id] || 2400;
  agentProgressSteps.slice(startIndex).forEach((step, index) => {
    const timer = setTimeout(() => activateAgentStep(step.id), nextDelay);
    agentProgressTimers.push(timer);
    nextDelay += agentProgressDwellMs[step.id] || Math.max(1800, 2600 - index * 150);
  });
}

function finishAgentProgress(message = t("agent.ready")) {
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
  if (message) message.textContent = state.agentProgress.statusMessage || t("agent.waiting");
  if (subtitle) {
    subtitle.textContent = state.agentProgress.running
      ? t("agent.subtitle.running")
      : failedStepId
        ? t("agent.subtitle.failed")
        : t("agent.subtitle.complete");
  }

  container.innerHTML = agentProgressSteps
    .map((step) => {
      const isComplete = completed.has(step.id);
      const isActive = step.id === activeStepId && !failedStepId && !isComplete;
      const isError = step.id === failedStepId;
      const status = isError
        ? t("agent.status.error")
        : isComplete
          ? t("agent.status.complete")
          : isActive
            ? t("agent.status.working")
            : t("agent.status.queued");
      const body = isComplete ? agentStepText(step, "done") : agentStepText(step, "working");
      return `
        <article class="agent-stage-card ${isComplete ? "complete" : ""} ${isActive ? "active" : ""} ${isError ? "error" : ""}">
          <span class="material-symbols-outlined">${step.icon}</span>
          <div>
            <h2>${agentStepText(step, "title")}</h2>
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

function moneyAmount(value) {
  return Number(value?.amount || 0);
}

function savingsForDisplay(option) {
  if (!option) return null;
  const explicitSavings = option.estimated_net_savings;
  if (moneyAmount(explicitSavings) > 0) return explicitSavings;

  const home = moneyAmount(option.home_country_benchmark) > 0
    ? option.home_country_benchmark
    : singaporeBudgetForOption(option);
  const total = option.total_estimated_cost;
  const homeAmount = moneyAmount(home);
  const totalAmount = moneyAmount(total);
  if (homeAmount > 0 && totalAmount > 0) {
    return {
      amount: Math.max(homeAmount - totalAmount, 0),
      currency: home?.currency || total?.currency || "SGD",
      source: "client_derived_home_benchmark",
    };
  }

  return null;
}

function singaporeBudgetForOption(option) {
  const purpose = option?.medical_purpose || "health_checkup";
  const subtype = option?.procedure_subtype || "default";
  const purposeBudget = SINGAPORE_MEDICAL_BUDGET_SGD[purpose] || SINGAPORE_MEDICAL_BUDGET_SGD.health_checkup;
  return {
    amount: purposeBudget[subtype] || purposeBudget.default,
    currency: "SGD",
    source: "client_hard_written_singapore_budget",
  };
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

function parseStructuredString(value) {
  if (typeof value !== "string") return null;
  const text = value.trim();
  if (!/^[{[]/.test(text)) return null;
  try {
    return JSON.parse(text);
  } catch (_error) {
    try {
      return JSON.parse(
        text
          .replaceAll("None", "null")
          .replaceAll("True", "true")
          .replaceAll("False", "false")
          .replace(/'/g, '"')
      );
    } catch (_fallbackError) {
      return null;
    }
  }
}

function structuredValue(value) {
  const parsed = parseStructuredString(value);
  return parsed || value;
}

function isObjectValue(value) {
  return value && typeof value === "object" && !Array.isArray(value);
}

function humanizeKey(key) {
  return String(key || "")
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function compactStructuredValue(value) {
  const parsed = structuredValue(value);
  if (parsed === null || parsed === undefined || parsed === "") return "";
  if (Array.isArray(parsed)) {
    return parsed.map(compactStructuredValue).filter(Boolean).join("; ");
  }
  if (isObjectValue(parsed)) {
    return Object.entries(parsed)
      .filter(([, nestedValue]) => nestedValue !== null && nestedValue !== undefined && String(nestedValue).trim())
      .map(([key, nestedValue]) => `${humanizeKey(key)}: ${compactStructuredValue(nestedValue)}`)
      .join(" · ");
  }
  return String(parsed);
}

function isMoneyObject(value) {
  return isObjectValue(value) && value.amount !== undefined && value.currency;
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

function isoDateWithOffset(startValue, offset) {
  const fallback = document.querySelector("#dateRangeInput")?.value
    ? parseDateRange(document.querySelector("#dateRangeInput").value).start
    : "2026-08-12";
  const date = new Date(`${startValue || fallback}T00:00:00`);
  if (Number.isNaN(date.getTime())) return "";
  date.setDate(date.getDate() + offset);
  return date.toISOString().slice(0, 10);
}

function timelineTime(date, time) {
  return date ? `${date}T${time}:00+08:00` : "";
}

function clientFallbackTimeline(option) {
  if (!option) return [];
  const city = option.city || "Selected city";
  const hospital = option.target_hospital || "Selected hospital international clinic";
  const hotel = option.hotel || {};
  const flight = option.flight || {};
  const doctor = option.hospital_visit_protocol?.suggested_doctor || {};
  const contact = option.hospital_visit_protocol?.registration_contact || {};
  const serviceBilling = option.hospital_visit_protocol?.service_billing || {};
  const doctorName = doctor.name || option.suggested_doctor_name || "";
  const doctorSpecialty = doctor.specialty || option.suggested_doctor_specialty || "Assigned specialist to confirm";
  const registrationEmail = contact.email || option.registration_email || "";
  const medicalCost = option.cost_breakdown?.medical;
  const start = option.start_date;
  const details = (steps) => ({
    registration_email: registrationEmail,
    registration_email_status: contact.email_status || "needs_confirmation",
    appointment_phone: contact.appointment_phone || "",
    main_phone: contact.main_phone || "",
    wechat_or_portal_route: contact.wechat_or_portal_route || "",
    service_billing: serviceBilling,
    service_billing_status: serviceBilling.service_billing_status || "needs_confirmation",
    direct_billing_status: serviceBilling.direct_billing_status || "unknown",
    suggested_doctor_name: doctorName,
    suggested_doctor_specialty: doctorSpecialty,
    suggested_doctor_request: doctor.request_note || "Confirm the responsible care team, appointment route, billing desk, and claim-document process before payment.",
    hospital_steps: steps,
  });
  const item = (category, title, dayIndex, startTime, endTime, location, extra = {}) => {
    const date = isoDateWithOffset(start, dayIndex);
    return {
      item_id: `tli_client_${dayIndex + 1}_${title.toLowerCase().replaceAll(" ", "_")}`,
      category,
      title,
      start_time: timelineTime(date, startTime),
      end_time: timelineTime(date, endTime),
      location_name: location,
      confidence_level: "medium",
      ...extra,
    };
  };

  return [
    {
      day: 1,
      date: isoDateWithOffset(start, 0),
      title: `Arrival and ${city} setup`,
      items: [
        item("flight", "Arrival flight", 0, "08:00", "13:30", flight.arrival_airport || city, {
          estimated_cost: flight.estimated_cost,
        }),
        item("hotel", "Hotel check-in near international clinic", 0, "15:00", "16:00", hotel.name || city, {
          address: hotel.address,
          estimated_cost: hotel.nightly_rate || option.cost_breakdown?.hotel,
        }),
        item("medical", "International desk pre-registration email check", 0, "16:30", "17:00", hospital, {
          hard_constraint: true,
          details: details([
            "Confirm the official international desk email before sending documents.",
            "Send passport name, preferred appointment window, medical purpose, and current insurance holder.",
            "Ask for doctor assignment, deposit requirement, interpreter support, and claim-document process.",
          ]),
        }),
      ],
    },
    {
      day: 2,
      date: isoDateWithOffset(start, 1),
      title: "Registration and medical assessment",
      items: [
        item("medical", "International outpatient registration and file setup", 1, "08:30", "09:30", hospital, {
          hard_constraint: true,
          details: details([
            "Show passport, appointment confirmation, insurance card or guarantee letter, and payment method.",
            "Create outpatient profile and confirm invoice name for insurance reimbursement.",
            "Complete consent, privacy, interpreter, and deposit or pre-authorization checks.",
          ]),
        }),
        item("medical", "Program-specific diagnostics and nurse intake", 1, "09:30", "12:00", hospital, {
          hard_constraint: true,
          estimated_cost: medicalCost,
          details: details([
            "Complete vitals, medical history, medication review, and program-specific tests.",
            "Confirm whether results allow the planned procedure or checkup to continue on this trip.",
          ]),
        }),
        item("medical", "Suggested doctor consultation and treatment decision", 1, "14:00", "15:30", hospital, {
          hard_constraint: true,
          details: details([
            `Meet ${doctorName} or request confirmed assignment through the international clinic.`,
            "Review eligibility, alternatives, risks, final price, insurance handling, and timing.",
          ]),
        }),
      ],
    },
    {
      day: 3,
      date: isoDateWithOffset(start, 2),
      title: "Procedure, documents, and follow-up",
      items: [
        item("medical", "Procedure or treatment block", 2, "09:00", "12:00", hospital, {
          hard_constraint: true,
          estimated_cost: medicalCost,
          details: details([
            "Reconfirm consent, assigned doctor, final estimate, deposit, and pre-authorization status.",
            "Proceed only after same-day safety and eligibility confirmation.",
          ]),
        }),
        item("medical", "Discharge briefing and insurance claim document collection", 2, "14:00", "15:30", hospital, {
          hard_constraint: true,
          details: details([
            "Collect medical report, diagnosis certificate, itemized invoice, prescriptions, and receipts.",
            "Confirm emergency contact route, medication instructions, and remote follow-up channel.",
          ]),
        }),
      ],
    },
  ];
}

function clientReadinessFromOption(option) {
  const items = (option?.readiness_items || option?.readiness_summary || [])
    .map((item, index) => {
      if (typeof item === "string") {
        return {
          id: `readiness_${index + 1}`,
          title: item,
          priority: "medium",
          status: "pending",
          steps: [item],
          helpful_links: [],
        };
      }
      return {
        id: item.id || `readiness_${index + 1}`,
        title: item.title || item.label || `Readiness item ${index + 1}`,
        priority: item.priority || "medium",
        status: item.status || "pending",
        steps: Array.isArray(item.steps) ? item.steps : item.note ? [item.note] : [],
        helpful_links: item.helpful_links || [],
      };
    });
  const completed = items.filter((item) => item.status === "complete");
  const highRisk = items.filter((item) => item.priority === "high" && item.status !== "complete");
  return {
    option_id: option?.option_id || null,
    completion_percent: items.length ? Math.round((completed.length / items.length) * 100) : 0,
    completed_count: completed.length,
    total_count: items.length,
    high_risk_items: highRisk,
    sections: [{ title: "Pre-trip readiness", items }],
  };
}

function useClientPlanSnapshot(option) {
  if (!option) return;
  const optionDays = Array.isArray(option.timeline) ? option.timeline : [];
  const days = timelineItemCount(optionDays) ? optionDays : clientFallbackTimeline(option);
  state.timeline = {
    option_id: option.option_id,
    timeline_version_id: option.timeline_version_id || "client_snapshot",
    days,
  };
  state.costs = {
    option_id: option.option_id,
    currency: "SGD",
    total: option.total_estimated_cost,
    categories: option.cost_breakdown || {},
    benchmark: { net_savings: savingsForDisplay(option) },
  };
  state.readiness = clientReadinessFromOption(option);
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
      details.appointment_phone ||
      details.wechat_or_portal_route ||
      details.registration_desk ||
      details.service_billing_status ||
      meaningfulDoctorLine(details) ||
      details.hospital_steps?.length
  );
}

function hasAnyTimelineDetails(item) {
  const details = item?.details;
  if (!isObjectValue(details)) return false;
  return Object.values(details).some((value) => compactStructuredValue(value));
}

function isHospitalTimelineCandidate(item) {
  if (item.category !== "medical") return false;
  const title = normalizedText(timelineItemTitle(item));
  return [
    "hospital",
    "clinic",
    "appointment",
    "registration",
    "pre-registration",
    "outpatient",
    "diagnostic",
    "exam",
    "test",
    "consult",
    "doctor",
    "procedure",
    "treatment",
    "surgery",
    "discharge",
    "claim",
    "invoice",
    "follow-up",
    "review",
  ].some((keyword) => title.includes(keyword));
}

function normalizedText(value) {
  return compactStructuredValue(value).trim().toLowerCase();
}

function isGenericDoctorText(value) {
  const text = normalizedText(value);
  return (
    !text ||
    text === "relevant specialist for selected medical program" ||
    text === "assigned specialist to confirm" ||
    text === "responsible specialist" ||
    text.includes("selected medical program")
  );
}

function isGenericDoctorRequest(value) {
  const text = normalizedText(value);
  return (
    !text ||
    text.includes("assign or confirm the responsible specialist before final payment") ||
    text.includes("assign or confirm the responsible specialist")
  );
}

function meaningfulDoctorLine(details) {
  const parts = [details.suggested_doctor_name, details.suggested_doctor_specialty].filter(
    (value) => !isGenericDoctorText(value)
  );
  return parts.join(" · ");
}

function purposeSpecialistLabel(option) {
  const purpose = option?.medical_purpose || option?.profile?.medical_purpose;
  const subtype = (option?.procedure_subtype || "").replaceAll("_", " ");
  const labels = {
    eye_surgery: subtype && subtype !== "not sure"
      ? `Ophthalmology / refractive surgery team (${subtype})`
      : "Ophthalmology / refractive surgery team",
    dental_care: subtype && subtype !== "not sure"
      ? `Stomatology / dental implant team (${subtype})`
      : "Stomatology / dental implant team",
    health_checkup: subtype && subtype !== "not sure"
      ? `Health management screening team (${subtype})`
      : "Health management screening team",
    car_t_blood_cancer: subtype && subtype !== "not sure"
      ? `Hematology-oncology / cellular therapy team (${subtype})`
      : "Hematology-oncology / cellular therapy team",
  };
  return labels[purpose] || "International clinic care team";
}

function careTeamForTimelineItem(item, option, doctor) {
  const title = normalizedText(item.title);
  const specificDoctor = [doctor.name, doctor.specialty].filter((value) => !isGenericDoctorText(value)).join(" · ");
  if (specificDoctor && (title.includes("doctor") || title.includes("consult") || title.includes("procedure") || title.includes("follow-up"))) {
    return specificDoctor;
  }
  if (title.includes("pre-registration") || title.includes("email") || title.includes("appointment")) {
    return "International patient services / appointment desk";
  }
  if (title.includes("registration") || title.includes("file")) {
    return "Registration desk, interpreter support, and billing counter";
  }
  if (title.includes("diagnostic") || title.includes("exam") || title.includes("test") || title.includes("nurse")) {
    return `${purposeSpecialistLabel(option)} and nursing intake`;
  }
  if (title.includes("procedure") || title.includes("treatment") || title.includes("surgery")) {
    return purposeSpecialistLabel(option);
  }
  if (title.includes("discharge") || title.includes("claim") || title.includes("invoice") || title.includes("document")) {
    return "Nursing discharge desk, pharmacy, and billing documentation";
  }
  if (title.includes("follow-up") || title.includes("review")) {
    return "Follow-up clinic and responsible specialist";
  }
  return purposeSpecialistLabel(option);
}

function nextConfirmationForTimelineItem(item, option) {
  const title = normalizedText(item.title);
  const hospital = option?.target_hospital || "the hospital";
  if (title.includes("pre-registration") || title.includes("email") || title.includes("appointment")) {
    return "Confirm the official appointment route before sending passport details or medical records.";
  }
  if (title.includes("registration") || title.includes("file")) {
    return "Confirm passport, payment method, invoice name, interpreter support, and outpatient profile requirements.";
  }
  if (title.includes("diagnostic") || title.includes("exam") || title.includes("test") || title.includes("nurse")) {
    return "Confirm which prior records to bring and whether same-day results are available for treatment decisions.";
  }
  if (title.includes("doctor") || title.includes("consult") || title.includes("eligibility")) {
    return "Ask the international clinic to name the responsible specialist and confirm final eligibility before payment.";
  }
  if (title.includes("procedure") || title.includes("treatment") || title.includes("surgery")) {
    return "Proceed only after final consent, responsible specialist, price, deposit, and pre-authorization are confirmed.";
  }
  if (title.includes("discharge") || title.includes("claim") || title.includes("invoice") || title.includes("document")) {
    return "Collect itemized invoices, receipts, medical report, diagnosis certificate, prescriptions, and insurer claim forms.";
  }
  if (title.includes("follow-up") || title.includes("review")) {
    return "Confirm warning signs, medication plan, remote follow-up route, and return-travel fitness.";
  }
  return `Confirm timing, location, documents, payment expectations, and contact route with ${hospital}.`;
}

function hospitalDetailTemplate(item, option) {
  const protocol = option?.hospital_visit_protocol || fallbackOptions[0]?.hospital_visit_protocol || {};
  const contact = protocol.registration_contact || {};
  const doctor = protocol.suggested_doctor || {};
  const serviceBilling = option?.hospital_visit_protocol?.service_billing || {};
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
    registration_email: contact.email || "",
    registration_email_status: contact.email_status || "needs_confirmation",
    appointment_phone: contact.appointment_phone || "",
    main_phone: contact.main_phone || "",
    wechat_or_portal_route: contact.wechat_or_portal_route || "",
    service_billing_status: serviceBilling.service_billing_status || "needs_confirmation",
    direct_billing_status: serviceBilling.direct_billing_status || "unknown",
    suggested_doctor_name: isGenericDoctorText(doctor.name) ? "" : doctor.name || "",
    suggested_doctor_specialty: careTeamForTimelineItem(item, option, doctor),
    suggested_doctor_request: !isGenericDoctorRequest(doctor.request_note)
      ? doctor.request_note
      : nextConfirmationForTimelineItem(item, option),
    hospital_steps: hospitalSteps,
  };
}

function timelineDaysForDisplay(days, option) {
  return (days || []).map((day) => ({
    ...day,
    items: (day.items || []).map((item) => {
      if (!isHospitalTimelineCandidate(item) || hasTimelineHospitalDetails(item) || hasAnyTimelineDetails(item)) return item;
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

function timelineItemCount(days) {
  return (days || []).reduce((count, day) => count + (Array.isArray(day.items) ? day.items.length : 0), 0);
}

function renderTimelineDetails(item, option, day) {
  const details = item.details || {};
  if (!hasTimelineHospitalDetails(item) && !hasAnyTimelineDetails(item)) return "";

  const doctorLine = meaningfulDoctorLine(details) || (!isGenericDoctorText(details.suggested_doctor_specialty) ? details.suggested_doctor_specialty : "");
  const appointmentRoute = [
    details.registration_desk,
    details.appointment_phone ? `Phone: ${details.appointment_phone}` : "",
    details.wechat_or_portal_route ? `WeChat/portal: ${details.wechat_or_portal_route}` : "",
  ].filter(Boolean).join(" · ");
  const billingLine = [
    details.service_billing_status ? `Billing: ${details.service_billing_status.replaceAll("_", " ")}` : "",
    details.direct_billing_status ? `Direct billing: ${details.direct_billing_status.replaceAll("_", " ")}` : "",
  ].filter(Boolean).join(" · ");
  const nextConfirmation = !isGenericDoctorRequest(details.suggested_doctor_request) ? details.suggested_doctor_request : "";
  const status = details.registration_email_status ? ` (${details.registration_email_status.replaceAll("_", " ")})` : "";
  const registrationEmailHref = details.registration_email
    ? registrationEmailMailto(details.registration_email, { option, item, day, details })
    : "";
  const consumedKeys = new Set([
    "registration_desk",
    "appointment_phone",
    "wechat_or_portal_route",
    "registration_email",
    "registration_email_status",
    "suggested_doctor_name",
    "suggested_doctor_specialty",
    "service_billing_status",
    "direct_billing_status",
    "suggested_doctor_request",
    "hospital_steps",
  ]);
  const structuredRows = timelineDetailRows(details, consumedKeys);
  return `
    <div class="timeline-details">
      ${structuredRows}
      ${
        appointmentRoute
          ? timelineDetailRowHtml("support_agent", "Appointment", appointmentRoute)
          : ""
      }
      ${
        details.registration_email
          ? `<div class="timeline-detail-row"><span class="material-symbols-outlined">alternate_email</span><b>Email</b><p><a href="${escapeHtml(registrationEmailHref)}">${escapeHtml(details.registration_email)}</a>${escapeHtml(status)}</p></div>`
          : ""
      }
      ${
        doctorLine
          ? timelineDetailRowHtml("stethoscope", "Care team", doctorLine)
          : ""
      }
      ${
        billingLine
          ? timelineDetailRowHtml("receipt_long", "Billing", billingLine)
          : ""
      }
      ${
        nextConfirmation
          ? timelineDetailRowHtml("assignment_ind", "Confirm next", nextConfirmation)
          : ""
      }
      ${
        details.hospital_steps?.length
          ? `<div class="timeline-detail-row timeline-detail-steps"><span class="material-symbols-outlined">checklist</span><b>Before you go</b><ul>${details.hospital_steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ul></div>`
          : ""
      }
    </div>
  `;
}

function timelineDetailRows(details, consumedKeys) {
  return Object.entries(details)
    .filter(([key, value]) => !consumedKeys.has(key) && !isTechnicalTimelineDetailKey(key) && compactStructuredValue(value))
    .map(([key, value]) => {
      const label = friendlyTimelineDetailLabel(key);
      const valueHtml = timelineDetailValueHtml(key, value);
      if (!valueHtml) return "";
      const rowClass = isSourceLeadKey(key) ? " timeline-detail-source-row" : "";
      return `<div class="timeline-detail-row${rowClass}"><span class="material-symbols-outlined">${timelineDetailIcon(key)}</span><b>${escapeHtml(label)}</b><p>${valueHtml}</p></div>`;
    })
    .join("");
}

function timelineDetailRowHtml(icon, label, value) {
  return `<div class="timeline-detail-row"><span class="material-symbols-outlined">${icon}</span><b>${escapeHtml(label)}</b><p>${flightSearchLinks(value)}</p></div>`;
}

function isTechnicalTimelineDetailKey(key) {
  const normalized = String(key || "").toLowerCase();
  return [
    "id",
    "item_id",
    "option_id",
    "report_id",
    "category",
    "confidence_level",
    "metadata",
    "source",
    "source_updated_at",
    "generated_at",
    "data_status",
    "schema",
    "raw_output",
    "validation_errors",
    "contact_lookup_skill",
    "contact_lookup_skill_path",
    "contact_lookup_source_registry",
    "contact_lookup_required_fields",
    "contact_lookup_audit_requirements",
  ].includes(normalized) || normalized.endsWith("_id") || normalized.endsWith("_status");
}

function friendlyTimelineDetailLabel(key) {
  const labels = {
    flight: "Flight",
    flight_number: "Flight",
    airline: "Airline",
    departure_airport: "From",
    arrival_airport: "To",
    departure_time: "Departure",
    arrival_time: "Arrival",
    hotel: "Hotel",
    documents: "Documents",
    claim_documents: "Claim documents",
    notes: "Notes",
    note: "Note",
    cost: "Cost",
    estimated_cost: "Cost",
    payment: "Payment",
    appointment_time: "Appointment time",
    contact: "Contact",
    phone: "Phone",
    address: "Address",
    contact_lookup_seed_sources: "Source leads",
    seed_official_sources: "Source leads",
    source_records: "Source links",
    contact_source_records: "Contact source records",
  };
  return labels[key] || humanizeKey(key);
}

function timelineDetailValueHtml(key, value) {
  const parsed = structuredValue(value);
  if (parsed === null || parsed === undefined || parsed === "") return "";
  if (isSourceLeadKey(key)) return sourceLeadListHtml(parsed);
  if (isMoneyObject(parsed)) return escapeHtml(money(parsed));
  if (Array.isArray(parsed)) {
    const items = parsed.map(compactStructuredValue).filter(Boolean);
    if (!items.length) return "";
    return `<ul class="timeline-detail-mini-list">${items.map((item) => `<li>${flightSearchLinks(item)}</li>`).join("")}</ul>`;
  }
  if (isObjectValue(parsed)) {
    const chips = Object.entries(parsed)
      .filter(([nestedKey, nestedValue]) => !isTechnicalTimelineDetailKey(nestedKey) && compactStructuredValue(nestedValue))
      .map(([nestedKey, nestedValue]) => {
        const nestedLabel = friendlyTimelineDetailLabel(nestedKey);
        const nestedText = isMoneyObject(nestedValue) ? money(nestedValue) : compactStructuredValue(nestedValue);
        return `<span class="timeline-detail-chip"><b>${escapeHtml(nestedLabel)}</b>${flightSearchLinks(nestedText)}</span>`;
      });
    return chips.length ? `<span class="timeline-detail-chipset">${chips.join("")}</span>` : "";
  }
  const text = compactStructuredValue(parsed);
  const sentenceParts = splitTimelineDetailText(text);
  if (sentenceParts.length > 1) {
    return `<ul class="timeline-detail-mini-list">${sentenceParts.map((part) => `<li>${flightSearchLinks(part)}</li>`).join("")}</ul>`;
  }
  return flightSearchLinks(text);
}

function isSourceLeadKey(key) {
  return [
    "contact_lookup_seed_sources",
    "seed_official_sources",
    "source_records",
    "contact_source_records",
    "hospital_source_records",
    "official_source_records",
  ].includes(String(key || ""));
}

function sourceLeadListHtml(value) {
  const sources = Array.isArray(value) ? value : [value];
  const cards = sources
    .filter(isObjectValue)
    .map((source) => {
      if (isStandaloneSourceRecord(source)) return sourceRecordCardHtml(source);
      const title = source.hospital || source.title || source.international_department_name || source.url || "Official source";
      const department = source.international_department_name || source.hospital_chinese || "";
      const contactBits = [
        source.registration_email ? `Email: ${source.registration_email}` : "",
        source.appointment_phone ? `Phone: ${source.appointment_phone}` : "",
        source.wechat_or_portal_route ? `Portal: ${source.wechat_or_portal_route}` : "",
      ].filter(Boolean);
      const records = Array.isArray(source.source_records) ? source.source_records : [];
      const recordLinks = records
        .slice(0, 3)
        .map((record) => {
          const linkTitle = record.title || record.url || "Official page";
          return record.url
            ? `<a href="${escapeHtml(record.url)}" target="_blank" rel="noreferrer">${escapeHtml(linkTitle)}</a>`
            : escapeHtml(linkTitle);
        });
      const directUrl = source.url
        ? `<a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(source.title || source.url)}</a>`
        : "";
      const links = [...(directUrl ? [directUrl] : []), ...recordLinks];
      return `
        <span class="timeline-source-card">
          <strong>${googleSearchAnchor(title, `${title} international department`)}</strong>
          ${department && department !== title ? `<em>${escapeHtml(department)}</em>` : ""}
          ${contactBits.length ? `<span>${contactBits.map(escapeHtml).join(" · ")}</span>` : ""}
          ${source.date_checked ? `<span>Checked ${escapeHtml(source.date_checked)}</span>` : ""}
          ${links.length ? `<span class="timeline-source-links">${links.join("")}</span>` : ""}
        </span>
      `;
    })
    .join("");
  if (cards) return `<span class="timeline-source-list">${cards}</span>`;
  return flightSearchLinks(compactStructuredValue(value));
}

function isStandaloneSourceRecord(source) {
  return Boolean(source?.url || source?.title) &&
    !source.hospital &&
    !source.hospital_chinese &&
    !source.international_department_name &&
    !source.registration_email &&
    !source.appointment_phone &&
    !source.wechat_or_portal_route &&
    !Array.isArray(source.source_records);
}

function sourceRecordCardHtml(source) {
  const title = source.title || source.url || "Official page";
  const titleHtml = source.url
    ? `<a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(title)}</a>`
    : escapeHtml(title);
  const meta = [
    source.source_type ? humanizeKey(source.source_type) : "",
    Array.isArray(source.fields_verified) && source.fields_verified.length
      ? `Verified: ${source.fields_verified.map(humanizeKey).join(", ")}`
      : "",
    source.date_checked ? `Checked ${source.date_checked}` : "",
  ].filter(Boolean);
  return `
    <span class="timeline-source-card timeline-source-record-card">
      <strong>${titleHtml}</strong>
      ${meta.length ? `<span>${meta.map(escapeHtml).join(" · ")}</span>` : ""}
    </span>
  `;
}

function splitTimelineDetailText(text) {
  const cleaned = String(text || "").trim();
  if (cleaned.length < 150) return [cleaned].filter(Boolean);
  return cleaned
    .split(/(?<=[.!?])\s+|;\s+/)
    .map((part) => part.trim())
    .filter(Boolean);
}

function registrationEmailMailto(email, { option, item, day, details }) {
  const profile = state.report?.profile || {};
  const medicalPurpose = humanizeKey(profile.medical_purpose || option?.medical_purpose || "medical care");
  const procedureSubtype = humanizeKey(profile.procedure_subtype || option?.procedure_subtype || "to confirm");
  const preferredDate = option?.start_date || day?.date || item?.start_time?.slice(0, 10) || "to confirm";
  const subject = `International patient registration request - ${medicalPurpose} - ${option?.city || "China"}`;
  const bodyLines = [
    "Dear International Patient Services Team,",
    "",
    `I am writing to request appointment and registration guidance for international patient care at ${option?.target_hospital || "your hospital"}.`,
    "",
    "Patient and trip information:",
    `- Medical purpose: ${medicalPurpose}`,
    `- Procedure/subtype: ${procedureSubtype}`,
    `- Program details: ${profile.program_details || option?.program_details || "to confirm"}`,
    `- Passport/nationality: ${profile.nationality || "to confirm"}`,
    `- Residence/departure city: ${[profile.residence_country, profile.departure_city].filter(Boolean).join(" / ") || "to confirm"}`,
    `- Preferred travel or appointment date: ${preferredDate}`,
    `- Current insurance holder: ${profile.current_insurance_holder || "not provided"}`,
    `- Traveler count: ${profile.traveler_count || 1}`,
    "",
    "Selected plan context:",
    `- City: ${option?.city || "to confirm"}`,
    `- Hospital: ${option?.target_hospital || "to confirm"}`,
    `- Timeline item: ${timelineItemTitle(item)}`,
    details.appointment_phone ? `- Appointment phone shown in plan: ${details.appointment_phone}` : null,
    details.wechat_or_portal_route ? `- WeChat/portal route shown in plan: ${details.wechat_or_portal_route}` : null,
    details.service_billing_status ? `- Service billing status shown in plan: ${details.service_billing_status}` : null,
    "",
    "Could you please confirm:",
    "1. Whether this is the correct official registration channel for international patients.",
    "2. Which documents are required before an appointment can be confirmed.",
    "3. The earliest suitable appointment date and the responsible department or specialist team.",
    "4. Whether a deposit, pre-authorization, direct billing, or self-pay process applies.",
    "5. Whether English-language assistance or interpreter support is available.",
    "",
    "For privacy, I will send passport details and medical records only after you confirm the official hospital channel and required document list.",
    "",
    "Kind regards,",
  ].filter((line) => line !== null);
  const recipient = String(email || "").split(/[;,]/)[0].trim();
  const body = bodyLines.join("\n");
  return `mailto:${encodeURI(recipient)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

function timelineDetailIcon(key) {
  const text = normalizedText(key);
  if (text.includes("flight")) return "flight";
  if (text.includes("hotel")) return "hotel";
  if (text.includes("phone") || text.includes("contact")) return "call";
  if (text.includes("email")) return "alternate_email";
  if (text.includes("doctor") || text.includes("specialist") || text.includes("team")) return "stethoscope";
  if (text.includes("billing") || text.includes("cost") || text.includes("payment")) return "receipt_long";
  if (text.includes("document") || text.includes("record")) return "description";
  return "notes";
}

function timelineItemTitle(item) {
  const value = structuredValue(item?.title || item?.event || item?.name || "Plan item");
  if (isObjectValue(value)) {
    const directTitle = value.title || value.event || value.name || value.activity || value.description || value.summary;
    if (directTitle && !isObjectValue(structuredValue(directTitle))) return compactStructuredValue(directTitle);
    if (value.flight_number) {
      return ["Flight", value.flight_number, value.arrival_time ? `arrives ${value.arrival_time}` : ""].filter(Boolean).join(" ");
    }
    if (value.appointment_time || value.appointment_phone || value.registration_email) return "Appointment details";
    return `${humanizeKey(item?.category || "Plan")} details`;
  }
  return compactStructuredValue(value) || "Plan item";
}

function flightSearchLinks(value) {
  const text = String(value || "");
  const flightNumberPattern = /\b(?=[A-Z0-9]{2}\d{2,4}\b)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{2}\d{2,4}\b/gi;
  let cursor = 0;
  let html = "";
  for (const match of text.matchAll(flightNumberPattern)) {
    const flightNumber = match[0].toUpperCase();
    html += escapeHtml(text.slice(cursor, match.index));
    html += googleSearchAnchor(match[0], flightNumber);
    cursor = match.index + match[0].length;
  }
  html += escapeHtml(text.slice(cursor));
  return html;
}

function googleSearchHref(query) {
  return `https://www.google.com/search?q=${encodeURIComponent(String(query || "").trim())}`;
}

function googleSearchAnchor(label, query = label) {
  const text = compactStructuredValue(label);
  if (!text) return "";
  return `<a href="${escapeHtml(googleSearchHref(query || text))}" target="_blank" rel="noreferrer">${escapeHtml(text)}</a>`;
}

function timelineLocationText(value) {
  return compactStructuredValue(value);
}

function timelineLocationHtml(item, option) {
  const text = timelineLocationText(item?.location_name);
  if (!text) return "";
  if (!shouldLinkTimelinePlace(item, text)) return flightSearchLinks(text);
  return googleSearchAnchor(text, googlePlaceSearchQuery(text, item, option));
}

function timelineAddressHtml(item, option) {
  const text = timelineLocationText(item?.address);
  if (!text) return "";
  if (!shouldLinkTimelinePlace(item, text)) return escapeHtml(text);
  return googleSearchAnchor(text, googlePlaceSearchQuery(text, item, option));
}

function shouldLinkTimelinePlace(item, text) {
  const category = String(item?.category || "").toLowerCase();
  const normalized = normalizedText(text);
  return (
    category === "hotel" ||
    category === "medical" ||
    normalized.includes("hospital") ||
    normalized.includes("clinic") ||
    normalized.includes("hotel") ||
    normalized.includes("medical center")
  );
}

function googlePlaceSearchQuery(text, item, option) {
  const category = String(item?.category || "").toLowerCase();
  const qualifiers = [
    text,
    option?.city,
    category === "hotel" ? "hotel" : "",
    category === "medical" ? "international department hospital" : "",
  ].filter(Boolean);
  return qualifiers.join(" ");
}

function hotelSearchLinks(option) {
  if (!option?.hotel?.name) return "-";
  const hotel = option.hotel;
  const linkedName = googleSearchAnchor(hotel.name, `${hotel.name} ${option.city || ""} hotel`);
  return [linkedName, hotel.distance_to_hospital ? escapeHtml(hotel.distance_to_hospital) : ""].filter(Boolean).join(", ");
}

function flightSummaryLinks(option) {
  if (!option?.flight) return "-";
  const flightNumber = option.flight.flight_number || "";
  const arrival = option.flight.arrival_airport || "";
  return [flightNumber ? flightSearchLinks(flightNumber) : "", arrival ? `to ${escapeHtml(arrival)}` : ""].filter(Boolean).join(" ");
}


function riskCount(option) {
  const count = option.key_risks?.length || 0;
  return `${count} ${count === 1 ? t("compare.riskSingular") : t("compare.riskPlural")}`;
}

function confidence(option) {
  return option.metadata?.confidence_level || option.medical_confidence || "medium";
}

function progressForOption(option, index) {
  const savings = moneyAmount(savingsForDisplay(option));
  return Math.max(54, Math.min(92, 62 + index * 6 + Math.round(savings / 1000)));
}

function selectedOption() {
  const options = state.options.length ? state.options : state.generationAttempted ? [] : fallbackOptions;
  return options.find((option) => option.option_id === state.selectedOptionId) || options[0] || null;
}

function renderCities() {
  const cityCards = document.querySelector("#cityCards");
  const rawOptions = state.options.length ? state.options : state.generationAttempted ? [] : fallbackOptions;
  const options = rawOptions.map(optionForDisplay);
  if (!options.length) {
    cityCards.innerHTML = `
      <article class="city-card selected">
        <span class="city-label">
          <span class="material-symbols-outlined">error</span>
          ${t("compare.noAgentOptions")}
        </span>
        <h2>${t("compare.noPlansTitle")}</h2>
        <div class="hospital-line">
          <strong>${t("compare.noPlansBody")}</strong>
          <span>${t("compare.noPlansHint")}</span>
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
            ${option.recommendation_label || t("compare.cityOption")}
          </span>
          <h2>${option.city}</h2>
          <div class="hospital-line">
            <strong><span class="material-symbols-outlined" style="font-size:16px">local_hospital</span> ${option.target_hospital}</strong>
            <span>${option.recommendation_reason || t("compare.internationalEstimate")}</span>
          </div>
          <div class="mini-divider"></div>
          <div class="metric-row">
            <div><span>${t("compare.totalCost")}</span><strong>${money(option.total_estimated_cost)}</strong></div>
            <div><span>${t("compare.duration")}</span><strong>${option.required_days || "-"} ${t("compare.days")}</strong></div>
          </div>
          <span class="muted">${t("compare.savings")}</span>
          <strong class="savings-value">${money(savingsForDisplay(option))}</strong>
          <div class="savings-bar"><span style="width:${progressForOption(option, index)}%"></span></div>
          <div class="risk-tags">
            <span>${t("compare.confidence")}: ${confidence(option)}</span>
            <span>${riskCount(option)}</span>
          </div>
          <button
            class="${selected ? "primary-button selected" : "outline-button"} select-plan"
            type="button"
            ${selected ? `data-open-plan-option-id="${option.option_id}"` : `data-compare-option-id="${option.option_id}"`}
          >
            ${selected ? t("compare.viewTimeline") : t("compare.selectPlan")}
          </button>
        </article>
      `;
    })
    .join("");
  renderAnalysisTable();
}

function renderAnalysisTable() {
  const table = document.querySelector("#analysisTable");
  const rawOptions = state.options.length ? state.options : state.generationAttempted ? [] : fallbackOptions;
  const options = rawOptions.map(optionForDisplay);
  if (!options.length) {
    table.innerHTML = `
      <div class="row header"><div>${t("compare.metric")}</div><div>${t("compare.noGeneratedOptions")}</div></div>
      <div class="row"><div>Status</div><div>${t("compare.noCityOptionsStatus")}</div></div>
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
    <div class="row header"><div>${t("compare.metric")}</div>${headers}</div>
    <div class="section-row">${t("compare.sectionMedicalTravel")}</div>
    ${row(t("compare.hospital"), options.map((option) => option.target_hospital))}
    ${row(t("compare.duration"), options.map((option) => `${option.required_days || "-"} ${t("compare.days").toLowerCase()}`))}
    ${row(t("compare.flight"), options.map((option) => flightSummaryLinks(option)))}
    ${row(t("compare.hotel"), options.map((option) => hotelSearchLinks(option)))}
    <div class="section-row">${t("compare.sectionCosts")}</div>
    ${row(t("compare.medicalEstimate"), options.map((option) => money(option.cost_breakdown?.medical)))}
    ${row(t("compare.insuranceEstimate"), options.map((option) => money(option.cost_breakdown?.travel_insurance || option.insurance_policy?.estimated_premium)))}
    ${row(t("compare.totalEstimate"), options.map((option) => money(option.total_estimated_cost)))}
    ${row(t("compare.estimatedSavings"), options.map((option) => money(savingsForDisplay(option))))}
    <div class="section-row">${t("compare.sectionInsurance")}</div>
    ${row(t("compare.policyReview"), options.map((option) => insuranceStatusLabel(option.insurance_policy?.policy_status)))}
    ${row(t("compare.hospitalBilling"), options.map((option) => option.insurance_policy?.hospital_policy?.direct_billing || "Confirm with hospital"))}
    <div class="section-row">${t("compare.sectionRisk")}</div>
    ${row(t("compare.identifiedFactors"), options.map((option) => (option.key_risks || []).join(" ")))}
  `;
}

function renderPlan() {
  const rawOption = selectedOption();
  const option = optionForDisplay(rawOption);
  const endpointDays = Array.isArray(state.timeline?.days) ? state.timeline.days : [];
  const optionDays = Array.isArray(option?.timeline) ? option.timeline : [];
  const rawTimelineDays = timelineItemCount(endpointDays) ? endpointDays : timelineItemCount(optionDays) ? optionDays : [];
  const displaySourceDays = rawTimelineDays.length
    ? rawTimelineDays
    : option
      ? clientFallbackTimeline(option)
      : state.generationAttempted
        ? []
        : fallbackOptions[0]?.timeline || [];
  const localizedDisplaySourceDays = isPreviewOption(rawOption) ? localizePreviewValue(displaySourceDays) : displaySourceDays;
  const timelineDays = timelineDaysForDisplay(localizedDisplaySourceDays, option || optionForDisplay(fallbackOptions[0]));
  document.querySelector("#sidePlanCity").textContent = option ? t("plan.cityPlan", { city: option.city }) : t("plan.selectedPlan");
  document.querySelector("#sidePlanSubtitle").textContent = option
    ? `${option.target_hospital}`
    : t("plan.chooseCity");
  document.querySelector("#planSubtitle").textContent = option
    ? t("plan.subtitleSelected", { city: option.city })
    : t("plan.subtitleDefault");
  renderPlanCitySwitcher(option);
  renderTimeline(timelineDays, option || optionForDisplay(fallbackOptions[0]));
  renderCostCard(state.costs, option);
  renderInsuranceCard(option);
}

function renderPlanCitySwitcher(activeOption) {
  const switcher = document.querySelector("#planCitySwitcher");
  if (!switcher) return;
  const rawOptions = state.options.length ? state.options : state.generationAttempted ? [] : fallbackOptions;
  const options = rawOptions.map(optionForDisplay);

  if (!options.length) {
    switcher.innerHTML = `
      <div class="plan-city-empty">
        <span class="material-symbols-outlined">travel_explore</span>
        <span>${t("plan.compareCityPlans")}</span>
      </div>
    `;
    return;
  }

  switcher.innerHTML = `
    <span class="switcher-label">${t("plan.cityPlans")}</span>
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
                <small>${option.required_days || "-"} ${t("compare.days").toLowerCase()} &middot; ${money(option.total_estimated_cost)}</small>
              </span>
              <span class="material-symbols-outlined">${selected ? "check_circle" : "chevron_right"}</span>
            </button>
          `;
        })
        .join("")}
    </div>
  `;
}

function renderTimeline(days, option) {
  const timeline = document.querySelector("#timelineDays");
  if (!days.length) {
    timeline.innerHTML = `<article class="day-card"><h2>${t("plan.noTimelineTitle")}</h2><p>${t("plan.noTimelineBody")}</p></article>`;
    return;
  }
  timeline.innerHTML = days
    .map(
      (day) => `
        <article class="day-card">
          <h2>${t("plan.day")} ${escapeHtml(day.day)}: ${escapeHtml(compactStructuredValue(day.title) || `${t("plan.day")} ${day.day}`)}</h2>
          <p>${escapeHtml(textDate(day.date))}</p>
          <div class="timeline-list">
            ${(day.items || [])
              .map(
                (item) => `
                  <div class="timeline-node ${item.category}">
                    <span class="node-icon material-symbols-outlined">${iconForCategory(item.category)}</span>
                    <div class="node-card ${item.hard_constraint ? "scheduled" : ""}">
                      <div class="node-top">
                        <strong>${flightSearchLinks(timelineItemTitle(item))}</strong>
                        <time>${timeRange(item)}</time>
                      </div>
                      ${timelineLocationText(item.location_name) ? `<p>${timelineLocationHtml(item, option)}</p>` : ""}
                      ${timelineLocationText(item.address) ? `<p>${timelineAddressHtml(item, option)}</p>` : ""}
                      ${renderTimelineDetails(item, option, day)}
                      <div class="node-tags">
                        ${item.estimated_cost ? `<span>${t("plan.estimated")} ${money(item.estimated_cost)}</span>` : ""}
                        <span>${item.confidence_level ? `${item.confidence_level} ${t("compare.confidence").toLowerCase()}` : t("plan.mediumConfidence")}</span>
                        ${item.hard_constraint ? `<span>${t("plan.medicalConstraint")}</span>` : ""}
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
      <h2>${t("plan.costTitle")}</h2>
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
    <span>${t("plan.totalEstimatedCost")}</span>
    <dl class="cost-lines">
      ${Object.entries(categories)
        .map(([label, value]) => `<div><dt>${costCategoryLabel(label)}</dt><dd>${money(value, selectedCurrency)}</dd></div>`)
        .join("")}
    </dl>
    <p class="info-callout">
      ${t("plan.costNote", {
        currencyNote: selectedCurrency === "RMB" ? t("plan.rmbNote", { rate: RMB_PER_SGD }) : "",
      })}
    </p>
  `;
}

function renderInsuranceCard(option) {
  const card = document.querySelector("#insuranceCard");
  if (!card) return;
  const policy = option?.insurance_policy;
  if (!policy) {
    card.innerHTML = `
      <h2>${t("plan.insuranceTitle")}</h2>
      <p>${t("plan.noInsurance")}</p>
    `;
    return;
  }
  const profileHolder = state.report?.profile?.current_insurance_holder;
  const provider = policy.provider_policy || {};
  const hospitalPolicy = policy.hospital_policy || {};
  const currentHolder = policy.current_holder || profileHolder || t("plan.insurance.notProvided");
  const providerName = provider.display_name || currentHolder;
  const preauthLabel = hospitalPolicy.preauthorization_required
    ? t("plan.insurance.requiredLikely")
    : t("plan.insurance.notFlagged");
  const suggestionItems = listHtml(policy.suggestions);
  const claimDocItems = listHtml(hospitalPolicy.claim_documents || provider.claim_documents);
  const providerFocusItems = listHtml(provider.policy_lookup_focus);
  const providerQuestionItems = listHtml(provider.preauthorization_questions);
  const riskFlagItems = listHtml([...(hospitalPolicy.common_exclusions || []), ...(provider.risk_flags || [])]);
  const linkItems = (policy.helpful_links || [])
    .map((link) => {
      const title = escapeHtml(link.title || link.url || "Reference");
      const url = escapeHtml(link.url || "#");
      return `<li><a href="${url}" target="_blank" rel="noreferrer">${title}</a></li>`;
    })
    .join("");

  card.innerHTML = `
    <div class="insurance-card-top">
      <h2>${t("plan.insuranceTitle")}</h2>
      <span>${escapeHtml(insuranceStatusLabel(policy.policy_status))}</span>
    </div>
    <p>${escapeHtml(policy.summary)}</p>
    <dl class="insurance-lines">
      <div><dt>${t("plan.insurance.currentHolder")}</dt><dd>${escapeHtml(currentHolder)}</dd></div>
      <div><dt>${t("plan.insurance.providerGuidance")}</dt><dd>${escapeHtml(providerName)}${provider.matched ? t("plan.insurance.match") : t("plan.insurance.lookupNeeded")}</dd></div>
      <div><dt>${t("plan.insurance.hospitalBilling")}</dt><dd>${escapeHtml(policy.hospital_policy?.direct_billing || t("plan.insurance.confirmHospital"))}</dd></div>
      <div><dt>${t("plan.insurance.preauthorization")}</dt><dd>${escapeHtml(preauthLabel)}</dd></div>
      <div><dt>${t("plan.insurance.directBillingAssumption")}</dt><dd>${escapeHtml(provider.direct_billing_assumption || t("plan.insurance.defaultDirectBilling"))}</dd></div>
      <div><dt>${t("plan.insurance.estimatedPremium")}</dt><dd>${money(policy.estimated_premium)}</dd></div>
    </dl>
    <div class="insurance-section">
      <strong>${t("plan.insurance.providerChecklist")}</strong>
      ${providerFocusItems || `<p>${t("plan.insurance.defaultProviderChecklist")}</p>`}
    </div>
    <div class="insurance-section">
      <strong>${t("plan.insurance.preauthQuestions")}</strong>
      ${providerQuestionItems || `<p>${t("plan.insurance.defaultPreauthQuestions")}</p>`}
    </div>
    <div class="insurance-section">
      <strong>${t("plan.insurance.claimDocuments")}</strong>
      ${claimDocItems || `<p>${t("plan.insurance.defaultClaimDocuments")}</p>`}
    </div>
    <div class="insurance-section">
      <strong>${t("plan.insurance.risksExclusions")}</strong>
      ${riskFlagItems || `<p>${t("plan.insurance.defaultRisks")}</p>`}
    </div>
    <div class="insurance-section">
      <strong>${t("plan.insurance.suggestions")}</strong>
      ${suggestionItems || `<p>${t("plan.insurance.defaultSuggestions")}</p>`}
    </div>
    ${linkItems ? `<div class="insurance-section"><strong>${t("plan.insurance.helpfulLinks")}</strong><ul class="insurance-links">${linkItems}</ul></div>` : ""}
    <p class="info-callout">${t("plan.insurance.termsNote")}</p>
  `;
}

function listHtml(items) {
  const values = (items || []).filter((item) => item !== null && item !== undefined && String(item).trim());
  if (!values.length) return "";
  return `<ul>${values.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
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
  const programDetailConfigs = programDetailConfigsByLanguage[normalizeLanguage(state.language)] || programDetailConfigsByLanguage.en;
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
  const details = [];
  document.querySelectorAll("[data-program-detail]").forEach((field) => {
    const value = field.value?.trim?.() ?? field.value;
    if (value) {
      const label = field.dataset.programDetail.replaceAll("_", " ");
      details.push(`${label}: ${value}`);
    }
  });
  return details.join("; ");
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
    preferred_language: normalizeLanguage(state.language),
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

async function showFallbackOptionsAfterAgentError() {
  state.reportId = null;
  state.operationId = null;
  state.report = {
    report_status: "preview",
    status: "ready",
    city_options: fallbackOptions,
    recommended_option_id: fallbackOptions[0]?.option_id || null,
    confirmation_requests: [],
    disclaimers: [],
    assumptions: [],
  };
  state.options = fallbackOptions;
  state.selectedOptionId = fallbackOptions[0]?.option_id || null;
  useClientPlanSnapshot(selectedOption());
  persistState();
  renderCities();
  renderPlan();
  renderReadiness();
  finishAgentProgress();
  await delay(350);
  showRoute("compare");
  setStatus("", "info");
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
    label.textContent = t("intake.actions.generating");
    setStatus(
      plannerBackend === "adk" ? t("status.agentRunning") : t("status.localRunning"),
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
        language: normalizeLanguage(state.language),
        run_now: true,
        planner_backend: plannerBackend,
      }),
    });
    const generated = plannerBackend === "adk" ? (await Promise.all([reportRequest, delay(1800)]))[0] : await reportRequest;

    if (generated.status === "failed" || generated.report?.status === "failed" || generated.report?.error) {
      const detail = plannerErrorMessage(generated.report?.error || generated.error);
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
    useClientPlanSnapshot(selectedOption());
    persistState();
    renderCities();
    if (plannerBackend === "adk") {
      finishAgentProgress();
      await delay(650);
    }
    showRoute("compare");
    setStatus(t("status.generated", { count: state.options.length }), "success");
  } catch (error) {
    console.error(error);
    if (plannerBackend === "adk") {
      await showFallbackOptionsAfterAgentError();
    } else {
      persistState();
      setStatus(`API error: ${error.message}`, "error");
    }
  } finally {
    state.loading = false;
    button.disabled = false;
    label.textContent = t("intake.actions.generate");
  }
}

async function selectOption(optionId) {
  if (!optionId) {
    setStatus("Generate options before selecting a plan.", "error");
    return;
  }
  const option = (state.options.length ? state.options : fallbackOptions).find((item) => item.option_id === optionId);
  if (!option) {
    setStatus("Selected plan was not found in the generated options.", "error");
    return;
  }
  if (optionId === state.selectedOptionId && state.timeline && state.costs && state.readiness) {
    renderPlan();
    renderReadiness();
    showRoute("plan");
    return;
  }
  let backendReportMissing = false;
  try {
    if (state.reportId) {
      await api(`/api/v1/reports/${state.reportId}/options/${optionId}/select`, { method: "POST" });
    }
  } catch (error) {
    if (!isMissingBackendReportError(error)) throw error;
    backendReportMissing = true;
  }
  try {
    state.selectedOptionId = optionId;
    state.timeline = null;
    state.costs = null;
    state.readiness = null;
    useClientPlanSnapshot(option);
    renderPlan();
    renderReadiness();
    if (!backendReportMissing && state.reportId) {
      await loadSelectedPlan();
    }
    persistState();
    renderCities();
    renderPlan();
    renderReadiness();
    showRoute("plan");
    if (backendReportMissing) {
      setStatus("Opened timeline from the generated plan snapshot. Backend report storage was not available on this Vercel request.", "info");
    }
  } catch (error) {
    console.error(error);
    setStatus(`Could not select plan: ${error.message}`, "error");
  }
}

async function selectComparisonOption(optionId) {
  if (!optionId) {
    setStatus("Generate options before selecting a plan.", "error");
    return;
  }
  const option = (state.options.length ? state.options : fallbackOptions).find((item) => item.option_id === optionId);
  if (!option) {
    setStatus("Selected city was not found in the generated options.", "error");
    return;
  }
  try {
    if (optionId !== state.selectedOptionId) {
      if (state.reportId) {
        try {
          await api(`/api/v1/reports/${state.reportId}/options/${optionId}/select`, { method: "POST" });
        } catch (error) {
          if (!isMissingBackendReportError(error)) throw error;
        }
      }
      state.selectedOptionId = optionId;
      state.timeline = null;
      state.costs = null;
      state.readiness = null;
      useClientPlanSnapshot(option);
      persistState();
    }
    renderCities();
    setStatus(`${option?.city || "City"} selected. Tap View Timeline to open the detailed plan.`, "success");
  } catch (error) {
    console.error(error);
    setStatus(`Could not select city: ${error.message}`, "error");
  }
}

async function loadSelectedPlan() {
  if (!state.reportId || !state.selectedOptionId) return;
  try {
    const [timeline, costs, readiness] = await Promise.all([
      api(`/api/v1/reports/${state.reportId}/options/${state.selectedOptionId}/timeline`),
      api(`/api/v1/reports/${state.reportId}/options/${state.selectedOptionId}/costs`),
      api(`/api/v1/reports/${state.reportId}/options/${state.selectedOptionId}/readiness`),
    ]);
    state.timeline = timeline;
    state.costs = costs;
    state.readiness = readiness;
  } catch (error) {
    if (!isMissingBackendReportError(error)) throw error;
    useClientPlanSnapshot(selectedOption());
  }
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

async function exportPlanPdf() {
  const option = selectedOption();
  if (!option) {
    setStatus("Generate and select a plan before exporting a PDF.", "error");
    return;
  }
  const button = document.querySelector("#exportPdfButton");
  const label = button?.querySelector(".button-label");
  const previousLabel = label?.textContent || "Export PDF";
  try {
    if (button) button.disabled = true;
    if (label) label.textContent = "Preparing...";
    const response = await fetchPlanPdfResponse(option);
    await downloadPdfResponse(response, `medtour-plan-${option.option_id || "local"}.pdf`);
    setStatus("PDF export ready.", "success");
  } catch (error) {
    console.error(error);
    setStatus(`Could not export PDF: ${error.message}`, "error");
  } finally {
    if (button) button.disabled = false;
    if (label) label.textContent = previousLabel;
  }
}

async function fetchPlanPdfResponse(option) {
  const response = await fetch(`${API_BASE_URL}/api/v1/plan-export.pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      report: state.report || {},
      option: planExportSnapshot(option),
    }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${detail}`);
  }
  return response;
}

function planExportSnapshot(option) {
  const snapshot = JSON.parse(JSON.stringify(option));
  const endpointDays = Array.isArray(state.timeline?.days) ? state.timeline.days : [];
  const optionDays = Array.isArray(option.timeline) ? option.timeline : [];
  const timeline = endpointDays.length ? endpointDays : optionDays.length ? optionDays : clientFallbackTimeline(option);
  snapshot.timeline = timelineDaysForDisplay(timeline, option);

  if (state.costs?.categories) snapshot.cost_breakdown = state.costs.categories;
  if (state.costs?.total) snapshot.total_estimated_cost = state.costs.total;

  const readinessItems = (state.readiness?.sections || []).flatMap((section) => section.items || []);
  if (readinessItems.length) snapshot.readiness_items = readinessItems;
  if (!snapshot.option_id) snapshot.option_id = "local_plan";
  return snapshot;
}

async function downloadPdfResponse(response, fallbackFilename) {
  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") || "";
  const filename = disposition.match(/filename="([^"]+)"/)?.[1] || fallbackFilename;
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function updateReadiness(itemId, checked) {
  if (!state.selectedOptionId) return;
  const applyClientReadinessUpdate = () => {
    const sections = state.readiness?.sections || [];
    sections.forEach((section) => {
      (section.items || []).forEach((item) => {
        if (item.id === itemId) item.status = checked ? "complete" : "pending";
      });
    });
    const items = sections.flatMap((section) => section.items || []);
    const completed = items.filter((item) => item.status === "complete");
    const highRisk = items.filter((item) => item.priority === "high" && item.status !== "complete");
    state.readiness = {
      ...state.readiness,
      completion_percent: items.length ? Math.round((completed.length / items.length) * 100) : 0,
      completed_count: completed.length,
      total_count: items.length,
      high_risk_items: highRisk,
      sections,
    };
    persistState();
    renderReadiness();
  };
  if (!state.reportId) {
    applyClientReadinessUpdate();
    return;
  }
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
    if (isMissingBackendReportError(error)) {
      applyClientReadinessUpdate();
      setStatus("Updated readiness locally for this plan snapshot.", "info");
      return;
    }
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
      language: state.language,
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
    state.language = normalizeLanguage(state.language);
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
      selectOption(openPlanButton.dataset.openPlanOptionId);
      return;
    }

    const compareCard = event.target.closest(".city-card[data-compare-option-id]");
    if (compareCard) {
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
      return;
    }

    const exportPdfButton = event.target.closest("#exportPdfButton");
    if (exportPdfButton) {
      exportPlanPdf();
    }
  });

  document.addEventListener("change", (event) => {
    const languageSelect = event.target.closest("#languageSelect");
    if (languageSelect) {
      state.language = normalizeLanguage(languageSelect.value);
      persistState();
      applyTranslations();
      renderProgramDetails();
      renderAgentProgress();
      renderCities();
      renderPlan();
      renderReadiness();
      setAgentBackendAvailable(!document.querySelector('[data-planner-backend="adk"]')?.disabled);
      return;
    }

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
applyTranslations();
setPlannerBackend(state.plannerBackend || "adk");
loadPlannerConfig();
renderAgentProgress();
renderProgramDetails();
renderCities();
renderPlan();
renderReadiness();
bindInteractions();
showRoute(location.hash.replace("#", "") || "intake");
refreshAuthSession();
