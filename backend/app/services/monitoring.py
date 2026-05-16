import json
from pathlib import Path

from app.core import settings


def load_model_metadata() -> dict:
    metadata_path = settings.model_path.parent / "model_metadata.json"

    if not metadata_path.exists():
        return {
            "model_name": "unknown",
            "model_version": "unknown",
            "training_dataset": "unknown",
            "task": "unknown",
        }

    with metadata_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_runtime_status() -> dict:
    metadata = load_model_metadata()

    return {
        "service": settings.app_name,
        "api_prefix": settings.api_prefix,
        "model_path": str(settings.model_path),
        "model_name": metadata.get("model_name", "unknown"),
        "model_version": metadata.get("model_version", "unknown"),
        "training_dataset": metadata.get("training_dataset", "unknown"),
        "task": metadata.get("task", "unknown"),
        "rate_limit_requests": settings.rate_limit_requests,
        "rate_limit_window_seconds": settings.rate_limit_window_seconds,
        "audit_log_file": str(settings.audit_log_file),
    }
