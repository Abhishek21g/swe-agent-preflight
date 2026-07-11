"""Harness profile specs (timeout ceilings, required artifacts)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HarnessSpec:
    name: str
    timeout_seconds: int
    description: str


SPECS: dict[str, HarnessSpec] = {
    "swebench-lite": HarnessSpec(
        name="swebench-lite",
        timeout_seconds=45 * 60,
        description="SWE-bench agent eval (45m ceiling from Cognition technical report)",
    ),
    "swebench-devin": HarnessSpec(
        name="swebench-devin",
        timeout_seconds=45 * 60,
        description="Devin SWE-bench harness profile",
    ),
    "terminal-bench": HarnessSpec(
        name="terminal-bench",
        timeout_seconds=4 * 60 * 60,
        description="Long-horizon terminal agent profile (4h)",
    ),
}


def get_spec(name: str) -> HarnessSpec:
    if name not in SPECS:
        raise KeyError(
            f"Unknown spec {name!r}. Choose from: {', '.join(sorted(SPECS))}"
        )
    return SPECS[name]
