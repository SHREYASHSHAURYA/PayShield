import re

import joblib

from app.core import settings
from app.schemas.assessment import AssessmentRequest
from app.services.ml_engine.features import build_runtime_frame

SAFE_PAYMENT_PATTERNS = (
    "split bill",
    "send when free",
    "when free",
    "dinner bill",
    "lunch bill",
    "rent share",
    "share of",
    "for groceries",
    "for tickets",
)

SCAM_PRESSURE_PATTERNS = (
    "account will be blocked",
    "scan this qr",
    "approve the request",
    "collect request",
    "urgent",
    "immediately",
    "customer care",
    "bank customer care",
    "anydesk",
    "teamviewer",
)


class MLSignalScorer:
    def __init__(self) -> None:
        self.model = joblib.load(settings.model_path)

    def score(
        self,
        request: AssessmentRequest,
        repeat_contact_score: int = 0,
        trusted_beneficiary_score: int = 0,
    ) -> float:
        features = build_runtime_frame(request)
        probability = float(self.model.predict_proba(features)[0][1])
        calibrated = self._calibrate(
            probability,
            request,
            repeat_contact_score,
            trusted_beneficiary_score,
        )

        if calibrated < 0.0:
            return 0.0
        if calibrated > 1.0:
            return 1.0
        return calibrated

    def _calibrate(
        self,
        probability: float,
        request: AssessmentRequest,
        repeat_contact_score: int,
        trusted_beneficiary_score: int,
    ) -> float:
        text = self._build_text(request)
        lowered = re.sub(r"\s+", " ", text.strip().lower())
        flags = request.user_flags
        payment = request.payment_context

        if any(pattern in lowered for pattern in SCAM_PRESSURE_PATTERNS):
            probability += 0.03

        safe_pattern_found = any(
            pattern in lowered for pattern in SAFE_PAYMENT_PATTERNS
        )

        if safe_pattern_found:
            probability -= 0.30

        if flags.user_initiated_contact:
            probability -= 0.10

        if flags.trusted_beneficiary:
            probability -= 0.22

        if flags.user_confirms_identity_verified:
            probability -= 0.10

        if not flags.first_time_beneficiary:
            probability -= 0.12

        if payment.payment_direction.value == "receive" and flags.user_expects_money:
            probability -= 0.06

        if payment.qr_present:
            probability += 0.04

        if payment.collect_request_present:
            probability += 0.08

        probability -= min(repeat_contact_score, 3) * 0.06
        probability -= min(trusted_beneficiary_score, 3) * 0.08

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
