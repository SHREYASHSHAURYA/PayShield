from typing import List

from app.models.enums import RecommendedAction, RiskLevel, ScamStage, SignalType
from app.schemas.assessment import StageState, TriggeredSignal


class RiskEngine:
    _signal_weights = {
        SignalType.URGENCY: 10,
        SignalType.IMPERSONATION: 14,
        SignalType.AUTHORITY_CLAIM: 8,
        SignalType.REWARD_BAIT: 7,
        SignalType.FEAR_PRESSURE: 12,
        SignalType.SECRECY_REQUEST: 12,
        SignalType.QR_PAYMENT_PROMPT: 16,
        SignalType.UPI_ID_SHARED: 10,
        SignalType.COLLECT_REQUEST_DETECTED: 18,
        SignalType.PAYMENT_LINK_SHARED: 14,
        SignalType.REMOTE_APP_REQUEST: 20,
        SignalType.REFUND_CLAIM: 9,
        SignalType.JOB_OFFER: 8,
        SignalType.KYC_CLAIM: 10,
        SignalType.ACCOUNT_BLOCK_CLAIM: 12,
        SignalType.PAYMENT_REQUEST: 15,
        SignalType.TRANSACTION_CONFIRMATION_REQUEST: 18,
    }

    _stage_bonus = {
        ScamStage.TRUST: 0,
        ScamStage.URGENCY: 10,
        ScamStage.PAYMENT: 20,
        ScamStage.EXTRACTION: 30,
    }

    def evaluate(
        self,
        signals: List[TriggeredSignal],
        stage_state: StageState,
        scam_probability: float = 0.0,
    ) -> dict:
        score = self._calculate_score(
            signals, stage_state.current_stage, scam_probability
        )
        risk_level = self._map_risk_level(score)
        recommended_action = self._map_recommended_action(risk_level)
        explanation = self._build_explanation(
            signals,
            stage_state.current_stage,
            score,
            risk_level,
            scam_probability,
        )

        return {
            "risk_score": score,
            "risk_level": risk_level,
            "recommended_action": recommended_action,
            "should_warn_user": risk_level
            in {RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL},
            "explanation": explanation,
        }

    def _calculate_score(
        self,
        signals: List[TriggeredSignal],
        current_stage: ScamStage,
        scam_probability: float,
    ) -> int:
        signal_score = 0

        for signal in signals:
            weight = self._signal_weights.get(signal.signal_type, 0)
            signal_score += round(weight * signal.confidence)

        ml_bonus = round(20 * scam_probability)
        total_score = signal_score + self._stage_bonus[current_stage] + ml_bonus

        if total_score > 100:
            return 100

        return total_score

    def _map_risk_level(self, score: int) -> RiskLevel:
        if score <= 24:
            return RiskLevel.LOW
        if score <= 49:
            return RiskLevel.MEDIUM
        if score <= 74:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL

    def _map_recommended_action(self, risk_level: RiskLevel) -> RecommendedAction:
        if risk_level == RiskLevel.LOW:
            return RecommendedAction.SAFE_TO_CONTINUE
        if risk_level == RiskLevel.MEDIUM:
            return RecommendedAction.WARN_ONLY
        if risk_level == RiskLevel.HIGH:
            return RecommendedAction.REQUIRE_EXTRA_CONFIRMATION
        return RecommendedAction.RECOMMEND_ABORT

    def _build_explanation(
        self,
        signals: List[TriggeredSignal],
        current_stage: ScamStage,
        score: int,
        risk_level: RiskLevel,
        scam_probability: float,
    ) -> List[str]:
        explanation = [
            f"Current scam progression stage is '{current_stage.value}'.",
            f"Overall risk score is {score}, mapped to '{risk_level.value}' risk.",
            f"ML scam probability is {scam_probability:.4f}.",
        ]

        for signal in signals[:5]:
            explanation.append(
                f"Detected signal '{signal.signal_type.value}' because {signal.evidence.lower()}."
            )

        return explanation
