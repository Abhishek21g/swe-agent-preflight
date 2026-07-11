const SCENARIOS = {
  pass: {
    id: "demo-pass",
    repo: "django/django",
    profile: "swebench-lite",
    instanceYaml: "examples/demo-pass.yaml",
    hint: "Clean harness — all seven invariants pass. Score is trustworthy.",
    verdict: "PASS",
    plain: "All seven harness invariants hold. Safe to publish this eval score.",
    story: [
      { strong: "Setup", text: "Agent runs in isolated repo; git remote stripped." },
      { strong: "Reset", text: "Test files from test_patch reset before patch extraction." },
      { strong: "Apply", text: "Agent patch applied, then test_patch, then fail-to-pass tests." },
      { strong: "Verdict", text: "All gates pass — grading score is meaningful." },
    ],
    gates: [
      { name: "test_file_integrity", passed: true, detail: "test files matching test_patch were reset before patch extraction" },
      { name: "patch_ordering", passed: true, detail: "agent patch applied before test_patch" },
      { name: "git_leakage", passed: true, detail: "no git remote and no commits beyond base ancestry" },
      { name: "timeout_policy", passed: true, detail: "run duration 1200s within swebench-lite ceiling 2700s" },
      { name: "grading_env_fingerprint", passed: true, detail: "manifest=requirements.txt lock=sha256:demo-lock-abc123" },
      { name: "patch_apply_dry_run", passed: true, detail: "git apply --check passed" },
      { name: "fail_to_pass_manifest", passed: true, detail: "1 fail-to-pass test(s): tests/admin/test_filters.py" },
    ],
    card: {
      tag: "pass",
      tagLabel: "PASS",
      title: "Clean harness",
      desc: "All invariants hold. Benchmark score reflects agent capability.",
      meta: "7/7 gates · 20 min run",
    },
  },
  "fail-gate1": {
    id: "demo-fail-gate1",
    repo: "django/django",
    profile: "swebench-lite",
    instanceYaml: "examples/demo-fail-gate1.yaml",
    hint: "Agent left test files dirty — grading may silently pass with corrupted test state.",
    verdict: "FAIL",
    plain: "Test file integrity failed. Agent modified files in the test_patch set without resetting them before grading.",
    story: [
      { strong: "Agent run", text: "Agent edited tests/admin/test_filters.py during exploration." },
      { strong: "Grading prep", text: "Harness skipped git checkout reset on test files." },
      { strong: "Risk", text: "Score may reflect test tampering, not source fix quality." },
      { strong: "Verdict", text: "FAIL gate 1 — do not publish this score." },
    ],
    gates: [
      { name: "test_file_integrity", passed: false, detail: "agent-modified test files not reset: ['tests/admin/test_filters.py']" },
      { name: "patch_ordering", passed: true, detail: "agent patch applied before test_patch" },
      { name: "git_leakage", passed: true, detail: "no git remote and no commits beyond base ancestry" },
      { name: "timeout_policy", passed: true, detail: "run duration 1200s within swebench-lite ceiling 2700s" },
      { name: "grading_env_fingerprint", passed: true, detail: "manifest=requirements.txt lock=sha256:demo-lock-abc123" },
      { name: "patch_apply_dry_run", passed: true, detail: "git apply --check passed" },
      { name: "fail_to_pass_manifest", passed: true, detail: "1 fail-to-pass test(s): tests/admin/test_filters.py" },
    ],
    card: {
      tag: "fail",
      tagLabel: "FAIL",
      title: "Dirty test file",
      desc: "Gate 1 fails — classic silent false pass when tests aren't reset.",
      meta: "6/7 gates · gate 1 fail",
    },
  },
  "fail-order": {
    id: "demo-fail-patch-order",
    repo: "pytest-dev/pytest",
    profile: "swebench-lite",
    instanceYaml: "examples/demo-fail-patch-order.yaml",
    hint: "test_patch applied before agent patch — reversed ordering invalidates SWE-bench semantics.",
    verdict: "FAIL",
    plain: "Patch ordering failed. test_patch was applied before the agent patch — scores are not comparable.",
    story: [
      { strong: "Expected", text: "Agent patch first, then test_patch (Cognition technical report)." },
      { strong: "Observed", text: "Harness reversed apply order." },
      { strong: "Risk", text: "Fail-to-pass tests may not exercise the agent's actual fix." },
      { strong: "Verdict", text: "FAIL gate 2 — fix harness before comparing runs." },
    ],
    gates: [
      { name: "test_file_integrity", passed: true, detail: "test files reset before grading" },
      { name: "patch_ordering", passed: false, detail: "test_patch applied before agent patch (reversed)" },
      { name: "git_leakage", passed: true, detail: "no git remote and no commits beyond base ancestry" },
      { name: "timeout_policy", passed: true, detail: "run duration 900s within swebench-lite ceiling 2700s" },
      { name: "grading_env_fingerprint", passed: true, detail: "manifest=requirements.txt lock=sha256:demo-lock-order" },
      { name: "patch_apply_dry_run", passed: true, detail: "git apply --check passed" },
      { name: "fail_to_pass_manifest", passed: true, detail: "1 fail-to-pass test(s): testing/test_mark.py" },
    ],
    card: {
      tag: "fail",
      tagLabel: "FAIL",
      title: "Reversed patches",
      desc: "Gate 2 fails — test_patch before agent patch breaks eval semantics.",
      meta: "6/7 gates · gate 2 fail",
    },
  },
  "fail-timeout": {
    id: "demo-fail-timeout",
    repo: "sympy/sympy",
    profile: "swebench-lite",
    instanceYaml: "examples/demo-fail-timeout.yaml",
    hint: "Run exceeded 45m SWE-bench profile ceiling — score not comparable to published baselines.",
    verdict: "FAIL",
    plain: "Timeout policy failed. Run duration exceeds swebench-lite ceiling (2700s). Score is not apples-to-apples.",
    story: [
      { strong: "Profile", text: "SWE-bench agent eval uses 45 minute ceiling (Cognition report)." },
      { strong: "Observed", text: "Mock run logged 3600s — over ceiling." },
      { strong: "Risk", text: "Extra time may inflate pass rate vs other harnesses." },
      { strong: "Verdict", text: "FAIL gate 4 — normalize timeout before publishing." },
    ],
    gates: [
      { name: "test_file_integrity", passed: true, detail: "test files reset before grading" },
      { name: "patch_ordering", passed: true, detail: "agent patch applied before test_patch" },
      { name: "git_leakage", passed: true, detail: "no git remote and no commits beyond base ancestry" },
      { name: "timeout_policy", passed: false, detail: "run duration 3600s exceeds swebench-lite ceiling 2700s" },
      { name: "grading_env_fingerprint", passed: true, detail: "manifest=requirements.txt lock=sha256:demo-lock-timeout" },
      { name: "patch_apply_dry_run", passed: true, detail: "git apply --check passed" },
      { name: "fail_to_pass_manifest", passed: true, detail: "1 fail-to-pass test(s): sympy/core/tests/test_basic.py" },
    ],
    card: {
      tag: "fail",
      tagLabel: "FAIL",
      title: "Timeout exceeded",
      desc: "Gate 4 fails — inconsistent timeout policy across harnesses.",
      meta: "6/7 gates · gate 4 fail",
    },
  },
};

const SCENARIO_ORDER = ["pass", "fail-gate1", "fail-order", "fail-timeout"];

function buildReceipt(scenario) {
  return {
    instance_id: scenario.id,
    harness_profile: scenario.profile,
    evaluated_at: new Date().toISOString(),
    passed: scenario.verdict === "PASS",
    overall: scenario.verdict,
    gates: scenario.gates.map((g) => ({
      name: g.name,
      passed: g.passed,
      detail: g.detail,
    })),
  };
}

function render(mode) {
  const s = SCENARIOS[mode];
  if (!s) return;

  document.querySelectorAll(".mode-tabs button").forEach((btn) => {
    const on = btn.dataset.mode === mode;
    btn.classList.toggle("active", on);
    btn.setAttribute("aria-selected", on ? "true" : "false");
  });

  document.querySelectorAll(".scenario-card").forEach((card) => {
    card.classList.toggle("active", card.dataset.mode === mode);
  });

  document.getElementById("scenarioHint").textContent = s.hint;

  const word = document.getElementById("verdictWord");
  word.textContent = s.verdict;
  word.className = `verdict-word ${s.verdict === "PASS" ? "pass" : "fail"}`;
  document.getElementById("verdictPlain").textContent = s.plain;

  const passCount = s.gates.filter((g) => g.passed).length;
  const failCount = s.gates.length - passCount;
  document.getElementById("passRate").textContent = `${passCount}/${s.gates.length}`;
  document.getElementById("passBar").style.width = `${(passCount / s.gates.length) * 100}%`;
  document.getElementById("countPass").textContent = passCount;
  document.getElementById("countFail").textContent = failCount;
  document.getElementById("instanceMeta").textContent = `${s.id} · ${s.repo} · ${s.profile}`;

  document.getElementById("gateList").innerHTML = s.gates
    .map(
      (g) => `
      <li>
        <span class="gate-status ${g.passed ? "pass" : "fail"}">${g.passed ? "pass" : "fail"}</span>
        <span>
          <span class="gate-name">${g.name}</span>
          <span class="gate-detail">${g.detail}</span>
        </span>
      </li>`
    )
    .join("");

  document.getElementById("storySteps").innerHTML = s.story
    .map((step) => `<li><strong>${step.strong}</strong> ${step.text}</li>`)
    .join("");

  document.getElementById("receiptPre").textContent = JSON.stringify(buildReceipt(s), null, 2);

  document.getElementById("cliRun").textContent = `swe-agent-preflight run --mock --instance ${s.instanceYaml}`;
  document.getElementById("cliDoctor").textContent = `swe-agent-preflight doctor --receipt out/receipts/${s.id}/ --json`;
  document.getElementById("cliReport").textContent = `swe-agent-preflight report --receipt out/receipts/${s.id}/ --html report.html`;
}

function buildScenarioCards() {
  const grid = document.getElementById("scenarioGrid");
  grid.innerHTML = SCENARIO_ORDER.map((mode) => {
    const s = SCENARIOS[mode];
    const c = s.card;
    return `
      <button type="button" class="scenario-card" data-mode="${mode}">
        <span class="scenario-tag ${c.tag}">${c.tagLabel}</span>
        <h3>${c.title}</h3>
        <p>${c.desc}</p>
        <span class="scenario-meta">${c.meta}</span>
      </button>`;
  }).join("");

  grid.querySelectorAll(".scenario-card").forEach((el) => {
    el.addEventListener("click", () => render(el.dataset.mode));
  });
}

function initTheme() {
  const root = document.documentElement;
  const btn = document.getElementById("themeToggle");
  const saved = localStorage.getItem("swe-preflight-theme");
  if (saved === "light") {
    root.setAttribute("data-theme", "light");
    btn.textContent = "☾";
  }
  btn.addEventListener("click", () => {
    const light = root.getAttribute("data-theme") === "light";
    if (light) {
      root.removeAttribute("data-theme");
      btn.textContent = "☀";
      localStorage.setItem("swe-preflight-theme", "dark");
    } else {
      root.setAttribute("data-theme", "light");
      btn.textContent = "☾";
      localStorage.setItem("swe-preflight-theme", "light");
    }
  });
}

function initCopy() {
  document.getElementById("copyReceipt").addEventListener("click", async () => {
    const text = document.getElementById("receiptPre").textContent;
    try {
      await navigator.clipboard.writeText(text);
      const btn = document.getElementById("copyReceipt");
      const orig = btn.textContent;
      btn.textContent = "Copied";
      setTimeout(() => { btn.textContent = orig; }, 1500);
    } catch (_) {
      /* clipboard blocked */
    }
  });
}

function initNav() {
  document.querySelectorAll(".deck-nav-pill a[data-nav]").forEach((link) => {
    link.addEventListener("click", () => {
      document.querySelectorAll(".deck-nav-pill a[data-nav]").forEach((a) => a.classList.remove("active"));
      link.classList.add("active");
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  buildScenarioCards();
  document.querySelectorAll(".mode-tabs button").forEach((btn) => {
    btn.addEventListener("click", () => render(btn.dataset.mode));
  });
  initTheme();
  initCopy();
  initNav();
  render("pass");
});
