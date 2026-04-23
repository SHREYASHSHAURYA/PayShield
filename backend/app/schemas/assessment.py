from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, constr

from app.models.enums import (
    InteractionType,
    PaymentDirection,
    PaymentMethodType,
    RecommendedAction,
    RiskLevel,
    ScamStage,
    SignalType,
)


class InteractionEvent(BaseModel):
    event_id: constr(strip_whitespace=True, min_length=1, max_length=64)
    timestamp: datetime
    interaction_type: InteractionType
    content_text: Optional[constr(strip_whitespace=True, max_length=1000)] = None
    source_label: Optional[constr(strip_whitespace=True, max_length=120)] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class PaymentContext(BaseModel):
    payment_method: PaymentMethodType = PaymentMethodType.NONE
    payment_direction: PaymentDirection = PaymentDirection.NONE
    amount: Optional[Decimal] = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    currency: constr(strip_whitespace=True, min_length=3, max_length=3) = "INR"
    upi_id: Optional[constr(strip_whitespace=True, max_length=120)] = None
    collect_request_present: bool = False
    qr_present: bool = False
    payment_link_present: bool = False
    merchant_name: Optional[constr(strip_whitespace=True, max_length=120)] = None
    note: Optional[constr(strip_whitespace=True, max_length=250)] = None


class UserFlags(BaseModel):
    user_expects_money: bool = False
    user_initiated_contact: bool = False
    trusted_beneficiary: bool = False
    first_time_beneficiary: bool = True
    user_confirms_pressure: bool = False
    user_confirms_identity_verified: bool = False


class AssessmentRequest(BaseModel):
    session_id: constr(strip_whitespace=True, min_length=1, max_length=64)
    device_timestamp: datetime
    locale: constr(strip_whitespace=True, min_length=2, max_length=16) = "en-IN"
    interaction_events: List[InteractionEvent] = Field(min_length=1, max_length=50)
    payment_context: PaymentContext
    user_flags: UserFlags = Field(default_factory=UserFlags)


class TriggeredSignal(BaseModel):
    signal_type: SignalType
    confidence: float = Field(ge=0.0, le=1.0)
    source_event_id: Optional[str] = None
    evidence: constr(strip_whitespace=True, min_length=1, max_length=200)


class StageState(BaseModel):
    current_stage: ScamStage
    completed_stages: List[ScamStage] = Field(default_factory=list)


class AssessmentResponse(BaseModel):
    request_id: constr(strip_whitespace=True, min_length=1, max_length=64)
    session_id: constr(strip_whitespace=True, min_length=1, max_length=64)
    risk_level: RiskLevel
    risk_score: int = Field(ge=0, le=100)
    current_stage: ScamStage
    recommended_action: RecommendedAction
    should_warn_user: bool
    triggered_signals: List[TriggeredSignal]
    stage_state: StageState
    explanation: List[constr(strip_whitespace=True, min_length=1, max_length=200)]
