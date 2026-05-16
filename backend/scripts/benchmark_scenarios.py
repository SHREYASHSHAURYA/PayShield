from datetime import datetime
from pathlib import Path
import json
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.models.enums import InteractionType, PaymentDirection, PaymentMethodType
from app.schemas.assessment import (
    AssessmentRequest,
    InteractionEvent,
    PaymentContext,
    UserFlags,
    StageState,
)
from app.services.ml_engine import HybridSignalPipeline
from app.services.risk_engine import RiskEngine
from app.services.stage_engine import StageClassifier


def build_request(
    session_id: str,
    message: str,
    interaction_type: InteractionType,
    payment_method: PaymentMethodType,
    payment_direction: PaymentDirection,
    amount: float | None,
    upi_id: str | None = None,
    qr_present: bool = False,
    collect_request_present: bool = False,
    payment_link_present: bool = False,
    user_initiated_contact: bool = False,
    trusted_beneficiary: bool = False,
    first_time_beneficiary: bool = True,
    user_confirms_identity_verified: bool = False,
) -> AssessmentRequest:
    return AssessmentRequest(
        session_id=session_id,
        device_timestamp=datetime.utcnow(),
        interaction_events=[
            InteractionEvent(
                event_id="e1",
                timestamp=datetime.utcnow(),
                interaction_type=interaction_type,
                content_text=message,
                source_label="benchmark",
                metadata={},
            )
        ],
        payment_context=PaymentContext(
            payment_method=payment_method,
            payment_direction=payment_direction,
            amount=amount,
            currency="INR",
            upi_id=upi_id,
            collect_request_present=collect_request_present,
            qr_present=qr_present,
            payment_link_present=payment_link_present,
            merchant_name=None,
            note=None,
        ),
        user_flags=UserFlags(
            user_expects_money=False,
            user_initiated_contact=user_initiated_contact,
            trusted_beneficiary=trusted_beneficiary,
            first_time_beneficiary=first_time_beneficiary,
            user_confirms_pressure=False,
            user_confirms_identity_verified=user_confirms_identity_verified,
        ),
    )


def evaluate(request: AssessmentRequest) -> dict:
    hybrid = HybridSignalPipeline().detect(request)
    stage = StageClassifier().classify(hybrid["rule_signals"])
    result = RiskEngine().evaluate(
        hybrid["rule_signals"],
        StageState(current_stage=stage, completed_stages=[]),
        hybrid["scam_probability"],
    )

    return {
        "session_id": request.session_id,
        "message": request.interaction_events[0].content_text,
        "signal_types": [signal.signal_type.value for signal in hybrid["rule_signals"]],
        "scam_probability": round(hybrid["scam_probability"], 4),
        "stage": stage.value,
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"].value,
        "recommended_action": result["recommended_action"].value,
    }


def main() -> None:
    scenarios = [
        build_request(
            session_id="bench-1",
            message="I am from bank customer care. Your account will be blocked. Scan this QR and pay now urgently.",
            interaction_type=InteractionType.TEXT_MESSAGE,
            payment_method=PaymentMethodType.QR_CODE,
            payment_direction=PaymentDirection.SEND,
            amount=500.0,
            qr_present=True,
        ),
        build_request(
            session_id="bench-2",
            message="Your refund is pending. Approve the collect request to receive your money.",
            interaction_type=InteractionType.TEXT_MESSAGE,
            payment_method=PaymentMethodType.COLLECT_REQUEST,
            payment_direction=PaymentDirection.RECEIVE,
            amount=1200.0,
            collect_request_present=True,
        ),
        build_request(
            session_id="bench-3",
            message="Jaldi account block ho jayega. QR scan karo aur paise bhejo.",
            interaction_type=InteractionType.TEXT_MESSAGE,
            payment_method=PaymentMethodType.QR_CODE,
            payment_direction=PaymentDirection.SEND,
            amount=500.0,
            qr_present=True,
        ),
        build_request(
            session_id="bench-4",
            message="Dinner bill split is 500 INR. Send when free.",
            interaction_type=InteractionType.TEXT_MESSAGE,
            payment_method=PaymentMethodType.UPI_ID,
            payment_direction=PaymentDirection.SEND,
            amount=500.0,
            upi_id="friend@bank",
            user_initiated_contact=True,
            trusted_beneficiary=True,
            first_time_beneficiary=False,
            user_confirms_identity_verified=True,
        ),
    ]

    results = [evaluate(scenario) for scenario in scenarios]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
