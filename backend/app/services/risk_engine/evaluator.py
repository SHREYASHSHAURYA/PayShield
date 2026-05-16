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
        SignalType.UPI_ID_SHARED: 3,
        SignalType.COLLECT_REQUEST_DETECTED: 18,
        SignalType.PAYMENT_LINK_SHARED: 14,
        SignalType.REMOTE_APP_REQUEST: 20,
        SignalType.REFUND_CLAIM: 9,
        SignalType.JOB_OFFER: 8,
        SignalType.KYC_CLAIM: 10,
        SignalType.ACCOUNT_BLOCK_CLAIM: 12,
        SignalType.PAYMENT_REQUEST: 3,
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
        benign_context_score: int = 0,
        safe_payment_context: bool = False,
    ) -> dict:
        score = self._calculate_score(
            signals,
            stage_state.current_stage,
            scam_probability,
            benign_context_score,
            safe_payment_context,
        )
        risk_level = self._map_risk_level(score)
        recommended_action = self._map_recommended_action(risk_level)
        explanation = self._build_explanation(
            signals,
            stage_state,
            score,
            risk_level,
            scam_probability,
            benign_context_score,
            safe_payment_context,
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
        benign_context_score: int,
        safe_payment_context: bool,
    ) -> int:
        signal_score = 0

        for signal in signals:
            weight = self._signal_weights.get(signal.signal_type, 0)
            signal_score += round(weight * signal.confidence)

        ml_bonus = round(20 * scam_probability)
        stage_bonus = self._stage_bonus[current_stage]

        if safe_payment_context and current_stage == ScamStage.PAYMENT:
            stage_bonus = 8

        benign_discount = min(benign_context_score, 4) * 3
        total_score = signal_score + stage_bonus + ml_bonus - benign_discount

        if safe_payment_context:
            total_score = max(total_score, 12)

        if total_score < 0:
            return 0
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
        stage_state: StageState,
        score: int,
        risk_level: RiskLevel,
        scam_probability: float,
        benign_context_score: int,
        safe_payment_context: bool,
    ) -> List[str]:
        explanation = [
            f"Current scam progression stage is '{stage_state.current_stage.value}'.",
            f"Overall risk score is {score}, mapped to '{risk_level.value}' risk.",
            f"ML scam probability is {scam_probability:.4f}.",
            self._describe_uncertainty(scam_probability),
            self._describe_stage_context(stage_state, safe_payment_context),
            self._describe_signal_strength(signals, safe_payment_context),
        ]

        if benign_context_score > 0:
            explanation.append(
                f"Trusted or repeated benign context reduced the final score by {min(benign_context_score, 4) * 3} points."
            )

        if safe_payment_context:
            explanation.append(
                "This matched a likely benign payment context, so payment-stage risk was reduced."
            )

        sorted_signals = sorted(signals, key=lambda item: item.confidence, reverse=True)

        for signal in sorted_signals[:5]:
            explanation.append(self._describe_signal(signal, safe_payment_context))

        return explanation

    def _describe_uncertainty(self, scam_probability: float) -> str:
        if scam_probability >= 0.85:
            return "ML confidence is very high and strongly supports scam suspicion."
        if scam_probability >= 0.65:
            return "ML confidence is high and supports scam suspicion."
        if scam_probability >= 0.40:
            return "ML confidence is moderate, so the result should be interpreted with caution."
        return "ML confidence is low, so rule-based indicators are more important for this result."

    def _describe_stage_context(
        self, stage_state: StageState, safe_payment_context: bool
    ) -> str:
        if safe_payment_context:
            return "This session currently looks more like a normal payment flow than a scam progression flow."

        completed = ", ".join(stage.value for stage in stage_state.completed_stages)

        if completed:
            return (
                f"Completed progression stages before the current state: {completed}."
            )
        return (
            "No prior completed scam progression stages are recorded for this session."
        )

    def _describe_signal_strength(
        self,
        signals: List[TriggeredSignal],
        safe_payment_context: bool,
    ) -> str:
        if not signals:
            return "No explicit scam signals were detected."

        benign_only_signals = {"upi_id_shared", "payment_request"}
        signal_types = {signal.signal_type.value for signal in signals}

        if safe_payment_context and signal_types.issubset(benign_only_signals):
            return "Only routine payment-context indicators were detected."

        high_confidence_count = sum(1 for signal in signals if signal.confidence >= 0.8)

        if high_confidence_count >= 3:
            return "Multiple high-confidence scam indicators were detected."
        if high_confidence_count >= 1:
            return "At least one high-confidence scam indicator was detected."
        return "Signals were detected, but most of them are moderate-confidence indicators."

    def _describe_signal(
        self, signal: TriggeredSignal, safe_payment_context: bool
    ) -> str:
        if safe_payment_context and signal.signal_type == SignalType.UPI_ID_SHARED:
            return "Detected payment-context signal 'upi_id_shared' from the provided UPI details."

        if safe_payment_context and signal.signal_type == SignalType.PAYMENT_REQUEST:
            return "Detected payment-context signal 'payment_request' because this flow involves sending money."

        return f"Detected signal '{signal.signal_type.value}' because {signal.evidence.lower()}."
