from datetime import datetime

from app.models.enums import InteractionType, PaymentDirection, PaymentMethodType
from app.schemas.assessment import (
    AssessmentRequest,
    InteractionEvent,
    PaymentContext,
    UserFlags,
)
from app.services.signal_engine import RuleBasedSignalDetector
from app.utils.qr_parser import parse_qr_payload
from app.utils.text_normalizer import normalize_text


def test_text_normalizer_maps_romanized_hindi() -> None:
    normalized = normalize_text(
        "Jaldi account block ho jayega. QR scan karo aur paise bhejo."
    )
    assert "urgent" in normalized
    assert "account will be blocked" in normalized
    assert "scan qr" in normalized
    assert "send money" in normalized


def test_qr_parser_extracts_upi_fields() -> None:
    parsed = parse_qr_payload(
        "upi://pay?pa=merchant@upi&pn=Demo%20Store&am=499.00&tn=Payment"
    )
    assert parsed["upi_id"] == "merchant@upi"
    assert parsed["merchant_name"] == "Demo Store"
    assert parsed["amount"] == "499.00"
    assert parsed["note"] == "Payment"


def test_rule_detector_uses_qr_metadata() -> None:
    request = AssessmentRequest(
        session_id="qr-demo",
        device_timestamp=datetime.utcnow(),
        interaction_events=[
            InteractionEvent(
                event_id="e1",
                timestamp=datetime.utcnow(),
                interaction_type=InteractionType.QR_SCAN,
                content_text="",
                source_label="camera",
                metadata={
                    "qr_payload": "upi://pay?pa=merchant@upi&pn=Demo%20Store&am=499.00&tn=Payment"
                },
            )
        ],
        payment_context=PaymentContext(
            payment_method=PaymentMethodType.QR_CODE,
            payment_direction=PaymentDirection.SEND,
            amount=499,
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

    signals = RuleBasedSignalDetector().detect(request)
    signal_types = {signal.signal_type.value for signal in signals}

    assert "qr_payment_prompt" in signal_types
    assert "upi_id_shared" in signal_types
