"""Typed contracts shared by API code and ADK agents."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ConfidenceLevel(StrEnum):
    high = "high"
    medium = "medium"
    low = "low"


class DataStatus(StrEnum):
    real_time = "real_time"
    estimated = "estimated"
    stale = "stale"
    needs_confirmation = "needs_confirmation"


class Money(BaseModel):
    amount: float
    currency: str = "SGD"
    low: float | None = None
    high: float | None = None


class SourceMetadata(BaseModel):
    source: Literal["rag", "external_api", "agent_estimate", "advisor_confirmed"]
    source_url: str | None = None
    source_updated_at: str | None = None
    generated_at: str | None = None
    confidence_level: ConfidenceLevel = ConfidenceLevel.medium
    data_status: DataStatus = DataStatus.estimated


class IntakeAnswers(BaseModel):
    medical_purpose: str
    procedure_subtype: str | None = None
    program_details: dict[str, Any] = Field(default_factory=dict)
    nationality: str
    residence_country: str | None = None
    departure_city: str
    current_insurance_holder: str | None = None
    date_mode: str = "flexible"
    planned_date: str | None = None
    date_range: dict[str, str] | None = None
    duration_preference: str = "5_7_days"
    season_flexibility: str = "depends_on_price"
    budget_tier: str = "balanced"
    traveler_count: int = Field(default=1, ge=1, le=8)
    hotel_preference: str = "near_hospital_foreign_guest_eligible"
    tourism_intensity: str = "light"


class ConfirmationOption(BaseModel):
    id: str
    label: str
    impact: str
    recommended: bool = False


class ConfirmationRequest(BaseModel):
    confirmation_id: str
    blocking: bool
    question: str
    reason: str
    recommended_option: str | None = None
    options: list[ConfirmationOption]
    affected_sections: list[str] = Field(default_factory=list)


class FlightDetails(BaseModel):
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    estimated_cost: Money


class HotelChoice(BaseModel):
    name: str
    address: str
    nightly_rate: Money
    nights: int
    distance_to_hospital: str
    foreign_guest_eligible: bool
    cancellation_policy: str


class HospitalInsurancePolicy(BaseModel):
    direct_billing: str
    preauthorization_required: bool = True
    claim_documents: list[str] = Field(default_factory=list)
    common_exclusions: list[str] = Field(default_factory=list)


class InsurancePolicy(BaseModel):
    current_holder: str | None = None
    hospital_name: str
    medical_purpose: str | None = None
    policy_status: str
    summary: str
    hospital_policy: HospitalInsurancePolicy
    estimated_premium: Money
    suggestions: list[str] = Field(default_factory=list)
    helpful_links: list[dict[str, str]] = Field(default_factory=list)
    metadata: SourceMetadata


class TimelineItem(BaseModel):
    item_id: str
    category: Literal["flight", "hotel", "medical", "transport", "meal", "tourism", "readiness"]
    title: str
    start_time: str
    end_time: str
    location_name: str | None = None
    address: str | None = None
    estimated_cost: Money | None = None
    hard_constraint: bool = False
    confidence_level: ConfidenceLevel = ConfidenceLevel.medium
    details: dict[str, Any] = Field(default_factory=dict)


class TimelineDay(BaseModel):
    day: int
    date: str
    title: str
    items: list[TimelineItem]


class ReadinessItem(BaseModel):
    id: str
    title: str
    priority: Literal["low", "medium", "high"] = "medium"
    status: Literal["pending", "in_progress", "complete", "blocked"] = "pending"
    steps: list[str] = Field(default_factory=list)
    helpful_links: list[dict[str, str]] = Field(default_factory=list)


class CityPlanOption(BaseModel):
    option_id: str
    city: str
    recommendation_label: str
    target_hospital: str
    required_days: int
    total_estimated_cost: Money
    estimated_net_savings: Money
    flight: FlightDetails
    hotel: HotelChoice
    timeline: list[TimelineDay]
    cost_breakdown: dict[str, Money]
    insurance_policy: InsurancePolicy | None = None
    readiness_items: list[ReadinessItem] = Field(default_factory=list)
    readiness_summary: list[str] = Field(default_factory=list)
    key_risks: list[str]
    metadata: SourceMetadata


class GeneratedReport(BaseModel):
    report_id: str
    status: Literal["queued", "generating", "needs_confirmation", "ready", "failed"]
    profile: dict[str, Any]
    city_options: list[CityPlanOption]
    confirmation_requests: list[ConfirmationRequest] = Field(default_factory=list)
    selected_option_id: str | None = None
    disclaimers: list[str] = Field(default_factory=list)
