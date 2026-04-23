from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "PayShield"}


def test_assess_endpoint_returns_expected_shape() -> None:
    payload = {
        "session_id": "demo-session-1",
        "device_timestamp": datetime.utcnow().isoformat(),
        "locale": "en-IN",
        "interaction_events": [
            {
                "event_id": "e1",
                "timestamp": datetime.utcnow().isoformat(),
                "interaction_type": "text_message",
                "content_text": "I am from bank customer care. Your account will be blocked. Scan this QR and pay now urgently.",
                "source_label": "sms",
                "metadata": {},
            }
        ],
        "payment_context": {
            "payment_method": "qr_code",
            "payment_direction": "send",
            "amount": 500.0,
            "currency": "INR",
            "upi_id": None,
            "collect_request_present": False,
            "qr_present": True,
            "payment_link_present": False,
            "merchant_name": None,
            "note": None,
        },
        "user_flags": {
            "user_expects_money": False,
            "user_initiated_contact": False,
            "trusted_beneficiary": False,
            "first_time_beneficiary": True,
            "user_confirms_pressure": False,
            "user_confirms_identity_verified": False,
        },
    }

    response = client.post("/api/v1/risk/assess", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["risk_level"] == "critical"
    assert data["current_stage"] == "payment"
    assert data["recommended_action"] == "recommend_abort"
    assert data["should_warn_user"] is True
    assert isinstance(data["risk_score"], int)
    assert isinstance(data["triggered_signals"], list)
    assert isinstance(data["explanation"], list)
