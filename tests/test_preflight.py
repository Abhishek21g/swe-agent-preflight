import json
from pathlib import Path

import pytest

from swe_agent_preflight.cli import main
from swe_agent_preflight.doctor import diagnose
from swe_agent_preflight.gates import (
    check_fail_to_pass_manifest,
    check_git_leakage,
    check_grading_env_fingerprint,
    check_patch_apply_dry_run,
    check_patch_ordering,
    check_test_file_integrity,
    check_timeout_policy,
    run_all_gates,
)
from swe_agent_preflight.instance import InstanceConfig
from swe_agent_preflight.planner import build_plan
from swe_agent_preflight.report import render_html, render_markdown, write_report
from swe_agent_preflight.runner import execute_mock_run
from swe_agent_preflight.specs import get_spec

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def test_plan_command_json():
    rc = main(["plan", "--instance", str(EXAMPLES / "demo-pass.yaml"), "--json"])
    assert rc == 0


def test_plan_lists_seven_gates():
    inst = InstanceConfig.from_yaml(EXAMPLES / "demo-pass.yaml")
    plan = build_plan(inst)
    assert len(plan["gates_planned"]) == 7


def test_mock_run_creates_manifest(tmp_path):
    inst = InstanceConfig.from_yaml(EXAMPLES / "demo-pass.yaml")
    run_dir = execute_mock_run(inst, tmp_path)
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["instance_id"] == "demo-pass"
    assert (run_dir / "plan.json").exists()


def test_doctor_pass_scenario(tmp_path):
    inst = InstanceConfig.from_yaml(EXAMPLES / "demo-pass.yaml")
    run_dir = execute_mock_run(inst, tmp_path)
    summary = diagnose(run_dir, "swebench-lite")
    assert summary["passed"] is True
    assert len(summary["gates"]) == 7


def test_doctor_fail_gate1(tmp_path):
    inst = InstanceConfig.from_yaml(EXAMPLES / "demo-fail-gate1.yaml")
    run_dir = execute_mock_run(inst, tmp_path)
    summary = diagnose(run_dir, "swebench-lite")
    assert summary["passed"] is False
    gate = next(g for g in summary["gates"] if g["name"] == "test_file_integrity")
    assert gate["passed"] is False


def test_doctor_cli_exit_code_fail(tmp_path):
    inst = InstanceConfig.from_yaml(EXAMPLES / "demo-fail-gate1.yaml")
    run_dir = execute_mock_run(inst, tmp_path)
    rc = main(["doctor", "--receipt", str(run_dir), "--spec", "swebench-lite"])
    assert rc == 2


def test_doctor_cli_exit_code_pass(tmp_path):
    inst = InstanceConfig.from_yaml(EXAMPLES / "demo-pass.yaml")
    run_dir = execute_mock_run(inst, tmp_path)
    diagnose(run_dir, "swebench-lite")
    rc = main(["doctor", "--receipt", str(run_dir)])
    assert rc == 0


def test_timeout_gate_fails():
    spec = get_spec("swebench-lite")
    receipt = {"run_duration_seconds": spec.timeout_seconds + 1}
    result = check_timeout_policy(receipt, spec)
    assert result.passed is False


def test_timeout_gate_passes():
    spec = get_spec("terminal-bench")
    receipt = {"run_duration_seconds": 3600}
    result = check_timeout_policy(receipt, spec)
    assert result.passed is True


def test_git_leakage_remote():
    fail = check_git_leakage({"has_git_remote": True, "git_remote": "origin"})
    assert fail.passed is False
    ok = check_git_leakage({"has_git_remote": False, "extra_commits": []})
    assert ok.passed is True


def test_patch_ordering_reversed():
    bad = check_patch_ordering({"patch_ordering": "test_then_agent"})
    assert bad.passed is False
    good = check_patch_ordering({"patch_ordering": "agent_then_test"})
    assert good.passed is True


def test_patch_apply_dry_run():
    ok = check_patch_apply_dry_run({"patch_apply_ok": True})
    assert ok.passed is True
    bad = check_patch_apply_dry_run({"patch_apply_ok": False, "patch_apply_detail": "failed"})
    assert bad.passed is False


def test_grading_env_fingerprint():
    ok = check_grading_env_fingerprint(
        {"dependency_manifest": "requirements.txt", "grading_env_hash": "sha256:x"}
    )
    assert ok.passed is True
    bad = check_grading_env_fingerprint({})
    assert bad.passed is False


def test_fail_to_pass_manifest_empty():
    bad = check_fail_to_pass_manifest({"fail_to_pass": []})
    assert bad.passed is False
    ok = check_fail_to_pass_manifest({"fail_to_pass": ["tests/a.py"]})
    assert ok.passed is True


def test_test_file_integrity_dirty():
    bad = check_test_file_integrity(
        {"test_files_reset": False, "dirty_test_files": ["tests/x.py"]}
    )
    assert bad.passed is False


def test_run_all_gates_count():
    receipt = {
        "test_files_reset": True,
        "dirty_test_files": [],
        "patch_ordering": "agent_then_test",
        "has_git_remote": False,
        "extra_commits": [],
        "run_duration_seconds": 60,
        "dependency_manifest": "req.txt",
        "grading_env_hash": "sha256:a",
        "patch_apply_ok": True,
        "fail_to_pass": ["t.py"],
    }
    gates = run_all_gates(receipt, get_spec("swebench-lite"))
    assert len(gates) == 7
    assert all(g.passed for g in gates)


def test_report_writes_html_and_md(tmp_path):
    inst = InstanceConfig.from_yaml(EXAMPLES / "demo-pass.yaml")
    run_dir = execute_mock_run(inst, tmp_path)
    diagnose(run_dir, "swebench-lite")
    outputs = write_report(run_dir)
    assert Path(outputs["html"]).exists()
    assert Path(outputs["markdown"]).exists()
    html = Path(outputs["html"]).read_text()
    assert "SWE Agent Preflight" in html


def test_render_markdown_contains_overall():
    summary = {"instance_id": "x", "harness_profile": "swebench-lite", "overall": "PASS", "gates": []}
    md = render_markdown(summary)
    assert "PASS" in md


def test_full_cli_pipeline(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rc = main(
        [
            "run",
            "--mock",
            "--instance",
            str(EXAMPLES / "demo-pass.yaml"),
            "--out",
            str(tmp_path / "receipts"),
        ]
    )
    assert rc == 0
    rc = main(["doctor", "--receipt", str(tmp_path / "receipts" / "demo-pass")])
    assert rc == 0
    rc = main(["report", "--receipt", str(tmp_path / "receipts" / "demo-pass")])
    assert rc == 0


def test_unknown_spec_raises():
    with pytest.raises(KeyError):
        get_spec("not-a-real-profile")


def test_run_requires_mock_flag():
    rc = main(["run", "--instance", str(EXAMPLES / "demo-pass.yaml")])
    assert rc == 1
