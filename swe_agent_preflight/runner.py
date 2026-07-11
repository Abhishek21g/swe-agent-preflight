"""Mock agent run → receipt artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .gates import instance_to_receipt
from .instance import InstanceConfig
from .planner import build_plan
from .store import receipt_dir_for, write_json


def execute_mock_run(
    instance: InstanceConfig,
    out_root: Path | None = None,
    spec_name: str = "swebench-lite",
) -> Path:
    run_dir = receipt_dir_for(instance.instance_id, out_root)
    run_dir.mkdir(parents=True, exist_ok=True)

    plan = build_plan(instance, spec_name)
    manifest = instance_to_receipt(instance)
    manifest["harness_profile"] = spec_name
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()
    manifest["mode"] = "mock"
    manifest["mock_scenario"] = instance.mock_scenario

    write_json(run_dir / "plan.json", plan)
    write_json(run_dir / "manifest.json", manifest)

    if instance.agent_patch:
        (run_dir / "agent.patch").write_text(instance.agent_patch)
    (run_dir / "test.patch").write_text(instance.test_patch)

    events = [
        {"ts": manifest["created_at"], "event": "run_start", "instance_id": instance.instance_id},
        {"ts": manifest["created_at"], "event": "mock_complete", "scenario": instance.mock_scenario},
    ]
    (run_dir / "events.jsonl").write_text(
        "\n".join(__import__("json").dumps(e) for e in events) + "\n"
    )

    return run_dir
