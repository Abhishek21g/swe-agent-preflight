"""Receipt storage."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def default_out_dir() -> Path:
    return Path("out/receipts")


def receipt_dir_for(instance_id: str, base: Path | None = None) -> Path:
    root = base or default_out_dir()
    safe_id = instance_id.replace("/", "_")
    return root / safe_id
