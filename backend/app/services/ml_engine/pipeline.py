from typing import Dict, List

from app.schemas.assessment import AssessmentRequest, TriggeredSignal
from app.services.ml_engine.scorer import MLSignalScorer
from app.services.signal_engine import RuleBasedSignalDetector


class HybridSignalPipeline:
    def __init__(self) -> None:
        self.rule_detector = RuleBasedSignalDetector()
        self.ml_scorer = MLSignalScorer()

    def detect(
        self,
        request: AssessmentRequest,
        repeat_contact_score: int = 0,
        trusted_beneficiary_score: int = 0,
    ) -> Dict[str, object]:
        rule_signals: List[TriggeredSignal] = self.rule_detector.detect(request)
        scam_probability = self.ml_scorer.score(
            request,
            repeat_contact_score=repeat_contact_score,
            trusted_beneficiary_score=trusted_beneficiary_score,
        )

        return {
            "rule_signals": rule_signals,
            "scam_probability": scam_probability,
        }
