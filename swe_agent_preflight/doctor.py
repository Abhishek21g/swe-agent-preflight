"""Doctor command — run gates and write summary.json."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .gates import load_receipt_dir, run_all_gates
from .specs import get_spec
from .store import write_json


def diagnose(receipt_dir: Path, spec_name: str) -> dict[str, Any]:
    spec = get_spec(spec_name)
    receipt = load_receipt_dir(receipt_dir)
    receipt["harness_profile"] = spec_name

    gates = run_all_gates(receipt, spec)
    passed = all(g.passed for g in gates)

    summary: dict[str, Any] = {
        "instance_id": receipt.get("instance_id"),
        "receipt_dir": str(receipt_dir),
        "harness_profile": spec.name,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "gates": [g.to_dict() for g in gates],
        "overall": "PASS" if passed else "FAIL",
    }
    write_json(receipt_dir / "summary.json", summary)
    return summary
