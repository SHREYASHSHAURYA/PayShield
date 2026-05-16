from uuid import uuid4

from fastapi import APIRouter, Depends, Header

from app.schemas.assessment import AssessmentRequest, AssessmentResponse, StageState
from app.services.audit_logger import write_audit_log
from app.services.ml_engine import HybridSignalPipeline
from app.services.risk_engine import RiskEngine
from app.services.security import rate_limiter, verify_api_key
from app.services.stage_engine import StageClassifier
from app.services.state_machine import (
    InMemorySessionStore,
    ScamStateMachine,
    SessionContext,
)

router = APIRouter()
session_store = InMemorySessionStore()
state_machine = ScamStateMachine()


def _build_beneficiary_key(request: AssessmentRequest) -> str:
    payment = request.payment_context

    if payment.upi_id:
        return payment.upi_id.strip().lower()

    if payment.merchant_name:
        return payment.merchant_name.strip().lower()

    return ""


def _is_safe_payment_context(
    request: AssessmentRequest,
    detected_stage: str,
    scam_probability: float,
    rule_signals: list,
) -> bool:
    signal_types = {signal.signal_type.value for signal in rule_signals}

    dangerous_signals = {
        "urgency",
        "impersonation",
        "fear_pressure",
        "qr_payment_prompt",
        "collect_request_detected",
        "payment_link_shared",
        "remote_app_request",
        "transaction_confirmation_request",
        "account_block_claim",
        "authority_claim",
    }

    if signal_types & dangerous_signals:
        return False

    if detected_stage != "payment":
        return False

    if scam_probability >= 0.20:
        return False

    if request.payment_context.qr_present:
        return False

    if request.payment_context.collect_request_present:
        return False

    if request.payment_context.payment_link_present:
        return False

    if not request.user_flags.user_initiated_contact:
        return False

    if not request.user_flags.trusted_beneficiary:
        return False

    if not request.user_flags.user_confirms_identity_verified:
        return False

    if request.user_flags.first_time_beneficiary:
        return False

    return True


@router.post(
    "/assess", response_model=AssessmentResponse, dependencies=[Depends(verify_api_key)]
)
def assess_risk(
    request: AssessmentRequest,
    x_client_id: str = Header(default="anonymous"),
) -> AssessmentResponse:
    rate_limiter.check(x_client_id)

    previous_context = session_store.get(request.session_id)

    if previous_context is None:
        previous_context = SessionContext(stage_state=state_machine.initial_state())

    hybrid_result = HybridSignalPipeline().detect(
        request,
        repeat_contact_score=previous_context.repeat_contact_score,
        trusted_beneficiary_score=previous_context.trusted_beneficiary_score,
    )

    rule_signals = hybrid_result["rule_signals"]
    scam_probability = hybrid_result["scam_probability"]

    detected_stage = StageClassifier().classify(rule_signals)
    stage_state = state_machine.update(previous_context.stage_state, detected_stage)

    beneficiary_key = _build_beneficiary_key(request)

    repeat_contact_score = previous_context.repeat_contact_score
    trusted_beneficiary_score = previous_context.trusted_beneficiary_score
    safe_interaction_count = previous_context.safe_interaction_count

    if beneficiary_key and beneficiary_key == previous_context.last_beneficiary_key:
        repeat_contact_score += 1

    safe_payment_context = _is_safe_payment_context(
        request,
        detected_stage.value,
        scam_probability,
        rule_signals,
    )

    if safe_payment_context:
        safe_interaction_count += 1

    if safe_payment_context and beneficiary_key:
        trusted_beneficiary_score += 1

    benign_context_score = 0

    if request.user_flags.user_initiated_contact:
        benign_context_score += 1

    if request.user_flags.trusted_beneficiary:
        benign_context_score += 1

    if request.user_flags.user_confirms_identity_verified:
        benign_context_score += 1

    if not request.user_flags.first_time_beneficiary:
        benign_context_score += 1

    if repeat_contact_score > 0:
        benign_context_score += 1

    if trusted_beneficiary_score > 0:
        benign_context_score += 1

    updated_context = SessionContext(
        stage_state=stage_state,
        interaction_count=previous_context.interaction_count + 1,
        safe_interaction_count=safe_interaction_count,
        repeat_contact_score=repeat_contact_score,
        trusted_beneficiary_score=trusted_beneficiary_score,
        last_beneficiary_key=beneficiary_key,
        last_interaction_safe=safe_payment_context,
    )
    session_store.set(request.session_id, updated_context)

    risk_result = RiskEngine().evaluate(
        rule_signals,
        stage_state,
        scam_probability,
        benign_context_score=benign_context_score,
        safe_payment_context=safe_payment_context,
    )

    response = AssessmentResponse(
        request_id=str(uuid4()),
        session_id=request.session_id,
        risk_level=risk_result["risk_level"],
        risk_score=risk_result["risk_score"],
        current_stage=stage_state.current_stage,
        recommended_action=risk_result["recommended_action"],
        should_warn_user=risk_result["should_warn_user"],
        triggered_signals=rule_signals,
        stage_state=StageState(
            current_stage=stage_state.current_stage,
            completed_stages=stage_state.completed_stages,
        ),
        explanation=risk_result["explanation"],
    )

    write_audit_log(
        {
            "client_id": x_client_id,
            "session_id": request.session_id,
            "risk_level": response.risk_level.value,
            "risk_score": response.risk_score,
            "current_stage": response.current_stage.value,
            "signal_count": len(response.triggered_signals),
        }
    )

    return response
