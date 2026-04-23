from typing import Dict, List

from app.schemas.assessment import AssessmentRequest, TriggeredSignal
from app.services.ml_engine.scorer import MLSignalScorer
from app.services.signal_engine import RuleBasedSignalDetector


class HybridSignalPipeline:
    def __init__(self) -> None:
        self.rule_detector = RuleBasedSignalDetector()
        self.ml_scorer = MLSignalScorer()

    def detect(self, request: AssessmentRequest) -> Dict[str, object]:
        rule_signals: List[TriggeredSignal] = self.rule_detector.detect(request)
        scam_probability = self.ml_scorer.score(request)

        return {
            "rule_signals": rule_signals,
            "scam_probability": scam_probability,
        }
