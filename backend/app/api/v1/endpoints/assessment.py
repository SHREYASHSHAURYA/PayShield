from uuid import uuid4

from fastapi import APIRouter

from app.schemas.assessment import AssessmentRequest, AssessmentResponse, StageState
from app.services.ml_engine import HybridSignalPipeline
from app.services.risk_engine import RiskEngine
from app.services.stage_engine import StageClassifier
from app.services.state_machine import ScamStateMachine


router = APIRouter()


@router.post("/assess", response_model=AssessmentResponse)
def assess_risk(request: AssessmentRequest) -> AssessmentResponse:
    hybrid_result = HybridSignalPipeline().detect(request)
    rule_signals = hybrid_result["rule_signals"]
    scam_probability = hybrid_result["scam_probability"]

    current_stage = StageClassifier().classify(rule_signals)
    state_machine = ScamStateMachine()
    stage_state = state_machine.update(state_machine.initial_state(), current_stage)

    risk_result = RiskEngine().evaluate(
        rule_signals,
        stage_state,
        scam_probability,
    )

    return AssessmentResponse(
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
