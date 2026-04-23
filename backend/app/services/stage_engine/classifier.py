from typing import List, Set

from app.models.enums import ScamStage, SignalType
from app.schemas.assessment import TriggeredSignal


class StageClassifier:
    def classify(self, signals: List[TriggeredSignal]) -> ScamStage:
        signal_types = {signal.signal_type for signal in signals}

        if self._is_extraction_stage(signal_types):
            return ScamStage.EXTRACTION

        if self._is_payment_stage(signal_types):
            return ScamStage.PAYMENT

        if self._is_urgency_stage(signal_types):
            return ScamStage.URGENCY

        return ScamStage.TRUST

    def _is_urgency_stage(self, signal_types: Set[SignalType]) -> bool:
        urgency_signals = {
            SignalType.URGENCY,
            SignalType.FEAR_PRESSURE,
            SignalType.SECRECY_REQUEST,
            SignalType.AUTHORITY_CLAIM,
            SignalType.ACCOUNT_BLOCK_CLAIM,
            SignalType.KYC_CLAIM,
        }
        return bool(signal_types & urgency_signals)

    def _is_payment_stage(self, signal_types: Set[SignalType]) -> bool:
        payment_signals = {
            SignalType.QR_PAYMENT_PROMPT,
            SignalType.UPI_ID_SHARED,
            SignalType.COLLECT_REQUEST_DETECTED,
            SignalType.PAYMENT_LINK_SHARED,
            SignalType.PAYMENT_REQUEST,
        }
        return bool(signal_types & payment_signals)

    def _is_extraction_stage(self, signal_types: Set[SignalType]) -> bool:
        extraction_signals = {
            SignalType.TRANSACTION_CONFIRMATION_REQUEST,
            SignalType.REMOTE_APP_REQUEST,
        }
        return bool(signal_types & extraction_signals)
