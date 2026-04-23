from app.models.enums import RecommendedAction, RiskLevel, ScamStage, SignalType
from app.schemas.assessment import StageState, TriggeredSignal
from app.services.risk_engine import RiskEngine
from app.services.state_machine import ScamStateMachine


def test_state_machine_preserves_progression() -> None:
    machine = ScamStateMachine()

    state = machine.initial_state()
    state = machine.update(state, ScamStage.URGENCY)
    state = machine.update(state, ScamStage.PAYMENT)
    state = machine.update(state, ScamStage.TRUST)

    assert state.current_stage == ScamStage.PAYMENT
    assert state.completed_stages == [ScamStage.TRUST, ScamStage.URGENCY]


def test_risk_engine_returns_critical_for_high_risk_scenario() -> None:
    signals = [
        TriggeredSignal(
            signal_type=SignalType.URGENCY,
            confidence=0.78,
            source_event_id="e1",
            evidence="Urgency language detected in interaction content",
        ),
        TriggeredSignal(
            signal_type=SignalType.IMPERSONATION,
            confidence=0.82,
            source_event_id="e1",
            evidence="Impersonation pattern detected in interaction content",
        ),
        TriggeredSignal(
            signal_type=SignalType.QR_PAYMENT_PROMPT,
            confidence=0.90,
            source_event_id="e1",
            evidence="QR payment prompt detected in interaction content",
        ),
        TriggeredSignal(
            signal_type=SignalType.ACCOUNT_BLOCK_CLAIM,
            confidence=0.83,
            source_event_id="e1",
            evidence="Account blocking claim detected in interaction content",
        ),
        TriggeredSignal(
            signal_type=SignalType.PAYMENT_REQUEST,
            confidence=0.80,
            source_event_id="e1",
            evidence="Payment request detected in interaction content",
        ),
    ]

    result = RiskEngine().evaluate(
        signals=signals,
        stage_state=StageState(
            current_stage=ScamStage.PAYMENT,
            completed_stages=[ScamStage.TRUST, ScamStage.URGENCY],
        ),
        scam_probability=0.6659,
    )

    assert result["risk_level"] == RiskLevel.CRITICAL
    assert result["recommended_action"] == RecommendedAction.RECOMMEND_ABORT
    assert result["risk_score"] >= 75
    assert result["should_warn_user"] is True
