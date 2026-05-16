import re
from typing import Iterable

import pandas as pd

from app.schemas.assessment import AssessmentRequest
from app.utils.text_normalizer import normalize_text

UPI_PATTERN = re.compile(r"\b[a-z0-9.\-_]{2,}@[a-z]{2,}\b")
LINK_PATTERN = re.compile(
    r"(https?://\S+)|(paytm\.me/\S+)|(phon\.pe/\S+)|(gpay\.app\.goo\.gl/\S+)"
)
AMOUNT_PATTERN = re.compile(r"\b\d{2,6}(?:\.\d{1,2})?\b")

URGENCY_TERMS = (
    "urgent",
    "immediately",
    "right now",
    "asap",
    "hurry",
    "blocked",
    "suspended",
    "penalty",
    "legal action",
)

QR_TERMS = (
    "scan this qr",
    "scan qr",
    "qr code",
    "scan the code",
)

COLLECT_TERMS = (
    "collect request",
    "approve the request",
    "mandate request",
    "approve collect request",
)

SEND_TERMS = (
    "pay now",
    "send money",
    "transfer money",
    "make payment",
    "complete the transaction",
)

RECEIVE_TERMS = (
    "receive money",
    "refund",
    "cashback",
    "claim reward",
)

IMPERSONATION_TERMS = (
    "bank customer care",
    "customer care",
    "support executive",
    "police",
    "cyber cell",
    "government officer",
)

REMOTE_ACCESS_TERMS = (
    "anydesk",
    "teamviewer",
    "quicksupport",
    "remote access",
)


def _contains_any(text: str, patterns: Iterable[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def _extract_amount_score(text: str) -> float:
    matches = AMOUNT_PATTERN.findall(text)
    if not matches:
        return 0.0

    amounts = [float(match) for match in matches]
    amount = max(amounts)

    if amount >= 10000:
        return 1.0
    if amount >= 5000:
        return 0.75
    if amount >= 1000:
        return 0.5
    if amount >= 100:
        return 0.25
    return 0.0


def _features_from_text(text: str) -> dict:
    normalized = normalize_text(text)

    return {
        "text": normalized,
        "amount_score": _extract_amount_score(normalized),
        "qr_present": int(_contains_any(normalized, QR_TERMS)),
        "collect_request_present": int(_contains_any(normalized, COLLECT_TERMS)),
        "payment_link_present": int(bool(LINK_PATTERN.search(normalized))),
        "upi_present": int(bool(UPI_PATTERN.search(normalized))),
        "send_direction": int(_contains_any(normalized, SEND_TERMS)),
        "receive_direction": int(_contains_any(normalized, RECEIVE_TERMS)),
        "pressure_flag": int(_contains_any(normalized, URGENCY_TERMS)),
        "impersonation_flag": int(_contains_any(normalized, IMPERSONATION_TERMS)),
        "remote_access_flag": int(_contains_any(normalized, REMOTE_ACCESS_TERMS)),
    }


def build_training_frame(texts: pd.Series) -> pd.DataFrame:
    rows = [_features_from_text(str(text)) for text in texts.fillna("")]
    return pd.DataFrame(rows)


def build_runtime_frame(request: AssessmentRequest) -> pd.DataFrame:
    text_parts = []

    for event in request.interaction_events:
        if event.content_text:
            text_parts.append(event.content_text)

    if request.payment_context.upi_id:
        text_parts.append(request.payment_context.upi_id)

    if request.payment_context.note:
        text_parts.append(request.payment_context.note)

    combined_text = " ".join(text_parts)
    derived = _features_from_text(combined_text)

    amount_score = derived["amount_score"]
    if request.payment_context.amount is not None:
        amount = float(request.payment_context.amount)
        if amount >= 10000:
            amount_score = 1.0
        elif amount >= 5000:
            amount_score = 0.75
        elif amount >= 1000:
            amount_score = 0.5
        elif amount >= 100:
            amount_score = 0.25
        else:
            amount_score = 0.0

    row = {
        "text": derived["text"],
        "amount_score": amount_score,
        "qr_present": int(derived["qr_present"] or request.payment_context.qr_present),
        "collect_request_present": int(
            derived["collect_request_present"]
            or request.payment_context.collect_request_present
        ),
        "payment_link_present": int(
            derived["payment_link_present"]
            or request.payment_context.payment_link_present
        ),
        "upi_present": int(
            derived["upi_present"] or bool(request.payment_context.upi_id)
        ),
        "send_direction": int(
            derived["send_direction"]
            or request.payment_context.payment_direction.value == "send"
        ),
        "receive_direction": int(
            derived["receive_direction"]
            or request.payment_context.payment_direction.value == "receive"
        ),
        "pressure_flag": int(
            derived["pressure_flag"] or request.user_flags.user_confirms_pressure
        ),
        "impersonation_flag": int(derived["impersonation_flag"]),
        "remote_access_flag": int(derived["remote_access_flag"]),
    }

    return pd.DataFrame([row])
