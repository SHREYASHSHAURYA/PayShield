from datetime import datetime

from app.models.enums import (
    InteractionType,
    PaymentDirection,
    PaymentMethodType,
    ScamStage,
)
from app.schemas.assessment import (
    AssessmentRequest,
    InteractionEvent,
    PaymentContext,
    UserFlags,
)
from app.services.signal_engine import RuleBasedSignalDetector
from app.services.stage_engine import StageClassifier


def build_request(message: str) -> AssessmentRequest:
    return AssessmentRequest(
        session_id="test-session",
        device_timestamp=datetime.utcnow(),
        interaction_events=[
            InteractionEvent(
                event_id="e1",
                timestamp=datetime.utcnow(),
                interaction_type=InteractionType.TEXT_MESSAGE,
                content_text=message,
                source_label="sms",
                metadata={},
            )
        ],
        payment_context=PaymentContext(
            payment_method=PaymentMethodType.QR_CODE,
            payment_direction=PaymentDirection.SEND,
            amount=500,
            currency="INR",
            upi_id=None,
            collect_request_present=False,
            qr_present=True,
            payment_link_present=False,
            merchant_name=None,
            note=None,
        ),
        user_flags=UserFlags(),
    )


def test_rule_detector_finds_expected_signals() -> None:
    request = build_request(
        "I am from bank customer care. Your account will be blocked. Scan this QR and pay now urgently."
    )

    signals = RuleBasedSignalDetector().detect(request)
    signal_types = {signal.signal_type.value for signal in signals}

    assert "urgency" in signal_types
    assert "impersonation" in signal_types
    assert "qr_payment_prompt" in signal_types
    assert "account_block_claim" in signal_types
    assert "payment_request" in signal_types


def test_stage_classifier_returns_payment_stage() -> None:
    request = build_request(
        "I am from bank customer care. Your account will be blocked. Scan this QR and pay now urgently."
    )

    signals = RuleBasedSignalDetector().detect(request)
    stage = StageClassifier().classify(signals)

    assert stage == ScamStage.PAYMENT
