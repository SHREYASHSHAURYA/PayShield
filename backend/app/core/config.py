from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "PayShield"
    api_prefix: str = "/api/v1"
    low_risk_max: int = 24
    medium_risk_max: int = 49
    high_risk_max: int = 74
    critical_risk_max: int = 100
    max_interaction_events: int = 50


settings = AppConfig()
