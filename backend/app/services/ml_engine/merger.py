from typing import Dict, List

from app.models.enums import SignalType
from app.schemas.assessment import TriggeredSignal


class MLSignalMerger:
    def merge(
        self,
        rule_signals: List[TriggeredSignal],
        ml_scores: Dict[SignalType, float],
    ) -> List[TriggeredSignal]:
        merged = {signal.signal_type: signal for signal in rule_signals}

        for signal_type, ml_confidence in ml_scores.items():
            if ml_confidence < 0.65:
                continue

            if signal_type in merged:
                current = merged[signal_type]
                if ml_confidence > current.confidence:
                    merged[signal_type] = TriggeredSignal(
                        signal_type=signal_type,
                        confidence=ml_confidence,
                        source_event_id=current.source_event_id,
                        evidence=f"ML scoring increased confidence for '{signal_type.value}'",
                    )
            else:
                merged[signal_type] = TriggeredSignal(
                    signal_type=signal_type,
                    confidence=ml_confidence,
                    source_event_id=None,
                    evidence=f"ML scoring detected '{signal_type.value}'",
                )

        return list(merged.values())
