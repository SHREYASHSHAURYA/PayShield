from dataclasses import dataclass, field

from app.schemas.assessment import StageState


@dataclass
class SessionContext:
    stage_state: StageState
    interaction_count: int = 0
    safe_interaction_count: int = 0
    repeat_contact_score: int = 0
    trusted_beneficiary_score: int = 0
    last_beneficiary_key: str = ""
    last_interaction_safe: bool = False
