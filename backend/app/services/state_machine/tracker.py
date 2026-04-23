from typing import List

from app.models.enums import ScamStage
from app.schemas.assessment import StageState


class ScamStateMachine:
    _ordered_stages = [
        ScamStage.TRUST,
        ScamStage.URGENCY,
        ScamStage.PAYMENT,
        ScamStage.EXTRACTION,
    ]

    _stage_order = {
        ScamStage.TRUST: 0,
        ScamStage.URGENCY: 1,
        ScamStage.PAYMENT: 2,
        ScamStage.EXTRACTION: 3,
    }

    def update(
        self, current_state: StageState, detected_stage: ScamStage
    ) -> StageState:
        current_rank = self._stage_order[current_state.current_stage]
        detected_rank = self._stage_order[detected_stage]

        if detected_rank <= current_rank:
            return StageState(
                current_stage=current_state.current_stage,
                completed_stages=current_state.completed_stages,
            )

        completed_stages = self._merge_completed_stages(
            current_state.completed_stages,
            current_state.current_stage,
            detected_stage,
        )

        return StageState(
            current_stage=detected_stage,
            completed_stages=completed_stages,
        )

    def initial_state(self) -> StageState:
        return StageState(
            current_stage=ScamStage.TRUST,
            completed_stages=[],
        )

    def _merge_completed_stages(
        self,
        existing_completed: List[ScamStage],
        current_stage: ScamStage,
        detected_stage: ScamStage,
    ) -> List[ScamStage]:
        current_rank = self._stage_order[current_stage]
        detected_rank = self._stage_order[detected_stage]

        merged = list(existing_completed)

        for stage in self._ordered_stages:
            rank = self._stage_order[stage]
            if current_rank <= rank < detected_rank and stage not in merged:
                merged.append(stage)

        return merged
