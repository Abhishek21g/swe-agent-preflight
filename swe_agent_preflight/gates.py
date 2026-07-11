"""Seven harness invariant gates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .instance import InstanceConfig
from .specs import HarnessSpec


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def check_test_file_integrity(receipt: dict[str, Any]) -> GateResult:
    reset = receipt.get("test_files_reset", False)
    dirty = receipt.get("dirty_test_files", [])
    if reset and not dirty:
        return GateResult(
            "test_file_integrity",
            True,
            "test files matching test_patch were reset before patch extraction",
        )
    if dirty:
        return GateResult(
            "test_file_integrity",
            False,
            f"agent-modified test files not reset: {dirty}",
        )
    return GateResult(
        "test_file_integrity",
        False,
        "test files were not reset before grading patch extraction",
    )


def check_patch_ordering(receipt: dict[str, Any]) -> GateResult:
    order = receipt.get("patch_ordering", "")
    if order == "agent_then_test":
        return GateResult(
            "patch_ordering",
            True,
            "agent patch applied before test_patch",
        )
    if order == "test_then_agent":
        return GateResult(
            "patch_ordering",
            False,
            "test_patch applied before agent patch (reversed)",
        )
    return GateResult("patch_ordering", False, f"unknown patch ordering: {order!r}")


def check_git_leakage(receipt: dict[str, Any]) -> GateResult:
    if receipt.get("has_git_remote"):
        return GateResult(
            "git_leakage",
            False,
            f"git remote still present: {receipt.get('git_remote', 'origin')}",
        )
    extra = receipt.get("extra_commits", [])
    if extra:
        return GateResult(
            "git_leakage",
            False,
            f"commits beyond base ancestry: {extra}",
        )
    return GateResult(
        "git_leakage",
        True,
        "no git remote and no commits beyond base ancestry",
    )


def check_timeout_policy(receipt: dict[str, Any], spec: HarnessSpec) -> GateResult:
    duration = int(receipt.get("run_duration_seconds", 0))
    ceiling = spec.timeout_seconds
    if duration <= ceiling:
        return GateResult(
            "timeout_policy",
            True,
            f"run duration {duration}s within {spec.name} ceiling {ceiling}s",
        )
    return GateResult(
        "timeout_policy",
        False,
        f"run duration {duration}s exceeds {spec.name} ceiling {ceiling}s",
    )


def check_grading_env_fingerprint(receipt: dict[str, Any]) -> GateResult:
    manifest = receipt.get("dependency_manifest")
    env_hash = receipt.get("grading_env_hash")
    if manifest and env_hash:
        return GateResult(
            "grading_env_fingerprint",
            True,
            f"manifest={manifest} lock={env_hash}",
        )
    missing = []
    if not manifest:
        missing.append("dependency_manifest")
    if not env_hash:
        missing.append("grading_env_hash")
    return GateResult(
        "grading_env_fingerprint",
        False,
        f"missing grading env artifacts: {missing}",
    )


def check_patch_apply_dry_run(receipt: dict[str, Any]) -> GateResult:
    if receipt.get("patch_apply_ok"):
        return GateResult(
            "patch_apply_dry_run",
            True,
            receipt.get("patch_apply_detail", "git apply --check passed"),
        )
    return GateResult(
        "patch_apply_dry_run",
        False,
        receipt.get("patch_apply_detail", "patch dry-run failed"),
    )


def check_fail_to_pass_manifest(receipt: dict[str, Any]) -> GateResult:
    tests = receipt.get("fail_to_pass") or []
    if tests:
        return GateResult(
            "fail_to_pass_manifest",
            True,
            f"{len(tests)} fail-to-pass test(s): {tests[:3]}{'...' if len(tests) > 3 else ''}",
        )
    return GateResult(
        "fail_to_pass_manifest",
        False,
        "expected fail-to-pass test list is empty",
    )


ALL_GATES = [
    check_test_file_integrity,
    check_patch_ordering,
    check_git_leakage,
    check_timeout_policy,
    check_grading_env_fingerprint,
    check_patch_apply_dry_run,
    check_fail_to_pass_manifest,
]


def run_all_gates(receipt: dict[str, Any], spec: HarnessSpec) -> list[GateResult]:
    results: list[GateResult] = []
    for gate_fn in ALL_GATES:
        if gate_fn is check_timeout_policy:
            results.append(gate_fn(receipt, spec))
        else:
            results.append(gate_fn(receipt))
    return results


def instance_to_receipt(instance: InstanceConfig) -> dict[str, Any]:
    dirty = [] if instance.test_files_reset else list(instance.test_files)
    patch_detail = (
        "git apply --check passed"
        if instance.patch_applies_cleanly
        else "git apply --check failed: corrupt patch hunk"
    )
    return {
        "instance_id": instance.instance_id,
        "repo": instance.repo,
        "base_commit": instance.base_commit,
        "harness_profile": "swebench-lite",
        "run_duration_seconds": instance.run_duration_seconds,
        "test_files": instance.test_files,
        "test_files_reset": instance.test_files_reset,
        "dirty_test_files": dirty,
        "patch_ordering": instance.patch_ordering,
        "has_git_remote": instance.has_git_remote,
        "git_remote": "origin" if instance.has_git_remote else None,
        "extra_commits": instance.extra_commits,
        "dependency_manifest": instance.dependency_manifest,
        "grading_env_hash": instance.grading_env_hash,
        "patch_apply_ok": instance.patch_applies_cleanly,
        "patch_apply_detail": patch_detail,
        "fail_to_pass": instance.fail_to_pass,
        "agent_patch": instance.agent_patch,
        "test_patch": instance.test_patch,
        "mock": True,
    }


def load_receipt_dir(receipt_dir: Path) -> dict[str, Any]:
    import json

    manifest_path = receipt_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest.json in {receipt_dir}")
    return json.loads(manifest_path.read_text())
