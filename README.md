# SWE Agent Preflight

Harness invariant gates before SWE-bench-style agent grading — so patch ordering, test-file reset, git leakage, and env drift can't silently inflate scores.

Inspired by Cognition's published [SWE-bench technical report](https://cognition.ai/blog/swe-bench-technical-report) methodology. **Not affiliated with Cognition or Devin.**

## Install

```bash
pip install -e ".[dev]"
```

## Quickstart (mock mode — no dataset download)

```bash
# Fail gate 1: test file not reset before patch extraction
swe-agent-preflight run --mock --instance examples/demo-fail-gate1.yaml
swe-agent-preflight doctor --receipt out/receipts/demo-fail-gate1/ --spec swebench-lite --json

# Pass all gates
swe-agent-preflight run --mock --instance examples/demo-pass.yaml
swe-agent-preflight doctor --receipt out/receipts/demo-pass/ --spec swebench-lite
swe-agent-preflight report --receipt out/receipts/demo-pass/ --html out/receipts/demo-pass/report.html
```

## CLI

| Command | Purpose |
|---------|---------|
| `plan` | Preflight plan from instance YAML (`--json`) |
| `run` | Mock agent run → receipt directory (`--mock`) |
| `doctor` | Run 7 harness gates on a receipt (`--json`, exit 2 if any fail) |
| `report` | HTML/Markdown report from doctor summary |

## Doctor gates

1. **test_file_integrity** — test files from `test_patch` reset before grading
2. **patch_ordering** — agent patch before test_patch (not reversed)
3. **git_leakage** — no git remote / no commits beyond base ancestry
4. **timeout_policy** — run duration vs profile ceiling
5. **grading_env_fingerprint** — dependency manifest + lock hash present
6. **patch_apply_dry_run** — patch applies cleanly before grading
7. **fail_to_pass_manifest** — expected tests listed and non-empty

## Demo site

https://enaguthi.com/swe-agent-preflight/site/

## License

MIT
