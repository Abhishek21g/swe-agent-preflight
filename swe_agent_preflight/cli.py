"""CLI entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .doctor import diagnose
from .errors import PreflightError
from .instance import InstanceConfig
from .planner import build_plan
from .report import write_report
from .runner import execute_mock_run


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except PreflightError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swe-agent-preflight",
        description="Harness invariant gates before SWE-bench-style agent grading.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    plan_p = sub.add_parser("plan", help="Build preflight plan from instance YAML")
    plan_p.add_argument("--instance", type=Path, required=True)
    plan_p.add_argument("--spec", default="swebench-lite")
    plan_p.add_argument("--json", action="store_true", dest="as_json")
    plan_p.set_defaults(handler=_cmd_plan)

    run_p = sub.add_parser("run", help="Execute mock agent run and write receipt")
    run_p.add_argument("--instance", type=Path, required=True)
    run_p.add_argument("--mock", action="store_true", help="Mock mode (no dataset download)")
    run_p.add_argument("--spec", default="swebench-lite")
    run_p.add_argument("--out", type=Path, default=Path("out/receipts"))
    run_p.add_argument("--json", action="store_true", dest="as_json")
    run_p.set_defaults(handler=_cmd_run)

    doc_p = sub.add_parser("doctor", help="Run harness gates on a receipt directory")
    doc_p.add_argument("--receipt", type=Path, required=True)
    doc_p.add_argument("--spec", default="swebench-lite")
    doc_p.add_argument("--json", action="store_true", dest="as_json")
    doc_p.set_defaults(handler=_cmd_doctor)

    rep_p = sub.add_parser("report", help="Generate HTML/Markdown report from summary")
    rep_p.add_argument("--receipt", type=Path, required=True)
    rep_p.add_argument("--html", type=Path, default=None)
    rep_p.add_argument("--markdown", type=Path, default=None)
    rep_p.add_argument("--json", action="store_true", dest="as_json")
    rep_p.set_defaults(handler=_cmd_report)

    return parser


def _cmd_plan(args: argparse.Namespace) -> int:
    instance = InstanceConfig.from_yaml(args.instance)
    plan = build_plan(instance, args.spec)
    if args.as_json:
        print(json.dumps(plan, indent=2))
    else:
        print(f"Instance: {plan['instance_id']}")
        print(f"Profile:  {plan['harness_profile']} ({plan['timeout_seconds']}s ceiling)")
        print(f"Gates:    {', '.join(plan['gates_planned'])}")
        if plan["risks"]:
            print("Risks:")
            for risk in plan["risks"]:
                print(f"  - {risk}")
        else:
            print("Risks:    none detected in scenario")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    if not args.mock:
        raise PreflightError("Only --mock mode is supported in v0.1 (no SWE-bench download required)")
    instance = InstanceConfig.from_yaml(args.instance)
    run_dir = execute_mock_run(instance, args.out, args.spec)
    payload = {"receipt_dir": str(run_dir), "instance_id": instance.instance_id, "mode": "mock"}
    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Mock run complete → {run_dir}")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    summary = diagnose(args.receipt, args.spec)
    if args.as_json:
        print(json.dumps(summary, indent=2))
    else:
        for gate in summary["gates"]:
            status = "PASS" if gate["passed"] else "FAIL"
            print(f"[{status}] {gate['name']}: {gate['detail']}")
        print(f"\nOverall: {summary['overall']}")
    return 0 if summary["passed"] else 2


def _cmd_report(args: argparse.Namespace) -> int:
    outputs = write_report(args.receipt, args.html, args.markdown)
    if args.as_json:
        print(json.dumps(outputs, indent=2))
    else:
        for kind, path in outputs.items():
            print(f"Wrote {kind}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
