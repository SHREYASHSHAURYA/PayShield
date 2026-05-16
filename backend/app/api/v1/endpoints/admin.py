import json
from pathlib import Path

from fastapi import APIRouter, Depends, Query

from app.core import settings
from app.services.security import verify_api_key

router = APIRouter()


@router.get("/audit-logs", dependencies=[Depends(verify_api_key)])
def get_audit_logs(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    log_file: Path = settings.audit_log_file

    if not log_file.exists():
        return {"entries": []}

    lines = log_file.read_text(encoding="utf-8").splitlines()
    selected = lines[-limit:]

    entries = []
    for line in selected:
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))

    return {"entries": entries}
