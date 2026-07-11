"""Instance YAML loading."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .errors import PreflightError


@dataclass
class InstanceConfig:
    instance_id: str
    repo: str
    base_commit: str
    problem_statement: str
    test_patch: str
    agent_patch: str
    test_files: list[str]
    fail_to_pass: list[str]
    run_duration_seconds: int
    mock_scenario: str = "pass"
    grading_env_hash: str = "sha256:demo-lock-abc123"
    has_git_remote: bool = False
    extra_commits: list[str] = field(default_factory=list)
    patch_ordering: str = "agent_then_test"
    test_files_reset: bool = True
    patch_applies_cleanly: bool = True
    dependency_manifest: str = "requirements.txt"

    @classmethod
    def from_yaml(cls, path: Path) -> "InstanceConfig":
        raw = yaml.safe_load(path.read_text())
        if not isinstance(raw, dict):
            raise PreflightError(f"Invalid instance YAML: {path}")
        return cls.from_dict(raw)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "InstanceConfig":
        required = ["instance_id", "repo", "base_commit", "test_patch"]
        missing = [k for k in required if k not in raw]
        if missing:
            raise PreflightError(f"Instance missing fields: {missing}")

        test_files = raw.get("test_files") or _parse_test_files(raw.get("test_patch", ""))
        fail_to_pass = raw.get("fail_to_pass") or test_files

        return cls(
            instance_id=str(raw["instance_id"]),
            repo=str(raw["repo"]),
            base_commit=str(raw["base_commit"]),
            problem_statement=str(raw.get("problem_statement", "")),
            test_patch=str(raw["test_patch"]),
            agent_patch=str(raw.get("agent_patch", "")),
            test_files=list(test_files),
            fail_to_pass=list(fail_to_pass),
            run_duration_seconds=int(raw.get("run_duration_seconds", 600)),
            mock_scenario=str(raw.get("mock_scenario", "pass")),
            grading_env_hash=str(raw.get("grading_env_hash", "sha256:demo-lock-abc123")),
            has_git_remote=bool(raw.get("has_git_remote", False)),
            extra_commits=list(raw.get("extra_commits", [])),
            patch_ordering=str(raw.get("patch_ordering", "agent_then_test")),
            test_files_reset=bool(raw.get("test_files_reset", True)),
            patch_applies_cleanly=bool(raw.get("patch_applies_cleanly", True)),
            dependency_manifest=str(raw.get("dependency_manifest", "requirements.txt")),
        )


def _parse_test_files(test_patch: str) -> list[str]:
    import re

    return re.findall(r"--- a/(.*)", test_patch)
