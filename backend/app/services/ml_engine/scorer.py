from pathlib import Path

import joblib

from app.schemas.assessment import AssessmentRequest


class MLSignalScorer:
    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parents[3]
        model_path = base_dir / "models_store" / "scam_text_pipeline.joblib"
        self.model = joblib.load(model_path)

    def score(self, request: AssessmentRequest) -> float:
        text = self._build_text(request)
        model_probability = float(self.model.predict_proba([text])[0][1])
        context_bonus = self._context_bonus(request)
        probability = model_probability + context_bonus

        if probability < 0.0:
            return 0.0
        if probability > 1.0:
            return 1.0
        return probability

    def _build_text(self, request: AssessmentRequest) -> str:
        parts = []

        for event in request.interaction_events:
            if event.content_text:
                parts.append(event.content_text.strip().lower())

        if request.payment_context.upi_id:
            parts.append(request.payment_context.upi_id.strip().lower())

        if request.payment_context.note:
            parts.append(request.payment_context.note.strip().lower())

        return " ".join(parts)

    def _context_bonus(self, request: AssessmentRequest) -> float:
        bonus = 0.0
        payment = request.payment_context
        flags = request.user_flags

        if payment.amount is not None:
            amount = float(payment.amount)
            if amount >= 10000:
                bonus += 0.06
            elif amount >= 5000:
                bonus += 0.04
            elif amount >= 1000:
                bonus += 0.02

        if payment.qr_present:
            bonus += 0.05

        if payment.collect_request_present:
            bonus += 0.10

        if payment.payment_link_present:
            bonus += 0.06

        if payment.payment_direction.value == "send":
            bonus += 0.03

        if payment.upi_id:
            bonus += 0.01

        if flags.user_confirms_pressure:
            bonus += 0.10

        if not flags.user_initiated_contact:
            bonus += 0.04

        if not flags.user_confirms_identity_verified:
            bonus += 0.04

        if flags.first_time_beneficiary:
            bonus += 0.03

        if flags.trusted_beneficiary:
            bonus -= 0.15

        if flags.user_expects_money and payment.payment_direction.value == "receive":
            bonus -= 0.10

        if flags.user_initiated_contact:
            bonus -= 0.05

        if flags.user_confirms_identity_verified:
            bonus -= 0.05

        return bonus
