from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIRECTORY))

import wait_upstream_gates  # noqa: E402


REPOSITORY = "Owner/Repo"
BRANCH = "automation/opencc-1.5.0"
HEAD_SHA = "b" * 40


class Clock:
    def __init__(self) -> None:
        self.value = 0.0

    def monotonic(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += seconds


class FixtureApi:
    def __init__(self) -> None:
        self.branch_sha = HEAD_SHA
        self.workflows = {
            "build.yml": ("Build integrity", 100, 101, "success"),
            "markdown.yml": ("Markdown integrity", 200, 201, "failure"),
        }
        self.include_new_runs = True

    def get_json(self, path: str, *, query: dict[str, str | int] | None = None) -> Any:
        if path == f"/repos/{REPOSITORY}":
            return {"full_name": REPOSITORY, "default_branch": "master"}
        workflow_prefix = f"/repos/{REPOSITORY}/actions/workflows/"
        if path.startswith(workflow_prefix):
            workflow_file = path.removeprefix(workflow_prefix)
            name = self.workflows[workflow_file][0]
            return {
                "name": name,
                "path": f".github/workflows/{workflow_file}",
                "state": "active",
            }
        if path == f"/repos/{REPOSITORY}/git/ref/heads/{BRANCH}":
            return {"object": {"type": "commit", "sha": self.branch_sha}}
        raise AssertionError(f"unexpected get_json call: {path}, {query}")

    def get_paginated(
        self,
        path: str,
        *,
        key: str | None = None,
        query: dict[str, str | int] | None = None,
    ) -> list[dict[str, Any]]:
        prefix = f"/repos/{REPOSITORY}/actions/workflows/"
        workflow_file = path.removeprefix(prefix).removesuffix("/runs")
        name, old_id, new_id, conclusion = self.workflows[workflow_file]
        old = self.run(workflow_file, name, old_id, "a" * 40, "success")
        if query == {"event": "workflow_dispatch"}:
            return [old]
        if query != {"event": "workflow_dispatch", "branch": BRANCH, "head_sha": HEAD_SHA}:
            raise AssertionError(f"unexpected run query: {path}, {key}, {query}")
        if not self.include_new_runs:
            return [old]
        return [self.run(workflow_file, name, new_id, HEAD_SHA, conclusion), old]

    @staticmethod
    def run(
        workflow_file: str,
        name: str,
        run_id: int,
        source_sha: str,
        conclusion: str,
    ) -> dict[str, Any]:
        return {
            "id": run_id,
            "name": name,
            "path": f".github/workflows/{workflow_file}@{BRANCH}",
            "event": "workflow_dispatch",
            "head_branch": BRANCH,
            "head_sha": source_sha,
            "status": "completed",
            "conclusion": conclusion,
            "repository": {"full_name": REPOSITORY},
            "head_repository": {"full_name": REPOSITORY},
            "html_url": f"https://github.com/{REPOSITORY}/actions/runs/{run_id}",
        }


class WaitUpstreamGatesTest(unittest.TestCase):
    def test_snapshot_records_latest_explicit_dispatch_run_ids(self) -> None:
        self.assertEqual(
            {"build": 100, "markdown": 200},
            wait_upstream_gates.snapshot_watermarks(FixtureApi(), REPOSITORY),  # type: ignore[arg-type]
        )

    def test_wait_binds_new_exact_runs_and_preserves_failure_for_controller(self) -> None:
        api = FixtureApi()
        evidence = wait_upstream_gates.wait_for_runs(
            api,  # type: ignore[arg-type]
            REPOSITORY,
            BRANCH,
            HEAD_SHA,
            {"build": 100, "markdown": 200},
            timeout_seconds=10,
            poll_seconds=1,
        )
        self.assertEqual((101, 201), tuple(item.run_id for item in evidence))
        self.assertEqual(("success", "failure"), tuple(item.conclusion for item in evidence))

    def test_wait_rejects_branch_movement_after_gates(self) -> None:
        api = FixtureApi()
        calls = 0
        original = api.get_json

        def moving_get(path: str, *, query: dict[str, str | int] | None = None) -> Any:
            nonlocal calls
            value = original(path, query=query)
            if path.endswith(BRANCH):
                calls += 1
                if calls == 2:
                    return {"object": {"type": "commit", "sha": "c" * 40}}
            return value

        api.get_json = moving_get  # type: ignore[method-assign]
        with self.assertRaisesRegex(wait_upstream_gates.GateWaitError, "moved while gates ran"):
            wait_upstream_gates.wait_for_runs(
                api,  # type: ignore[arg-type]
                REPOSITORY,
                BRANCH,
                HEAD_SHA,
                {"build": 100, "markdown": 200},
                timeout_seconds=10,
                poll_seconds=1,
            )

    def test_wait_times_out_without_a_new_exact_run(self) -> None:
        api = FixtureApi()
        api.include_new_runs = False
        clock = Clock()
        with self.assertRaisesRegex(wait_upstream_gates.GateWaitError, "timed out.*build, markdown"):
            wait_upstream_gates.wait_for_runs(
                api,  # type: ignore[arg-type]
                REPOSITORY,
                BRANCH,
                HEAD_SHA,
                {"build": 100, "markdown": 200},
                timeout_seconds=2,
                poll_seconds=1,
                monotonic=clock.monotonic,
                sleep=clock.sleep,
            )

    def test_wait_rejects_untrusted_run_repository(self) -> None:
        api = FixtureApi()
        original = api.get_paginated

        def untrusted_pages(
            path: str,
            *,
            key: str | None = None,
            query: dict[str, str | int] | None = None,
        ) -> list[dict[str, Any]]:
            values = original(path, key=key, query=query)
            if query and query.get("head_sha") == HEAD_SHA and values[0].get("head_sha") == HEAD_SHA:
                values[0]["repository"] = {"full_name": "Attacker/Fork"}
            return values

        api.get_paginated = untrusted_pages  # type: ignore[method-assign]
        with self.assertRaisesRegex(wait_upstream_gates.GateWaitError, "another repository"):
            wait_upstream_gates.wait_for_runs(
                api,  # type: ignore[arg-type]
                REPOSITORY,
                BRANCH,
                HEAD_SHA,
                {"build": 100, "markdown": 200},
                timeout_seconds=10,
                poll_seconds=1,
            )

    def test_snapshot_rejects_workflow_metadata_drift(self) -> None:
        api = FixtureApi()
        api.workflows["markdown.yml"] = ("Renamed", 200, 201, "success")
        with self.assertRaisesRegex(wait_upstream_gates.GateWaitError, "workflow name changed"):
            wait_upstream_gates.snapshot_watermarks(api, REPOSITORY)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
