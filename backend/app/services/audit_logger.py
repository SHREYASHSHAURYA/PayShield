from datetime import datetime
import json

from app.core import settings


def write_audit_log(entry: dict) -> None:
    settings.audit_log_file.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        **entry,
    }

    with settings.audit_log_file.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload) + "\n")
