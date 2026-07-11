"""HTML and Markdown report generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_summary(receipt_dir: Path) -> dict[str, Any]:
    path = receipt_dir / "summary.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing summary.json in {receipt_dir} — run doctor first"
        )
    return json.loads(path.read_text())


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        f"# SWE Agent Preflight Report",
        "",
        f"**Instance:** `{summary.get('instance_id')}`  ",
        f"**Profile:** `{summary.get('harness_profile')}`  ",
        f"**Overall:** **{summary.get('overall')}**  ",
        f"**Evaluated:** {summary.get('evaluated_at')}",
        "",
        "## Gate results",
        "",
        "| Gate | Status | Detail |",
        "|------|--------|--------|",
    ]
    for gate in summary.get("gates", []):
        status = "PASS" if gate["passed"] else "FAIL"
        detail = gate["detail"].replace("|", "\\|")
        lines.append(f"| {gate['name']} | {status} | {detail} |")
    lines.extend(
        [
            "",
            "---",
            "",
            "Scores are only trustworthy when all harness invariants pass.",
            "",
        ]
    )
    return "\n".join(lines)


def render_html(summary: dict[str, Any]) -> str:
    overall = summary.get("overall", "UNKNOWN")
    badge_class = "pass" if overall == "PASS" else "fail"
    gate_rows = ""
    for gate in summary.get("gates", []):
        status = "PASS" if gate["passed"] else "FAIL"
        row_class = "pass" if gate["passed"] else "fail"
        gate_rows += f"""
        <tr class="{row_class}">
          <td><code>{gate['name']}</code></td>
          <td><span class="badge {row_class}">{status}</span></td>
          <td>{gate['detail']}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SWE Agent Preflight — {summary.get('instance_id')}</title>
  <style>
    :root {{
      --bg: #0b0f14; --card: #121820; --text: #e6edf3; --muted: #8b949e;
      --pass: #3fb950; --fail: #f85149; --accent: #58a6ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: ui-sans-serif, system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; line-height: 1.5; }}
    .container {{ max-width: 960px; margin: 0 auto; }}
    h1 {{ font-size: 1.75rem; margin-bottom: 0.25rem; }}
    .subtitle {{ color: var(--muted); margin-bottom: 2rem; }}
    .hero {{ background: linear-gradient(135deg, #121820 0%, #1a2332 100%); border: 1px solid #30363d; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; }}
    .overall {{ font-size: 2rem; font-weight: 700; }}
    .overall.pass {{ color: var(--pass); }}
    .overall.fail {{ color: var(--fail); }}
    table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 12px; overflow: hidden; border: 1px solid #30363d; }}
    th, td {{ padding: 0.85rem 1rem; text-align: left; border-bottom: 1px solid #21262d; }}
    th {{ background: #161b22; color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    tr.fail td:first-child {{ border-left: 3px solid var(--fail); }}
    tr.pass td:first-child {{ border-left: 3px solid var(--pass); }}
    .badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }}
    .badge.pass {{ background: rgba(63,185,80,0.15); color: var(--pass); }}
    .badge.fail {{ background: rgba(248,81,73,0.15); color: var(--fail); }}
    .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 1rem; }}
    .meta div {{ background: #161b22; padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid #30363d; }}
    .meta label {{ display: block; font-size: 0.7rem; color: var(--muted); text-transform: uppercase; }}
    footer {{ margin-top: 2rem; color: var(--muted); font-size: 0.85rem; }}
    a {{ color: var(--accent); }}
  </style>
</head>
<body>
  <div class="container">
    <h1>SWE Agent Preflight</h1>
    <p class="subtitle">Harness invariant report — agent eval scores are meaningless without preflight</p>
    <div class="hero">
      <div class="overall {badge_class}">{overall}</div>
      <div class="meta">
        <div><label>Instance</label><code>{summary.get('instance_id')}</code></div>
        <div><label>Profile</label><code>{summary.get('harness_profile')}</code></div>
        <div><label>Evaluated</label>{summary.get('evaluated_at', '')[:19]}Z</div>
      </div>
    </div>
    <table>
      <thead><tr><th>Gate</th><th>Status</th><th>Detail</th></tr></thead>
      <tbody>{gate_rows}</tbody>
    </table>
    <footer>
      Inspired by Cognition's published SWE-bench harness methodology.
      Independent tool — not affiliated with Cognition or Devin.
      <br><a href="https://github.com/Abhishek21g/swe-agent-preflight">github.com/Abhishek21g/swe-agent-preflight</a>
    </footer>
  </div>
</body>
</html>"""


def write_report(receipt_dir: Path, html_path: Path | None = None, md_path: Path | None = None) -> dict[str, str]:
    summary = load_summary(receipt_dir)
    outputs: dict[str, str] = {}

    md_target = md_path or receipt_dir / "report.md"
    md_target.write_text(render_markdown(summary))
    outputs["markdown"] = str(md_target)

    html_target = html_path or receipt_dir / "report.html"
    html_target.write_text(render_html(summary))
    outputs["html"] = str(html_target)

    return outputs
