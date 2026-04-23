import re
from typing import List, Optional

from app.models.enums import (
    InteractionType,
    PaymentDirection,
    PaymentMethodType,
    SignalType,
)
from app.schemas.assessment import AssessmentRequest, InteractionEvent, TriggeredSignal


class RuleBasedSignalDetector:
    def detect(self, request: AssessmentRequest) -> List[TriggeredSignal]:
        signals: List[TriggeredSignal] = []

        for event in request.interaction_events:
            text = self._normalize_text(event.content_text)

            if self._contains_any(
                text,
                [
                    "urgent",
                    "immediately",
                    "right now",
                    "asap",
                    "within minutes",
                    "do it now",
                    "hurry",
                    "jaldi",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.URGENCY,
                        0.78,
                        event.event_id,
                        "Urgency language detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "bank manager",
                    "customer care",
                    "support executive",
                    "police",
                    "cyber cell",
                    "income tax",
                    "electricity board",
                    "courier office",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.IMPERSONATION,
                        0.82,
                        event.event_id,
                        "Impersonation pattern detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "official",
                    "verified team",
                    "government officer",
                    "senior officer",
                    "authority instruction",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.AUTHORITY_CLAIM,
                        0.74,
                        event.event_id,
                        "Authority claim detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "reward",
                    "cashback",
                    "gift",
                    "prize",
                    "lottery",
                    "bonus",
                    "free money",
                    "offer unlocked",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.REWARD_BAIT,
                        0.72,
                        event.event_id,
                        "Reward or bait language detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "account blocked",
                    "account frozen",
                    "kyc suspended",
                    "sim blocked",
                    "penalty",
                    "legal action",
                    "complaint filed",
                    "police case",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.FEAR_PRESSURE,
                        0.81,
                        event.event_id,
                        "Fear or threat language detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "do not tell anyone",
                    "keep this secret",
                    "confidential",
                    "only you should do this",
                    "don't inform family",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.SECRECY_REQUEST,
                        0.84,
                        event.event_id,
                        "Secrecy request detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "scan this qr",
                    "scan qr",
                    "pay by qr",
                    "receive money by scanning qr",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.QR_PAYMENT_PROMPT,
                        0.9,
                        event.event_id,
                        "QR payment prompt detected in interaction content",
                    )
                )

            if self._contains_upi_id(text):
                signals.append(
                    self._build_signal(
                        SignalType.UPI_ID_SHARED,
                        0.88,
                        event.event_id,
                        "UPI ID pattern detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "collect request",
                    "approve the request",
                    "accept collect request",
                    "mandate request",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.COLLECT_REQUEST_DETECTED,
                        0.9,
                        event.event_id,
                        "Collect request language detected in interaction content",
                    )
                )

            if self._contains_payment_link(text):
                signals.append(
                    self._build_signal(
                        SignalType.PAYMENT_LINK_SHARED,
                        0.85,
                        event.event_id,
                        "Payment link detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "anydesk",
                    "teamviewer",
                    "quicksupport",
                    "screen share app",
                    "remote access app",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.REMOTE_APP_REQUEST,
                        0.92,
                        event.event_id,
                        "Remote access app request detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "refund",
                    "chargeback",
                    "return your money",
                    "refund processing",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.REFUND_CLAIM,
                        0.76,
                        event.event_id,
                        "Refund claim detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "part time job",
                    "work from home",
                    "task commission",
                    "rating task",
                    "job payout",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.JOB_OFFER,
                        0.73,
                        event.event_id,
                        "Job or task scam pattern detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "complete kyc",
                    "update kyc",
                    "re-kyc",
                    "kyc verification",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.KYC_CLAIM,
                        0.8,
                        event.event_id,
                        "KYC claim detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "account will be blocked",
                    "upi will stop",
                    "wallet blocked",
                    "bank account suspended",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.ACCOUNT_BLOCK_CLAIM,
                        0.83,
                        event.event_id,
                        "Account blocking claim detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "send payment",
                    "pay now",
                    "make payment",
                    "transfer money",
                    "complete the transaction",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.PAYMENT_REQUEST,
                        0.8,
                        event.event_id,
                        "Payment request detected in interaction content",
                    )
                )

            if self._contains_any(
                text,
                [
                    "enter otp",
                    "approve the payment",
                    "confirm the transaction",
                    "authorize the payment",
                    "tap approve",
                ],
            ):
                signals.append(
                    self._build_signal(
                        SignalType.TRANSACTION_CONFIRMATION_REQUEST,
                        0.86,
                        event.event_id,
                        "Transaction confirmation request detected in interaction content",
                    )
                )

            if event.interaction_type == InteractionType.QR_SCAN:
                signals.append(
                    self._build_signal(
                        SignalType.QR_PAYMENT_PROMPT,
                        0.87,
                        event.event_id,
                        "QR scan interaction detected",
                    )
                )

            if event.interaction_type == InteractionType.COLLECT_REQUEST:
                signals.append(
                    self._build_signal(
                        SignalType.COLLECT_REQUEST_DETECTED,
                        0.95,
                        event.event_id,
                        "Collect request interaction detected",
                    )
                )

            if event.interaction_type == InteractionType.PAYMENT_LINK:
                signals.append(
                    self._build_signal(
                        SignalType.PAYMENT_LINK_SHARED,
                        0.9,
                        event.event_id,
                        "Payment link interaction detected",
                    )
                )

            if event.interaction_type == InteractionType.UPI_ID_ENTRY:
                signals.append(
                    self._build_signal(
                        SignalType.UPI_ID_SHARED,
                        0.82,
                        event.event_id,
                        "UPI ID entry interaction detected",
                    )
                )

        signals.extend(self._detect_payment_context_signals(request))
        signals.extend(self._detect_user_flag_signals(request))

        return self._deduplicate(signals)

    def _detect_payment_context_signals(
        self, request: AssessmentRequest
    ) -> List[TriggeredSignal]:
        payment = request.payment_context
        signals: List[TriggeredSignal] = []

        if payment.qr_present or payment.payment_method == PaymentMethodType.QR_CODE:
            signals.append(
                self._build_signal(
                    SignalType.QR_PAYMENT_PROMPT,
                    0.9,
                    None,
                    "QR payment context detected",
                )
            )

        if payment.upi_id or payment.payment_method == PaymentMethodType.UPI_ID:
            signals.append(
                self._build_signal(
                    SignalType.UPI_ID_SHARED,
                    0.88,
                    None,
                    "UPI ID context detected",
                )
            )

        if (
            payment.collect_request_present
            or payment.payment_method == PaymentMethodType.COLLECT_REQUEST
        ):
            signals.append(
                self._build_signal(
                    SignalType.COLLECT_REQUEST_DETECTED,
                    0.95,
                    None,
                    "Collect request payment context detected",
                )
            )

        if (
            payment.payment_link_present
            or payment.payment_method == PaymentMethodType.PAYMENT_LINK
        ):
            signals.append(
                self._build_signal(
                    SignalType.PAYMENT_LINK_SHARED,
                    0.9,
                    None,
                    "Payment link context detected",
                )
            )

        if payment.payment_direction == PaymentDirection.SEND:
            signals.append(
                self._build_signal(
                    SignalType.PAYMENT_REQUEST,
                    0.76,
                    None,
                    "Outbound payment direction detected",
                )
            )

        return signals

    def _detect_user_flag_signals(
        self, request: AssessmentRequest
    ) -> List[TriggeredSignal]:
        flags = request.user_flags
        signals: List[TriggeredSignal] = []

        if flags.user_confirms_pressure:
            signals.append(
                self._build_signal(
                    SignalType.URGENCY,
                    0.84,
                    None,
                    "User confirmed pressure during interaction",
                )
            )

        if (
            not flags.user_confirms_identity_verified
            and not flags.user_initiated_contact
        ):
            signals.append(
                self._build_signal(
                    SignalType.IMPERSONATION,
                    0.67,
                    None,
                    "User has not verified identity for inbound interaction",
                )
            )

        return signals

    def _deduplicate(self, signals: List[TriggeredSignal]) -> List[TriggeredSignal]:
        best = {}

        for signal in signals:
            key = signal.signal_type
            current = best.get(key)

            if current is None or signal.confidence > current.confidence:
                best[key] = signal

        return list(best.values())

    def _build_signal(
        self,
        signal_type: SignalType,
        confidence: float,
        source_event_id: Optional[str],
        evidence: str,
    ) -> TriggeredSignal:
        return TriggeredSignal(
            signal_type=signal_type,
            confidence=confidence,
            source_event_id=source_event_id,
            evidence=evidence,
        )

    def _normalize_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text.strip().lower())

    def _contains_any(self, text: str, patterns: List[str]) -> bool:
        return any(pattern in text for pattern in patterns)

    def _contains_upi_id(self, text: str) -> bool:
        return bool(re.search(r"\b[a-z0-9.\-_]{2,}@[a-z]{2,}\b", text))

    def _contains_payment_link(self, text: str) -> bool:
        return bool(
            re.search(
                r"(https?://\S+)|(paytm\.me/\S+)|(phon\.pe/\S+)|(gpay\.app\.goo\.gl/\S+)",
                text,
            )
        )
