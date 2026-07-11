"""Build preflight plan from instance config."""

from __future__ import annotations

from typing import Any

from .instance import InstanceConfig
from .specs import HarnessSpec, get_spec


def build_plan(instance: InstanceConfig, spec_name: str = "swebench-lite") -> dict[str, Any]:
    spec = get_spec(spec_name)
    risks: list[str] = []

    if not instance.test_files_reset:
        risks.append("test_file_integrity: agent may have left test files dirty")
    if instance.patch_ordering != "agent_then_test":
        risks.append("patch_ordering: reversed patch apply order detected in scenario")
    if instance.has_git_remote:
        risks.append("git_leakage: git remote still configured")
    if instance.run_duration_seconds > spec.timeout_seconds:
        risks.append(
            f"timeout_policy: run {instance.run_duration_seconds}s exceeds {spec.timeout_seconds}s ceiling"
        )
    if not instance.patch_applies_cleanly:
        risks.append("patch_apply_dry_run: agent patch may not apply cleanly")
    if not instance.fail_to_pass:
        risks.append("fail_to_pass_manifest: empty expected test list")

    return {
        "instance_id": instance.instance_id,
        "repo": instance.repo,
        "base_commit": instance.base_commit,
        "harness_profile": spec.name,
        "timeout_seconds": spec.timeout_seconds,
        "run_duration_seconds": instance.run_duration_seconds,
        "test_files": instance.test_files,
        "fail_to_pass": instance.fail_to_pass,
        "gates_planned": [
            "test_file_integrity",
            "patch_ordering",
            "git_leakage",
            "timeout_policy",
            "grading_env_fingerprint",
            "patch_apply_dry_run",
            "fail_to_pass_manifest",
        ],
        "risks": risks,
        "mock_scenario": instance.mock_scenario,
    }
