const RECEIPTS = {
  pass: {
    instance_id: "demo-pass",
    harness_profile: "swebench-lite",
    overall: "PASS",
    passed: true,
    gates: [
      { name: "test_file_integrity", passed: true, detail: "test files matching test_patch were reset before patch extraction" },
      { name: "patch_ordering", passed: true, detail: "agent patch applied before test_patch" },
      { name: "git_leakage", passed: true, detail: "no git remote and no commits beyond base ancestry" },
      { name: "timeout_policy", passed: true, detail: "run duration 1200s within swebench-lite ceiling 2700s" },
      { name: "grading_env_fingerprint", passed: true, detail: "manifest=requirements.txt lock=sha256:demo-lock-abc123" },
      { name: "patch_apply_dry_run", passed: true, detail: "git apply --check passed" },
      { name: "fail_to_pass_manifest", passed: true, detail: "1 fail-to-pass test(s): ['tests/admin/test_filters.py']" },
    ],
  },
  fail: {
    instance_id: "demo-fail-gate1",
    harness_profile: "swebench-lite",
    overall: "FAIL",
    passed: false,
    gates: [
      { name: "test_file_integrity", passed: false, detail: "agent-modified test files not reset: ['tests/admin/test_filters.py']" },
      { name: "patch_ordering", passed: true, detail: "agent patch applied before test_patch" },
      { name: "git_leakage", passed: true, detail: "no git remote and no commits beyond base ancestry" },
      { name: "timeout_policy", passed: true, detail: "run duration 1200s within swebench-lite ceiling 2700s" },
      { name: "grading_env_fingerprint", passed: true, detail: "manifest=requirements.txt lock=sha256:demo-lock-abc123" },
      { name: "patch_apply_dry_run", passed: true, detail: "git apply --check passed" },
      { name: "fail_to_pass_manifest", passed: true, detail: "1 fail-to-pass test(s): ['tests/admin/test_filters.py']" },
    ],
  },
};

function renderReceipt(receipt) {
  const overall = document.getElementById("overall");
  overall.textContent = receipt.overall;
  overall.className = `overall ${receipt.overall === "PASS" ? "pass" : "fail"}`;

  document.getElementById("instance-id").textContent = receipt.instance_id;
  document.getElementById("profile").textContent = receipt.harness_profile;

  const tbody = document.getElementById("gate-body");
  tbody.innerHTML = receipt.gates
    .map((gate) => {
      const rowClass = gate.passed ? "pass" : "fail";
      const status = gate.passed ? "PASS" : "FAIL";
      return `<tr class="${rowClass}">
        <td><code>${gate.name}</code></td>
        <td><span class="badge ${rowClass}">${status}</span></td>
        <td>${gate.detail}</td>
      </tr>`;
    })
    .join("");
}

document.getElementById("btn-pass").addEventListener("click", () => renderReceipt(RECEIPTS.pass));
document.getElementById("btn-fail").addEventListener("click", () => renderReceipt(RECEIPTS.fail));

renderReceipt(RECEIPTS.pass);
