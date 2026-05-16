import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class AppConfig:
    app_name: str
    api_prefix: str
    frontend_origins: list[str]
    model_path: Path
    low_risk_max: int
    medium_risk_max: int
    high_risk_max: int
    critical_risk_max: int
    max_interaction_events: int
    api_key: str
    rate_limit_requests: int
    rate_limit_window_seconds: int
    audit_log_file: Path


settings = AppConfig(
    app_name=os.getenv("APP_NAME", "PayShield"),
    api_prefix=os.getenv("API_PREFIX", "/api/v1"),
    frontend_origins=_split_csv(
        os.getenv(
            "FRONTEND_ORIGIN",
            "http://127.0.0.1:5173,http://localhost:5173",
        )
    ),
    model_path=Path(
        os.getenv(
            "MODEL_PATH", str(BASE_DIR / "models_store" / "scam_text_pipeline.joblib")
        )
    ),
    low_risk_max=int(os.getenv("LOW_RISK_MAX", "24")),
    medium_risk_max=int(os.getenv("MEDIUM_RISK_MAX", "49")),
    high_risk_max=int(os.getenv("HIGH_RISK_MAX", "74")),
    critical_risk_max=int(os.getenv("CRITICAL_RISK_MAX", "100")),
    max_interaction_events=int(os.getenv("MAX_INTERACTION_EVENTS", "50")),
    api_key=os.getenv("API_KEY", "dev-pay-shield-key"),
    rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "30")),
    rate_limit_window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
    audit_log_file=Path(
        os.getenv("AUDIT_LOG_FILE", str(BASE_DIR / "logs" / "audit.log"))
    ),
)
