#!/usr/bin/env python3
"""Bind upstream PR orchestration to newly dispatched, exact-SHA workflow runs."""

from __future__ import annotations

import argparse
import html
import os
import sys
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import merge_upstream


BASE_BRANCH = "master"
DEFAULT_TIMEOUT_SECONDS = 45 * 60
DEFAULT_POLL_SECONDS = 15
ACTIVE_STATUSES = {"queued", "in_progress", "pending", "waiting", "requested"}
TERMINAL_CONCLUSIONS = {
    "action_required",
    "cancelled",
    "failure",
    "neutral",
    "skipped",
    "stale",
    "startup_failure",
    "success",
    "timed_out",
}
WORKFLOW_CONTRACTS = (
    ("build", "build.yml", "Build integrity"),
    ("markdown", "markdown.yml", "Markdown integrity"),
)


class GateWaitError(Exception):
    """A workflow identity, service, or timeout failure that stops orchestration."""


@dataclass(frozen=True)
class RunEvidence:
    key: str
    workflow_file: str
    run_id: int
    conclusion: str
    url: str


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise GateWaitError(reason)


def positive_integer(value: Any, description: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise GateWaitError(f"GitHub returned a malformed {description}") from None
    require(result > 0, f"GitHub returned a non-positive {description}")
    return result


def canonical_repository(value: str) -> str:
    repository = value.strip()
    require(
        merge_upstream.REPOSITORY_PATTERN.fullmatch(repository) is not None,
        "malformed repository identity",
    )
    return repository


def canonical_branch(value: str) -> str:
    branch = value.strip()
    require(
        merge_upstream.AUTOMATION_BRANCH_PATTERN.fullmatch(branch) is not None,
        "head branch is not an exact automation/opencc-<semver> branch",
    )
    return branch


def canonical_sha(value: str) -> str:
    source_sha = value.strip().lower()
    require(merge_upstream.SHA_PATTERN.fullmatch(source_sha) is not None, "malformed head SHA")
    return source_sha


def canonical_watermark(value: int, description: str) -> int:
    require(value >= 0, f"{description} must not be negative")
    return value


def object_value(value: Any, description: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GateWaitError(f"GitHub returned malformed {description}")
    return value


def validate_repository(api: merge_upstream.GitHubApi, repository: str) -> None:
    value = object_value(api.get_json(f"/repos/{repository}"), "repository metadata")
    require(str(value.get("full_name", "")) == repository, "GitHub repository identity changed")
    require(value.get("default_branch") == BASE_BRANCH, "GitHub default branch changed")


def validate_workflow_metadata(
    api: merge_upstream.GitHubApi,
    repository: str,
    workflow_file: str,
    expected_name: str,
) -> None:
    value = object_value(
        api.get_json(f"/repos/{repository}/actions/workflows/{workflow_file}"),
        f"{workflow_file} workflow metadata",
    )
    require(value.get("name") == expected_name, f"workflow name changed for {workflow_file}")
    require(
        value.get("path") == f".github/workflows/{workflow_file}",
        f"workflow path changed for {workflow_file}",
    )
    require(value.get("state") == "active", f"workflow is not active: {workflow_file}")


def list_dispatched_runs(
    api: merge_upstream.GitHubApi,
    repository: str,
    workflow_file: str,
    *,
    branch: str | None = None,
    source_sha: str | None = None,
) -> list[dict[str, Any]]:
    query: dict[str, str | int] = {"event": "workflow_dispatch"}
    if branch is not None:
        query["branch"] = branch
    if source_sha is not None:
        query["head_sha"] = source_sha
    return api.get_paginated(
        f"/repos/{repository}/actions/workflows/{workflow_file}/runs",
        key="workflow_runs",
        query=query,
    )


def snapshot_watermarks(api: merge_upstream.GitHubApi, repository: str) -> dict[str, int]:
    repository = canonical_repository(repository)
    validate_repository(api, repository)
    watermarks: dict[str, int] = {}
    for key, workflow_file, expected_name in WORKFLOW_CONTRACTS:
        validate_workflow_metadata(api, repository, workflow_file, expected_name)
        watermarks[key] = max(
            (
                positive_integer(run.get("id"), f"listed {expected_name} run ID")
                for run in list_dispatched_runs(api, repository, workflow_file)
            ),
            default=0,
        )
    return watermarks


def remote_branch_sha(api: merge_upstream.GitHubApi, repository: str, branch: str) -> str:
    encoded_branch = urllib.parse.quote(branch, safe="/")
    reference = object_value(
        api.get_json(f"/repos/{repository}/git/ref/heads/{encoded_branch}"),
        "automation branch reference",
    )
    target = object_value(reference.get("object"), "automation branch target")
    require(target.get("type") == "commit", "automation branch does not target a commit")
    return canonical_sha(str(target.get("sha", "")))


def validate_run_identity(
    run: dict[str, Any],
    repository: str,
    branch: str,
    source_sha: str,
    workflow_file: str,
    expected_name: str,
) -> int:
    run_id = positive_integer(run.get("id"), f"{expected_name} run ID")
    require(run.get("name") == expected_name, f"unexpected workflow name for run {run_id}")
    require(
        str(run.get("path", "")).split("@", 1)[0] == f".github/workflows/{workflow_file}",
        f"unexpected workflow path for run {run_id}",
    )
    require(run.get("event") == "workflow_dispatch", f"run {run_id} was not explicitly dispatched")
    require(run.get("head_branch") == branch, f"run {run_id} used another head branch")
    require(str(run.get("head_sha", "")).lower() == source_sha, f"run {run_id} used another head SHA")
    run_repository = object_value(run.get("repository"), f"run {run_id} repository")
    require(str(run_repository.get("full_name", "")) == repository, f"run {run_id} belongs to another repository")
    head_repository = run.get("head_repository")
    if head_repository is not None:
        require(
            str(object_value(head_repository, f"run {run_id} head repository").get("full_name", ""))
            == repository,
            f"run {run_id} has an untrusted head repository",
        )
    expected_url = f"https://github.com/{repository}/actions/runs/{run_id}"
    require(run.get("html_url") == expected_url, f"unexpected URL for run {run_id}")
    return run_id


def find_new_exact_run(
    api: merge_upstream.GitHubApi,
    repository: str,
    branch: str,
    source_sha: str,
    workflow_file: str,
    expected_name: str,
    watermark: int,
) -> dict[str, Any] | None:
    exact_runs: list[dict[str, Any]] = []
    for run in list_dispatched_runs(
        api,
        repository,
        workflow_file,
        branch=branch,
        source_sha=source_sha,
    ):
        run_id = positive_integer(run.get("id"), f"listed {expected_name} run ID")
        if run_id <= watermark:
            continue
        if run.get("head_branch") != branch or str(run.get("head_sha", "")).lower() != source_sha:
            continue
        validate_run_identity(run, repository, branch, source_sha, workflow_file, expected_name)
        exact_runs.append(run)
    return max(exact_runs, key=lambda value: int(value["id"])) if exact_runs else None


def wait_for_runs(
    api: merge_upstream.GitHubApi,
    repository: str,
    branch: str,
    source_sha: str,
    watermarks: dict[str, int],
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    poll_seconds: int = DEFAULT_POLL_SECONDS,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[RunEvidence, ...]:
    repository = canonical_repository(repository)
    branch = canonical_branch(branch)
    source_sha = canonical_sha(source_sha)
    require(timeout_seconds > 0, "timeout must be positive")
    require(poll_seconds > 0, "poll interval must be positive")
    require(set(watermarks) == {item[0] for item in WORKFLOW_CONTRACTS}, "workflow watermark inventory changed")
    normalized_watermarks = {
        key: canonical_watermark(watermarks[key], f"{key} watermark")
        for key, _, _ in WORKFLOW_CONTRACTS
    }

    validate_repository(api, repository)
    for _, workflow_file, expected_name in WORKFLOW_CONTRACTS:
        validate_workflow_metadata(api, repository, workflow_file, expected_name)
    require(remote_branch_sha(api, repository, branch) == source_sha, "automation branch moved before gate wait")

    deadline = monotonic() + timeout_seconds
    pending = {key: (workflow_file, expected_name) for key, workflow_file, expected_name in WORKFLOW_CONTRACTS}
    evidence: dict[str, RunEvidence] = {}
    while pending and monotonic() <= deadline:
        for key, (workflow_file, expected_name) in tuple(pending.items()):
            run = find_new_exact_run(
                api,
                repository,
                branch,
                source_sha,
                workflow_file,
                expected_name,
                normalized_watermarks[key],
            )
            if run is None:
                continue
            run_id = validate_run_identity(
                run,
                repository,
                branch,
                source_sha,
                workflow_file,
                expected_name,
            )
            status = str(run.get("status", ""))
            if status == "completed":
                conclusion = str(run.get("conclusion", ""))
                require(
                    conclusion in TERMINAL_CONCLUSIONS,
                    f"run {run_id} has an unexpected terminal conclusion: {conclusion!r}",
                )
                evidence[key] = RunEvidence(key, workflow_file, run_id, conclusion, str(run["html_url"]))
                del pending[key]
            else:
                require(status in ACTIVE_STATUSES, f"run {run_id} has an unexpected status: {status!r}")
        if pending:
            sleep(float(poll_seconds))

    if pending:
        missing = ", ".join(sorted(pending))
        raise GateWaitError(f"timed out waiting for exact dispatched workflow runs: {missing}")
    require(remote_branch_sha(api, repository, branch) == source_sha, "automation branch moved while gates ran")
    return tuple(evidence[key] for key, _, _ in WORKFLOW_CONTRACTS)


def append_outputs(values: dict[str, int]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT", "").strip()
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as output:
        for key, value in values.items():
            output.write(f"{key}_watermark={value}\n")


def append_snapshot_summary(values: dict[str, int]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if not summary_path:
        return
    with Path(summary_path).open("a", encoding="utf-8") as summary:
        summary.write("## OpenCC dispatched-gate watermarks\n\n")
        for key, value in values.items():
            summary.write(f"- `{html.escape(key)}`: `{value}`\n")


def append_wait_summary(branch: str, source_sha: str, evidence: tuple[RunEvidence, ...]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if not summary_path:
        return
    with Path(summary_path).open("a", encoding="utf-8") as summary:
        summary.write("## Exact OpenCC PR gates reached a terminal state\n\n")
        summary.write(f"- Head: `{html.escape(branch)}` at `{source_sha}`\n")
        for item in evidence:
            summary.write(
                f"- [{html.escape(item.workflow_file)} run {item.run_id}]({item.url}): "
                f"`{html.escape(item.conclusion)}`\n"
            )
        summary.write("- Final eligibility and complete job inventories are checked by the trusted merge controller.\n")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""), help="owner/repository")
    parser.add_argument("--api-root", default=merge_upstream.DEFAULT_API_ROOT, help="GitHub REST API root")
    subparsers = parser.add_subparsers(dest="operation", required=True)

    subparsers.add_parser("snapshot", help="record pre-dispatch workflow run watermarks")

    wait_parser = subparsers.add_parser("wait", help="wait for new exact-head runs to become terminal")
    wait_parser.add_argument("--head-branch", required=True, help="exact automation pull-request branch")
    wait_parser.add_argument("--head-sha", required=True, help="exact automation pull-request head SHA")
    wait_parser.add_argument("--build-watermark", required=True, type=int)
    wait_parser.add_argument("--markdown-watermark", required=True, type=int)
    wait_parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    wait_parser.add_argument("--poll-seconds", type=int, default=DEFAULT_POLL_SECONDS)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        api = merge_upstream.GitHubApi(os.environ.get("GITHUB_TOKEN", ""), arguments.api_root)
        if arguments.operation == "snapshot":
            watermarks = snapshot_watermarks(api, arguments.repository)
            append_outputs(watermarks)
            append_snapshot_summary(watermarks)
            print(
                "OPENCC_GATE_WATERMARKS "
                + " ".join(f"{key}={value}" for key, value in watermarks.items())
            )
        else:
            evidence = wait_for_runs(
                api,
                arguments.repository,
                arguments.head_branch,
                arguments.head_sha,
                {
                    "build": arguments.build_watermark,
                    "markdown": arguments.markdown_watermark,
                },
                timeout_seconds=arguments.timeout_seconds,
                poll_seconds=arguments.poll_seconds,
            )
            append_wait_summary(arguments.head_branch, arguments.head_sha, evidence)
            print(
                "OPENCC_GATES_TERMINAL "
                + " ".join(
                    f"{item.key}_run={item.run_id} {item.key}_conclusion={item.conclusion}"
                    for item in evidence
                )
            )
    except (GateWaitError, merge_upstream.AutomationError) as error:
        print(f"OPENCC_GATE_WAIT_ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
