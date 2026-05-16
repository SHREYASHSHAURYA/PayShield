from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_repeat_safe_interaction_gets_no_worse() -> None:
    first_payload = {
        "session_id": "safe-repeat-demo",
        "device_timestamp": datetime.utcnow().isoformat(),
        "locale": "en-IN",
        "interaction_events": [
            {
                "event_id": "e1",
                "timestamp": datetime.utcnow().isoformat(),
                "interaction_type": "text_message",
                "content_text": "Dinner bill split is 500 INR. Send when free.",
                "source_label": "sms",
                "metadata": {},
            }
        ],
        "payment_context": {
            "payment_method": "upi_id",
            "payment_direction": "send",
            "amount": 500.0,
            "currency": "INR",
            "upi_id": "friend@bank",
            "collect_request_present": False,
            "qr_present": False,
            "payment_link_present": False,
            "merchant_name": None,
            "note": None,
        },
        "user_flags": {
            "user_expects_money": False,
            "user_initiated_contact": True,
            "trusted_beneficiary": True,
            "first_time_beneficiary": False,
            "user_confirms_pressure": False,
            "user_confirms_identity_verified": True,
        },
    }

    second_payload = {
        "session_id": "safe-repeat-demo",
        "device_timestamp": datetime.utcnow().isoformat(),
        "locale": "en-IN",
        "interaction_events": [
            {
                "event_id": "e2",
                "timestamp": datetime.utcnow().isoformat(),
                "interaction_type": "text_message",
                "content_text": "Send me the same 500 for dinner bill split when free.",
                "source_label": "sms",
                "metadata": {},
            }
        ],
        "payment_context": {
            "payment_method": "upi_id",
            "payment_direction": "send",
            "amount": 500.0,
            "currency": "INR",
            "upi_id": "friend@bank",
            "collect_request_present": False,
            "qr_present": False,
            "payment_link_present": False,
            "merchant_name": None,
            "note": None,
        },
        "user_flags": {
            "user_expects_money": False,
            "user_initiated_contact": True,
            "trusted_beneficiary": True,
            "first_time_beneficiary": False,
            "user_confirms_pressure": False,
            "user_confirms_identity_verified": True,
        },
    }

    first_response = client.post("/api/v1/risk/assess", json=first_payload)
    second_response = client.post("/api/v1/risk/assess", json=second_payload)

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_data["risk_score"] <= first_data["risk_score"]
