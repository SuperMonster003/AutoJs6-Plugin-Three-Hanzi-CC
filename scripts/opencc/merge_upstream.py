#!/usr/bin/env python3
"""Evaluate and optionally merge one automation-owned OpenCC upgrade pull request."""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import check_upstream
import verify_upstream


API_VERSION = "2022-11-28"
DEFAULT_API_ROOT = "https://api.github.com"
BASE_BRANCH = "master"
EXPECTED_BOT_LOGIN = "github-actions[bot]"
EXPECTED_BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
EXPECTED_SOURCE_URL = "https://github.com/BYVoid/OpenCC.git"
AUTOMATION_BRANCH_PATTERN = re.compile(r"automation/opencc-([0-9]+(?:\.[0-9]+){2})")
REPOSITORY_PATTERN = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
POLICY_MODES = {"paused", "pr-only", "merge", "release"}
FUSE_LABELS = {"do-not-merge", "automation-pause", "automation-paused"}
MAX_CONTENT_BYTES = 64 * 1024 * 1024
MAX_PAGES = 10
MAX_RESOURCE_GROWTH_BYTES = 512 * 1024
MAX_RESOURCE_GROWTH_PERCENT = 25
LICENSE_EVIDENCE_PATHS = (
    "LICENSE",
    "deps/marisa-0.3.1/COPYING.md",
    "deps/darts-clone-0.32h/COPYING.md",
    "deps/rapidjson-1.1.0/rapidjson/rapidjson.h",
)
EXPECTED_WORKFLOWS = {
    "build.yml": (
        "Build integrity",
        {
            "Unit tests and debug/release APKs",
            "Binder round trip (arm64-v8a)",
            "Binder round trip (x86_64)",
            "Binder round trip (x86_64, 16 KB pages)",
        },
    ),
    "markdown.yml": (
        "Markdown integrity",
        {"Check generated documentation"},
    ),
}


class AutomationError(Exception):
    """A controller or GitHub service error that must fail the workflow."""


class GateRejected(Exception):
    """An expected policy mismatch that leaves the pull request open."""


class GitHubHttpError(AutomationError):
    def __init__(self, status: int, url: str, detail: str) -> None:
        super().__init__(f"GitHub API returned HTTP {status} for {url}: {detail}")
        self.status = status
        self.url = url


@dataclass(frozen=True)
class WorkflowEvidence:
    workflow_file: str
    run_id: int
    run_url: str
    job_names: tuple[str, ...]


@dataclass(frozen=True)
class Evaluation:
    eligible: bool
    reason: str
    repository: str
    head_branch: str
    head_sha: str
    mode: str
    pull_number: int | None = None
    pull_url: str = ""
    version: str = ""
    base_sha: str = ""
    evidence: tuple[WorkflowEvidence, ...] = ()
    merged: bool = False
    merge_sha: str = ""
    branch_deleted: bool = False


class GitHubApi:
    """Small REST client with bounded responses and pagination."""

    def __init__(self, token: str, api_root: str = DEFAULT_API_ROOT) -> None:
        if not token.strip():
            raise AutomationError("GITHUB_TOKEN is required")
        self.token = token.strip()
        self.api_root = api_root.rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str | int] | None = None,
        body: dict[str, Any] | None = None,
        accept: str = "application/vnd.github+json",
        maximum_bytes: int = MAX_CONTENT_BYTES,
    ) -> bytes:
        encoded_query = urllib.parse.urlencode(query or {})
        url = f"{self.api_root}{path}"
        if encoded_query:
            url = f"{url}?{encoded_query}"
        data = None if body is None else json.dumps(body, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": accept,
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "AutoJs6-Plugin-OpenCC-merge-controller/1",
                "X-GitHub-Api-Version": API_VERSION,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read(maximum_bytes + 1)
        except urllib.error.HTTPError as error:
            try:
                detail = error.read(8193).decode("utf-8", errors="replace")[:8192]
            except OSError:
                detail = str(error)
            raise GitHubHttpError(error.code, url, detail or str(error)) from None
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise AutomationError(f"Unable to read GitHub API URL {url}: {error}") from None
        if len(payload) > maximum_bytes:
            raise AutomationError(f"GitHub API response exceeds {maximum_bytes} bytes: {url}")
        return payload

    def get_json(
        self,
        path: str,
        *,
        query: dict[str, str | int] | None = None,
    ) -> Any:
        payload = self._request("GET", path, query=query)
        try:
            return json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise AutomationError(f"GitHub API returned invalid JSON for {path}: {error}") from None

    def get_bytes(
        self,
        path: str,
        *,
        query: dict[str, str | int] | None = None,
        maximum_bytes: int = MAX_CONTENT_BYTES,
    ) -> bytes:
        return self._request(
            "GET",
            path,
            query=query,
            accept="application/vnd.github.raw+json",
            maximum_bytes=maximum_bytes,
        )

    def get_paginated(
        self,
        path: str,
        *,
        key: str | None = None,
        query: dict[str, str | int] | None = None,
    ) -> list[dict[str, Any]]:
        values: list[dict[str, Any]] = []
        for page in range(1, MAX_PAGES + 1):
            page_query = {**(query or {}), "per_page": 100, "page": page}
            response = self.get_json(path, query=page_query)
            page_values = response.get(key) if key is not None and isinstance(response, dict) else response
            if not isinstance(page_values, list) or any(not isinstance(value, dict) for value in page_values):
                raise AutomationError(f"GitHub API returned an invalid paginated response for {path}")
            values.extend(page_values)
            if len(page_values) < 100:
                return values
        raise AutomationError(f"GitHub API pagination exceeded {MAX_PAGES * 100} entries for {path}")

    def put_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        payload = self._request("PUT", path, body=body)
        try:
            value = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise AutomationError(f"GitHub API returned invalid JSON for PUT {path}: {error}") from None
        if not isinstance(value, dict):
            raise AutomationError(f"GitHub API returned a non-object response for PUT {path}")
        return value

    def delete(self, path: str) -> None:
        self._request("DELETE", path, maximum_bytes=1024)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise GateRejected(reason)


def safe_log_text(value: str, maximum_characters: int = 2000) -> str:
    single_line = " ".join(value.replace("\x00", "").splitlines())
    sanitized = "".join(character if ord(character) >= 32 else "?" for character in single_line)
    if len(sanitized) > maximum_characters:
        return sanitized[:maximum_characters].rstrip() + "…"
    return sanitized


def object_value(value: Any, description: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AutomationError(f"GitHub API returned malformed {description}")
    return value


def parse_lock(data: bytes, description: str) -> dict[str, str]:
    if len(data) > 16 * 1024:
        raise GateRejected(f"{description} exceeds the lock-file size limit")
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise GateRejected(f"{description} is not UTF-8: {error}") from None
    properties: dict[str, str] = {}
    for line_number, source_line in enumerate(lines, 1):
        line = source_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        require("=" in line, f"malformed property in {description} at line {line_number}")
        name, value = (part.strip() for part in line.split("=", 1))
        require(bool(name and value), f"empty property in {description} at line {line_number}")
        require(name not in properties, f"duplicate property {name!r} in {description}")
        properties[name] = value
    missing = verify_upstream.REQUIRED_PROPERTIES - properties.keys()
    unexpected = properties.keys() - verify_upstream.REQUIRED_PROPERTIES
    require(
        not missing and not unexpected,
        f"unexpected schema in {description}: missing={sorted(missing)}, unexpected={sorted(unexpected)}",
    )
    return properties


def validate_lock(properties: dict[str, str], description: str) -> str:
    version = properties["OPENCC_VERSION"]
    require(
        check_upstream.VERSION_PATTERN.fullmatch(version) is not None,
        f"unsupported version in {description}: {version!r}",
    )
    require(properties["OPENCC_TAG"] == f"ver.{version}", f"tag/version mismatch in {description}")
    require(
        SHA_PATTERN.fullmatch(properties["OPENCC_COMMIT"]) is not None,
        f"malformed commit in {description}",
    )
    require(properties["OPENCC_SOURCE_URL"] == EXPECTED_SOURCE_URL, f"unexpected source URL in {description}")
    require(
        properties["OPENCC_RESOURCE_ASSET"] == f"opencc-v{version}-resources.zip",
        f"resource/version mismatch in {description}",
    )
    require(
        SHA256_PATTERN.fullmatch(properties["OPENCC_RESOURCE_SHA256"]) is not None,
        f"malformed resource digest in {description}",
    )
    try:
        resource_size = int(properties["OPENCC_RESOURCE_SIZE"])
        manifest_version = int(properties["OPENCC_RESOURCE_MANIFEST_VERSION"])
    except ValueError:
        raise GateRejected(f"non-integer resource metadata in {description}") from None
    require(
        str(resource_size) == properties["OPENCC_RESOURCE_SIZE"] and 0 < resource_size <= MAX_CONTENT_BYTES,
        f"unsafe resource size in {description}",
    )
    require(
        str(manifest_version) == properties["OPENCC_RESOURCE_MANIFEST_VERSION"] and manifest_version == 1,
        f"unsupported resource manifest version in {description}",
    )
    return version


def encoded_contents_path(repository: str, path: str) -> str:
    return f"/repos/{repository}/contents/{urllib.parse.quote(path, safe='/')}"


def read_repository_file(
    api: GitHubApi,
    repository: str,
    path: str,
    ref: str,
    *,
    maximum_bytes: int = 16 * 1024,
) -> bytes:
    response = object_value(
        api.get_json(encoded_contents_path(repository, path), query={"ref": ref}),
        f"contents metadata for {path}@{ref}",
    )
    require(response.get("type") == "file", f"{path}@{ref} is not a regular file")
    require(response.get("encoding") == "base64", f"{path}@{ref} has unsupported contents encoding")
    content = response.get("content")
    require(isinstance(content, str), f"{path}@{ref} has no inline contents")
    try:
        data = base64.b64decode("".join(content.split()), validate=True)
    except (ValueError, TypeError) as error:
        raise GateRejected(f"{path}@{ref} has invalid base64 contents: {error}") from None
    require(len(data) <= maximum_bytes, f"{path}@{ref} exceeds {maximum_bytes} bytes")
    require(response.get("size") == len(data), f"{path}@{ref} size metadata is inconsistent")
    return data


def read_contents_metadata(api: GitHubApi, repository: str, path: str, ref: str) -> dict[str, Any]:
    return object_value(
        api.get_json(encoded_contents_path(repository, path), query={"ref": ref}),
        f"contents metadata for {path}@{ref}",
    )


def verify_submodule(
    api: GitHubApi,
    repository: str,
    ref: str,
    properties: dict[str, str],
    description: str,
) -> None:
    path = verify_upstream.SOURCE_DIRECTORY.as_posix()
    metadata = read_contents_metadata(api, repository, path, ref)
    require(metadata.get("type") in {"file", "submodule"}, f"{description} OpenCC path is not a submodule")
    require(metadata.get("sha") == properties["OPENCC_COMMIT"], f"{description} submodule commit mismatches lock")
    require(
        verify_upstream.normalized_repository_url(str(metadata.get("submodule_git_url", "")))
        == verify_upstream.normalized_repository_url(properties["OPENCC_SOURCE_URL"]),
        f"{description} submodule URL mismatches lock",
    )


def verify_resource_metadata(
    api: GitHubApi,
    repository: str,
    ref: str,
    properties: dict[str, str],
    description: str,
) -> None:
    path = (verify_upstream.ASSET_DIRECTORY / properties["OPENCC_RESOURCE_ASSET"]).as_posix()
    metadata = read_contents_metadata(api, repository, path, ref)
    require(metadata.get("type") == "file", f"{description} resource is not a regular file")
    require(metadata.get("size") == int(properties["OPENCC_RESOURCE_SIZE"]), f"{description} resource size mismatches lock")


def verify_head_resource(
    api: GitHubApi,
    repository: str,
    ref: str,
    properties: dict[str, str],
    official_archive: bytes,
) -> None:
    path = (verify_upstream.ASSET_DIRECTORY / properties["OPENCC_RESOURCE_ASSET"]).as_posix()
    expected_size = int(properties["OPENCC_RESOURCE_SIZE"])
    data = api.get_bytes(
        encoded_contents_path(repository, path),
        query={"ref": ref},
        maximum_bytes=expected_size,
    )
    require(len(data) == expected_size, "proposed resource byte size mismatches the head lock")
    require(hashlib.sha256(data).hexdigest() == properties["OPENCC_RESOURCE_SHA256"], "proposed resource digest mismatches the head lock")
    require(data == official_archive, "proposed resource bytes differ from the validated official GitHub asset")


def verify_resource_growth(base_properties: dict[str, str], head_properties: dict[str, str]) -> None:
    base_size = int(base_properties["OPENCC_RESOURCE_SIZE"])
    head_size = int(head_properties["OPENCC_RESOURCE_SIZE"])
    growth = head_size - base_size
    require(
        growth <= MAX_RESOURCE_GROWTH_BYTES,
        f"official resource grows by {growth} bytes, above the {MAX_RESOURCE_GROWTH_BYTES}-byte unattended limit",
    )
    require(
        head_size * 100 <= base_size * (100 + MAX_RESOURCE_GROWTH_PERCENT),
        f"official resource grows by more than {MAX_RESOURCE_GROWTH_PERCENT}%",
    )


def verify_license_evidence(
    api: GitHubApi,
    base_commit: str,
    head_commit: str,
) -> None:
    for path in LICENSE_EVIDENCE_PATHS:
        encoded_path = urllib.parse.quote(path, safe="/")
        endpoint = f"/repos/BYVoid/OpenCC/contents/{encoded_path}"
        base_data = api.get_bytes(endpoint, query={"ref": base_commit}, maximum_bytes=1024 * 1024)
        head_data = api.get_bytes(endpoint, query={"ref": head_commit}, maximum_bytes=1024 * 1024)
        require(base_data == head_data, f"declared third-party license evidence changed: {path}")


def current_base_sha(api: GitHubApi, repository: str) -> str:
    reference = object_value(
        api.get_json(f"/repos/{repository}/git/ref/heads/{BASE_BRANCH}"),
        f"{BASE_BRANCH} reference",
    )
    target = object_value(reference.get("object"), f"{BASE_BRANCH} reference target")
    sha = str(target.get("sha", "")).lower()
    if SHA_PATTERN.fullmatch(sha) is None:
        raise AutomationError(f"GitHub returned a malformed {BASE_BRANCH} SHA: {sha!r}")
    return sha


def latest_reviews_block_merge(reviews: list[dict[str, Any]]) -> str | None:
    latest: dict[str, tuple[str, int, str]] = {}
    for review in reviews:
        user = review.get("user")
        if not isinstance(user, dict):
            continue
        login = str(user.get("login", "")).lower()
        if not login:
            continue
        submitted_at = str(review.get("submitted_at", ""))
        try:
            review_id = int(review.get("id", 0))
        except (TypeError, ValueError):
            review_id = 0
        state = str(review.get("state", "")).upper()
        order = (submitted_at, review_id)
        previous = latest.get(login)
        if previous is None or order > (previous[0], previous[1]):
            latest[login] = (submitted_at, review_id, state)
    blockers = sorted(login for login, (_, _, state) in latest.items() if state == "CHANGES_REQUESTED")
    return ", ".join(blockers) if blockers else None


def verify_workflow(
    api: GitHubApi,
    repository: str,
    workflow_file: str,
    expected_name: str,
    expected_jobs: set[str],
    head_branch: str,
    head_sha: str,
) -> WorkflowEvidence:
    runs = api.get_paginated(
        f"/repos/{repository}/actions/workflows/{workflow_file}/runs",
        key="workflow_runs",
        query={
            "branch": head_branch,
            "event": "workflow_dispatch",
            "head_sha": head_sha,
        },
    )
    exact_runs = []
    for run in runs:
        repository_value = run.get("repository")
        head_repository_value = run.get("head_repository")
        path = str(run.get("path", "")).split("@", 1)[0]
        if (
            run.get("name") == expected_name
            and path == f".github/workflows/{workflow_file}"
            and run.get("event") == "workflow_dispatch"
            and run.get("head_branch") == head_branch
            and str(run.get("head_sha", "")).lower() == head_sha
            and isinstance(repository_value, dict)
            and str(repository_value.get("full_name", "")).lower() == repository.lower()
            and (
                head_repository_value is None
                or (
                    isinstance(head_repository_value, dict)
                    and str(head_repository_value.get("full_name", "")).lower() == repository.lower()
                )
            )
        ):
            exact_runs.append(run)
    require(bool(exact_runs), f"no exact explicitly dispatched {expected_name} run exists for head SHA {head_sha}")
    try:
        run = max(exact_runs, key=lambda item: int(item.get("id", 0)))
        run_id = int(run["id"])
    except (KeyError, TypeError, ValueError):
        raise AutomationError(f"GitHub returned a malformed {expected_name} workflow run") from None
    require(
        run.get("status") == "completed" and run.get("conclusion") == "success",
        f"latest exact {expected_name} run is not completed/success",
    )
    jobs = api.get_paginated(
        f"/repos/{repository}/actions/runs/{run_id}/jobs",
        key="jobs",
        query={"filter": "latest"},
    )
    actual_job_names = {str(job.get("name", "")) for job in jobs}
    require(
        len(jobs) == len(expected_jobs) and actual_job_names == expected_jobs,
        f"{expected_name} job inventory changed: expected={sorted(expected_jobs)}, actual={sorted(actual_job_names)}",
    )
    incomplete = sorted(
        str(job.get("name", ""))
        for job in jobs
        if job.get("status") != "completed" or job.get("conclusion") != "success"
    )
    require(not incomplete, f"{expected_name} contains non-success jobs: {incomplete}")
    run_url = str(run.get("html_url", ""))
    require(run_url.startswith(f"https://github.com/{repository}/actions/runs/"), f"unexpected {expected_name} run URL")
    return WorkflowEvidence(workflow_file, run_id, run_url, tuple(sorted(actual_job_names)))


def evaluate_candidate(
    api: GitHubApi,
    repository: str,
    head_branch: str,
    head_sha: str,
    mode: str,
    *,
    release_loader: Callable[[str, str], check_upstream.ValidatedRelease] = check_upstream.download_validated_release,
    upstream_api_base: str = check_upstream.DEFAULT_API_BASE,
) -> Evaluation:
    normalized_repository = repository.strip()
    normalized_branch = head_branch.strip()
    normalized_sha = head_sha.strip().lower()
    try:
        require(mode in POLICY_MODES, f"unsupported automation policy mode: {mode!r}")
        require(REPOSITORY_PATTERN.fullmatch(normalized_repository) is not None, "malformed repository identity")
        branch_match = AUTOMATION_BRANCH_PATTERN.fullmatch(normalized_branch)
        require(branch_match is not None, "head branch is not an exact automation/opencc-<semver> branch")
        require(SHA_PATTERN.fullmatch(normalized_sha) is not None, "head SHA is malformed")
        if mode == "paused":
            raise GateRejected("automation policy is paused")
        if mode == "release":
            raise AutomationError("release policy is not enabled until the isolated M4-D-4 controller is deployed")

        owner = normalized_repository.split("/", 1)[0]
        pulls = api.get_paginated(
            f"/repos/{normalized_repository}/pulls",
            query={"state": "open", "base": BASE_BRANCH, "head": f"{owner}:{normalized_branch}"},
        )
        require(len(pulls) == 1, f"expected exactly one matching open pull request, found {len(pulls)}")
        try:
            pull_number = int(pulls[0]["number"])
        except (KeyError, TypeError, ValueError):
            raise AutomationError("GitHub returned a malformed pull request number") from None
        pull = object_value(
            api.get_json(f"/repos/{normalized_repository}/pulls/{pull_number}"),
            f"pull request #{pull_number}",
        )
        user = object_value(pull.get("user"), f"pull request #{pull_number} author")
        base = object_value(pull.get("base"), f"pull request #{pull_number} base")
        head = object_value(pull.get("head"), f"pull request #{pull_number} head")
        base_repository = object_value(base.get("repo"), f"pull request #{pull_number} base repository")
        head_repository = object_value(head.get("repo"), f"pull request #{pull_number} head repository")
        require(pull.get("state") == "open" and pull.get("merged") is not True, "pull request is not open")
        require(pull.get("draft") is False, "pull request is a draft")
        require(user.get("login") == EXPECTED_BOT_LOGIN and user.get("type") == "Bot", "pull request author is not github-actions[bot]")
        require(base.get("ref") == BASE_BRANCH, f"pull request base is not {BASE_BRANCH}")
        require(str(base_repository.get("full_name", "")).lower() == normalized_repository.lower(), "pull request base repository differs from the target repository")
        require(head.get("ref") == normalized_branch, "pull request head branch differs from the triggering workflow")
        require(str(head.get("sha", "")).lower() == normalized_sha, "pull request head SHA differs from the triggering workflow")
        require(str(head_repository.get("full_name", "")).lower() == normalized_repository.lower(), "pull request head is not in the target repository")
        require(pull.get("commits") == 1, "automation pull request must contain exactly one commit")
        require(pull.get("changed_files") == 4, "automation pull request must contain exactly four changed paths")
        expected_pull_url = f"https://github.com/{normalized_repository}/pull/{pull_number}"
        require(pull.get("html_url") == expected_pull_url, "pull request URL differs from the target repository")
        labels = pull.get("labels")
        require(isinstance(labels, list), "pull request labels are malformed")
        label_names = {
            str(label.get("name", "")).strip().lower()
            for label in labels
            if isinstance(label, dict)
        }
        active_fuses = sorted(label_names & FUSE_LABELS)
        require(not active_fuses, f"pull request has automation fuse labels: {active_fuses}")

        base_sha = current_base_sha(api, normalized_repository)
        require(str(base.get("sha", "")).lower() == base_sha, f"pull request base SHA is stale relative to {BASE_BRANCH}")
        require(pull.get("mergeable") is True and pull.get("mergeable_state") == "clean", "pull request is not currently cleanly mergeable")

        commits = api.get_paginated(f"/repos/{normalized_repository}/pulls/{pull_number}/commits")
        require(len(commits) == 1, "GitHub commit list does not contain exactly one commit")
        commit = commits[0]
        commit_author = object_value(commit.get("author"), "automation commit author")
        commit_data = object_value(commit.get("commit"), "automation commit data")
        git_author = object_value(commit_data.get("author"), "automation Git author")
        parents = commit.get("parents")
        require(str(commit.get("sha", "")).lower() == normalized_sha, "automation commit SHA differs from pull request head")
        require(commit_author.get("login") == EXPECTED_BOT_LOGIN and commit_author.get("type") == "Bot", "automation commit author is not github-actions[bot]")
        require(git_author.get("name") == EXPECTED_BOT_LOGIN and git_author.get("email") == EXPECTED_BOT_EMAIL, "automation Git author identity is unexpected")
        require(isinstance(parents, list) and len(parents) == 1, "automation commit must have exactly one parent")
        require(isinstance(parents[0], dict) and str(parents[0].get("sha", "")).lower() == base_sha, "automation commit is not directly based on the current master SHA")

        base_lock = parse_lock(
            read_repository_file(api, normalized_repository, verify_upstream.LOCK_FILE, base_sha),
            "base OpenCC lock",
        )
        head_lock = parse_lock(
            read_repository_file(api, normalized_repository, verify_upstream.LOCK_FILE, normalized_sha),
            "head OpenCC lock",
        )
        base_version = validate_lock(base_lock, "base OpenCC lock")
        head_version = validate_lock(head_lock, "head OpenCC lock")
        require(branch_match.group(1) == head_version, "automation branch version differs from the head lock")
        require(check_upstream.version_tuple(head_version) > check_upstream.version_tuple(base_version), "head OpenCC version is not newer than the base lock")
        verify_resource_growth(base_lock, head_lock)
        expected_title = f"chore(deps): upgrade OpenCC to {head_version}"
        require(pull.get("title") == expected_title, "pull request title differs from the updater contract")
        require(commit_data.get("message") == expected_title, "automation commit message differs from the updater contract")

        files = api.get_paginated(f"/repos/{normalized_repository}/pulls/{pull_number}/files")
        actual_files = {
            str(file.get("filename", "")): str(file.get("status", ""))
            for file in files
        }
        expected_files = {
            verify_upstream.LOCK_FILE: "modified",
            verify_upstream.SOURCE_DIRECTORY.as_posix(): "modified",
            (verify_upstream.ASSET_DIRECTORY / base_lock["OPENCC_RESOURCE_ASSET"]).as_posix(): "removed",
            (verify_upstream.ASSET_DIRECTORY / head_lock["OPENCC_RESOURCE_ASSET"]).as_posix(): "added",
        }
        require(len(files) == 4 and actual_files == expected_files, f"pull request path/status inventory changed: expected={expected_files}, actual={actual_files}")
        require(all("previous_filename" not in file for file in files), "renamed files are not allowed in an automation update")

        verify_submodule(api, normalized_repository, base_sha, base_lock, "base")
        verify_submodule(api, normalized_repository, normalized_sha, head_lock, "head")
        verify_resource_metadata(api, normalized_repository, base_sha, base_lock, "base")
        verify_resource_metadata(api, normalized_repository, normalized_sha, head_lock, "head")

        try:
            release = release_loader(upstream_api_base.rstrip("/"), head_lock["OPENCC_SOURCE_URL"])
        except check_upstream.UpstreamCheckError as error:
            raise AutomationError(f"unable to revalidate the latest official OpenCC release: {error}") from None
        require(release.properties == head_lock, "head lock does not exactly match the latest validated official OpenCC release")
        verify_head_resource(api, normalized_repository, normalized_sha, head_lock, release.archive_data)
        verify_license_evidence(api, base_lock["OPENCC_COMMIT"], head_lock["OPENCC_COMMIT"])

        reviews = api.get_paginated(f"/repos/{normalized_repository}/pulls/{pull_number}/reviews")
        blocking_reviewers = latest_reviews_block_merge(reviews)
        require(blocking_reviewers is None, f"latest review requests changes from: {blocking_reviewers}")

        evidence = tuple(
            verify_workflow(
                api,
                normalized_repository,
                workflow_file,
                expected_name,
                expected_jobs,
                normalized_branch,
                normalized_sha,
            )
            for workflow_file, (expected_name, expected_jobs) in EXPECTED_WORKFLOWS.items()
        )
        return Evaluation(
            True,
            "all exact OpenCC auto-merge gates passed",
            normalized_repository,
            normalized_branch,
            normalized_sha,
            mode,
            pull_number,
            str(pull.get("html_url", "")),
            head_version,
            base_sha,
            evidence,
        )
    except GateRejected as error:
        return Evaluation(
            False,
            str(error),
            normalized_repository,
            normalized_branch,
            normalized_sha,
            mode,
        )


def merge_candidate(api: GitHubApi, evaluation: Evaluation) -> Evaluation:
    if not evaluation.eligible or evaluation.pull_number is None:
        raise AutomationError("refusing to merge an ineligible OpenCC pull request")
    if evaluation.mode != "merge":
        raise AutomationError(f"refusing write execution under automation mode {evaluation.mode!r}")
    if current_base_sha(api, evaluation.repository) != evaluation.base_sha:
        raise AutomationError(f"{BASE_BRANCH} advanced after the final eligibility evaluation")
    response = api.put_json(
        f"/repos/{evaluation.repository}/pulls/{evaluation.pull_number}/merge",
        {
            "commit_title": f"chore(deps): upgrade OpenCC to {evaluation.version} (#{evaluation.pull_number})",
            "commit_message": "Merged by the trusted OpenCC dependency controller after exact-SHA gates passed.",
            "sha": evaluation.head_sha,
            "merge_method": "squash",
        },
    )
    if response.get("merged") is not True:
        raise AutomationError(f"GitHub refused the eligible merge: {response.get('message', 'unknown reason')}")
    merge_sha = str(response.get("sha", "")).lower()
    if SHA_PATTERN.fullmatch(merge_sha) is None:
        raise AutomationError(f"GitHub returned a malformed merge commit SHA: {merge_sha!r}")

    branch_deleted = False
    encoded_branch = urllib.parse.quote(evaluation.head_branch, safe="/")
    try:
        reference = object_value(
            api.get_json(f"/repos/{evaluation.repository}/git/ref/heads/{encoded_branch}"),
            "post-merge automation branch reference",
        )
        target = object_value(reference.get("object"), "post-merge automation branch target")
        if str(target.get("sha", "")).lower() != evaluation.head_sha:
            raise AutomationError("automation branch changed after merge; refusing to delete it")
        api.delete(f"/repos/{evaluation.repository}/git/refs/heads/{encoded_branch}")
        branch_deleted = True
    except GitHubHttpError as error:
        if error.status != 404:
            raise
        branch_deleted = True

    return Evaluation(
        True,
        "eligible OpenCC upgrade was squash-merged and its unchanged automation branch was removed",
        evaluation.repository,
        evaluation.head_branch,
        evaluation.head_sha,
        evaluation.mode,
        evaluation.pull_number,
        evaluation.pull_url,
        evaluation.version,
        evaluation.base_sha,
        evaluation.evidence,
        True,
        merge_sha,
        branch_deleted,
    )


def append_workflow_outputs(evaluation: Evaluation) -> None:
    path_value = os.environ.get("GITHUB_OUTPUT", "").strip()
    if not path_value:
        return
    outputs = {
        "eligible": str(evaluation.eligible).lower(),
        "mode": evaluation.mode,
        "pr_number": "" if evaluation.pull_number is None else str(evaluation.pull_number),
        "head_branch": evaluation.head_branch,
        "head_sha": evaluation.head_sha,
        "version": evaluation.version,
        "base_sha": evaluation.base_sha,
        "merged": str(evaluation.merged).lower(),
        "merge_sha": evaluation.merge_sha,
    }
    with Path(path_value).open("a", encoding="utf-8") as output:
        for name, value in outputs.items():
            if "\n" in value or "\r" in value:
                raise AutomationError(f"workflow output {name} unexpectedly contains a newline")
            output.write(f"{name}={value}\n")


def append_workflow_summary(evaluation: Evaluation) -> None:
    path_value = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if not path_value:
        return
    with Path(path_value).open("a", encoding="utf-8") as summary:
        summary.write("## Trusted OpenCC merge controller\n\n")
        summary.write(f"- Policy: `{evaluation.mode}`\n")
        summary.write(f"- Decision: `{'eligible' if evaluation.eligible else 'rejected'}`\n")
        summary.write(f"- Head: `{evaluation.head_branch}` at `{evaluation.head_sha}`\n")
        if evaluation.pull_number is not None:
            summary.write(f"- Pull request: [#{evaluation.pull_number}]({evaluation.pull_url})\n")
            summary.write(f"- Base SHA: `{evaluation.base_sha}`\n")
        summary.write(f"- Reason: <code>{html.escape(safe_log_text(evaluation.reason))}</code>\n")
        for item in evaluation.evidence:
            summary.write(f"- Gate: [{item.workflow_file} run {item.run_id}]({item.run_url}) — {', '.join(item.job_names)}\n")
        if evaluation.merged:
            summary.write(f"- Merge commit: `{evaluation.merge_sha}`\n")
            summary.write(f"- Automation branch deleted: `{str(evaluation.branch_deleted).lower()}`\n")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""), help="owner/repository")
    parser.add_argument("--head-branch", required=True, help="exact automation pull-request branch")
    parser.add_argument("--head-sha", required=True, help="exact automation pull-request head SHA")
    parser.add_argument("--mode", default="pr-only", choices=sorted(POLICY_MODES), help="automation policy")
    parser.add_argument("--execute", action="store_true", help="perform the merge after a fresh evaluation")
    parser.add_argument("--api-root", default=DEFAULT_API_ROOT, help="GitHub REST API root")
    parser.add_argument("--upstream-api-base", default=check_upstream.DEFAULT_API_BASE, help="OpenCC GitHub API URL")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        api = GitHubApi(os.environ.get("GITHUB_TOKEN", ""), arguments.api_root)
        evaluation = evaluate_candidate(
            api,
            arguments.repository,
            arguments.head_branch,
            arguments.head_sha,
            arguments.mode,
            upstream_api_base=arguments.upstream_api_base,
        )
        if arguments.execute:
            if arguments.mode != "merge":
                raise AutomationError("--execute is permitted only when policy mode is merge")
            if not evaluation.eligible:
                raise AutomationError(f"final write-side evaluation rejected the pull request: {evaluation.reason}")
            evaluation = merge_candidate(api, evaluation)
        append_workflow_outputs(evaluation)
        append_workflow_summary(evaluation)
    except AutomationError as error:
        print(f"OPENCC_AUTO_MERGE_ERROR {error}", file=sys.stderr)
        return 1
    if evaluation.eligible:
        print(
            "OPENCC_AUTO_MERGE_ELIGIBLE "
            f"mode={evaluation.mode} pr={evaluation.pull_number} version={evaluation.version} "
            f"head={evaluation.head_sha} merged={str(evaluation.merged).lower()}",
        )
    else:
        safe_reason = safe_log_text(evaluation.reason)
        print(f"::warning::OpenCC auto-merge rejected: {safe_reason}")
        print(f"OPENCC_AUTO_MERGE_REJECTED mode={evaluation.mode} reason={safe_reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
