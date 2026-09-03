#!/usr/bin/env python3
"""Dispatch exact-SHA release gates and create a verified draft GitHub Release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci import verify_apk_variants  # noqa: E402
from scripts.release.prepare_candidate import (  # noqa: E402
    CANDIDATE_MANIFEST,
    EXPECTED_REPOSITORY,
    CandidateBaseline,
    candidate_manifest_data,
    canonical_certificate_sha256,
    canonical_source_sha,
    current_version_build,
    load_candidate_baseline,
    verify_bundle_documents,
    verify_bundle_inventory,
    verify_git_source,
    verify_no_signing_material,
    verify_package_sizes,
    verify_version_progression,
    version_tuple,
)
from scripts.release.prepare_release import (  # noqa: E402
    ABI_ORDER,
    PackageRecord,
    ReleaseContext,
    ReleaseError,
    collect_records,
    find_apksigner,
    load_release_context,
    released_apk_pattern,
    sha256,
    verify_signatures,
)


API_VERSION = "2022-11-28"
DEFAULT_API_ROOT = "https://api.github.com"
DEFAULT_UPLOAD_ROOT = "https://uploads.github.com"
BASE_BRANCH = "master"
RELEASE_WORKFLOW_FILE = "opencc-release.yml"
RELEASE_WORKFLOW_NAME = "OpenCC trusted release"
EXPECTED_BOT_LOGIN = "github-actions[bot]"
MAX_API_BYTES = 64 * 1024 * 1024
MAX_JSON_BYTES = 256 * 1024
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
MAX_RELEASE_NOTES_BYTES = 256 * 1024
MAX_PAGES = 10
DEFAULT_GATE_TIMEOUT_SECONDS = 50 * 60
DEFAULT_POLL_SECONDS = 10
POSITIVE_INTEGER_PATTERN = re.compile(r"[1-9][0-9]*")
ARTIFACT_DIGEST_PATTERN = re.compile(r"(?:sha256:)?([0-9a-f]{64})")


@dataclass(frozen=True)
class WorkflowContract:
    key: str
    file: str
    name: str
    jobs: frozenset[str]


WORKFLOW_CONTRACTS = (
    WorkflowContract(
        "build",
        "build.yml",
        "Build integrity",
        frozenset(
            {
                "Unit tests and debug/release APKs",
                "Debug/release runtime (x86, API 24 minSdk)",
                "Binder round trip (arm64-v8a)",
                "Binder round trip (x86_64)",
                "Binder round trip (x86_64, 16 KB pages)",
            },
        ),
    ),
    WorkflowContract(
        "markdown",
        "markdown.yml",
        "Markdown integrity",
        frozenset({"Check generated documentation"}),
    ),
)
WORKFLOW_BY_KEY = {contract.key: contract for contract in WORKFLOW_CONTRACTS}


class DraftError(Exception):
    """A local or remote release invariant failed."""


class GitHubHttpError(DraftError):
    def __init__(self, status: int, url: str, detail: str) -> None:
        super().__init__(f"GitHub API returned HTTP {status} for {url}: {detail}")
        self.status = status
        self.url = url


@dataclass(frozen=True)
class WorkflowEvidence:
    contract: WorkflowContract
    run_id: int
    run_url: str
    job_names: tuple[str, ...]


@dataclass(frozen=True)
class CandidateEvidence:
    context: ReleaseContext
    baseline: CandidateBaseline
    source_sha: str
    version_build: int
    signer_digest: str
    records: tuple[PackageRecord, ...]
    bundle: Path
    manifest_sha256: str

    @property
    def tag(self) -> str:
        return f"v{self.context.version_name}"

    @property
    def artifact_name(self) -> str:
        return (
            f"opencc-signed-candidate-v{self.context.version_name}-"
            f"build{self.version_build}-{self.source_sha[:12]}"
        )


@dataclass(frozen=True)
class ReleaseAsset:
    path: Path
    name: str
    size: int
    sha256: str
    content_type: str


@dataclass(frozen=True)
class DraftPlan:
    candidate: CandidateEvidence
    baseline_release_id: int
    notes: str
    assets: tuple[ReleaseAsset, ...]


@dataclass(frozen=True)
class DraftResult:
    release_id: int
    release_url: str
    tag: str
    source_sha: str
    assets: tuple[ReleaseAsset, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DraftError(message)


def object_value(value: Any, description: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DraftError(f"GitHub returned malformed {description}")
    return value


def positive_integer(value: object, description: str) -> int:
    text = str(value)
    require(POSITIVE_INTEGER_PATTERN.fullmatch(text) is not None, f"Malformed {description}")
    return int(text)


def canonical_artifact_digest(value: object) -> str:
    match = ARTIFACT_DIGEST_PATTERN.fullmatch(value) if isinstance(value, str) else None
    require(match is not None, "Malformed candidate artifact digest")
    return f"sha256:{match.group(1)}"


def canonical_repository(value: str) -> str:
    require(value == EXPECTED_REPOSITORY, f"Unexpected repository: {value!r}")
    return value


def read_json_object(path: Path, description: str) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), f"Missing regular {description}: {path}")
    require(path.stat().st_size <= MAX_JSON_BYTES, f"{description} exceeds {MAX_JSON_BYTES} bytes")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DraftError(f"Invalid {description}: {error}") from None
    require(isinstance(value, dict), f"{description} root must be an object")
    return value


def git_is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise DraftError(f"git merge-base failed: {result.stderr.strip()}")


def verify_zip_alignment(records: list[PackageRecord], zipalign: Path) -> None:
    zipalign = zipalign.resolve()
    require(zipalign.is_file(), f"zipalign does not exist: {zipalign}")
    for record in records:
        result = subprocess.run(
            [str(zipalign), "-c", "-P", "16", "-v", "4", str(record.source)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        require(result.returncode == 0, f"zipalign verification failed for {record.filename}")


def verify_deep_apk_content(records: list[PackageRecord]) -> None:
    verify_apk_variants.verify_api_artifact()
    upstream = verify_apk_variants.load_upstream_lock()
    require([record.abi for record in records] == list(ABI_ORDER), "Draft package order is not canonical")
    for record in records:
        expected_abis = verify_apk_variants.EXPECTED_VARIANTS[record.abi]
        actual_abis, minimum_alignment = verify_apk_variants.verify_apk(
            record.source,
            expected_abis,
            upstream,
        )
        require(actual_abis == expected_abis, f"Deep ABI verification changed for {record.filename}")
        require(
            minimum_alignment >= verify_apk_variants.MINIMUM_ELF_ALIGNMENT,
            f"ELF alignment regressed in {record.filename}",
        )


def verify_draft_progression(
    context: ReleaseContext,
    version_build: int,
    baseline: CandidateBaseline,
) -> None:
    verify_version_progression(context, version_build, baseline)
    require(
        version_tuple(context.version_name) > version_tuple(baseline.version_name),
        f"Draft version {context.version_name} must be newer than published baseline {baseline.version_name}",
    )
    require(
        version_build > baseline.version_build,
        f"Draft build {version_build} must be newer than published baseline build {baseline.version_build}",
    )


def verify_candidate_bundle(
    root: Path,
    bundle: Path,
    source_sha: str,
    expected_signer_digest: str,
    apksigner: Path,
    zipalign: Path,
) -> CandidateEvidence:
    root = root.resolve()
    bundle = bundle.resolve()
    source_sha = canonical_source_sha(source_sha)
    expected_signer_digest = canonical_certificate_sha256(
        expected_signer_digest,
        "expected signer certificate SHA-256",
    )
    require(bundle.is_dir() and not bundle.is_symlink(), f"Candidate bundle is not a regular directory: {bundle}")
    context = load_release_context(root)
    version_build = current_version_build(root)
    baseline = load_candidate_baseline(root / "scripts" / "release" / "candidate-baseline.json")
    verify_git_source(root, source_sha, baseline)
    require(
        git_is_ancestor(root, baseline.source_sha, source_sha),
        "Published baseline is not an ancestor of the draft source",
    )
    verify_draft_progression(context, version_build, baseline)
    require(
        expected_signer_digest == baseline.signer_certificate_sha256,
        "Environment signer certificate differs from the published baseline",
    )

    records, foreign_versions = collect_records(bundle, context)
    require(not foreign_versions, f"Draft bundle contains foreign-version APKs: {foreign_versions}")
    signer_digest = verify_signatures(records, find_apksigner(apksigner))
    require(signer_digest == expected_signer_digest, "Draft APK signer differs from the expected certificate")
    verify_no_signing_material(records)
    maximum_sizes = verify_package_sizes(records, baseline)
    verify_bundle_documents(context, records, signer_digest, bundle)
    verify_bundle_inventory(bundle, records)
    verify_deep_apk_content(records)
    verify_zip_alignment(records, zipalign)

    manifest_path = bundle / CANDIDATE_MANIFEST
    actual_manifest = read_json_object(manifest_path, CANDIDATE_MANIFEST)
    expected_manifest = candidate_manifest_data(
        context,
        bundle,
        source_sha,
        version_build,
        signer_digest,
        records,
        baseline,
        maximum_sizes,
    )
    require(actual_manifest == expected_manifest, "CANDIDATE.json differs from the independently verified bundle")
    return CandidateEvidence(
        context,
        baseline,
        source_sha,
        version_build,
        signer_digest,
        tuple(records),
        bundle,
        sha256(manifest_path),
    )


class GitHubApi:
    """Bounded GitHub REST client used only by the trusted workflow."""

    def __init__(
        self,
        token: str,
        api_root: str = DEFAULT_API_ROOT,
        upload_root: str = DEFAULT_UPLOAD_ROOT,
    ) -> None:
        require(bool(token.strip()), "GITHUB_TOKEN is required")
        self.token = token.strip()
        self.api_root = api_root.rstrip("/")
        self.upload_root = upload_root.rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, object] | None = None,
        json_body: dict[str, Any] | None = None,
        raw_body: bytes | None = None,
        content_type: str = "application/json",
        expected_statuses: frozenset[int] = frozenset({200}),
        maximum_bytes: int = MAX_API_BYTES,
        upload: bool = False,
    ) -> tuple[int, bytes]:
        require(json_body is None or raw_body is None, "GitHub request cannot contain two body formats")
        encoded_query = urllib.parse.urlencode(query or {})
        root = self.upload_root if upload else self.api_root
        url = f"{root}{path}"
        if encoded_query:
            url = f"{url}?{encoded_query}"
        body = raw_body
        if json_body is not None:
            body = json.dumps(json_body, separators=(",", ":")).encode("utf-8")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": content_type,
            "User-Agent": "AutoJs6-Plugin-OpenCC-draft-controller/1",
            "X-GitHub-Api-Version": API_VERSION,
        }
        if body is not None:
            headers["Content-Length"] = str(len(body))
        request = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                status = response.status
                payload = response.read(maximum_bytes + 1)
        except urllib.error.HTTPError as error:
            try:
                detail = error.read(8193).decode("utf-8", errors="replace")[:8192]
            except OSError:
                detail = str(error)
            raise GitHubHttpError(error.code, url, detail or str(error)) from None
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise DraftError(f"Unable to call GitHub API URL {url}: {error}") from None
        require(status in expected_statuses, f"GitHub API returned unexpected HTTP {status} for {url}")
        require(len(payload) <= maximum_bytes, f"GitHub API response exceeds {maximum_bytes} bytes: {url}")
        return status, payload

    @staticmethod
    def _json_object(payload: bytes, description: str) -> dict[str, Any]:
        try:
            value = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise DraftError(f"GitHub returned invalid JSON for {description}: {error}") from None
        return object_value(value, description)

    def get_json(self, path: str, *, query: dict[str, object] | None = None) -> dict[str, Any]:
        _, payload = self._request("GET", path, query=query)
        return self._json_object(payload, f"GET {path}")

    def get_optional_json(self, path: str, *, query: dict[str, object] | None = None) -> dict[str, Any] | None:
        try:
            return self.get_json(path, query=query)
        except GitHubHttpError as error:
            if error.status == 404:
                return None
            raise

    def get_paginated(
        self,
        path: str,
        *,
        key: str | None = None,
        query: dict[str, object] | None = None,
    ) -> list[dict[str, Any]]:
        values: list[dict[str, Any]] = []
        for page in range(1, MAX_PAGES + 1):
            page_query = {**(query or {}), "per_page": 100, "page": page}
            _, payload = self._request("GET", path, query=page_query)
            try:
                response = json.loads(payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise DraftError(f"GitHub returned invalid paginated JSON for {path}: {error}") from None
            page_values = response.get(key) if key is not None and isinstance(response, dict) else response
            require(
                isinstance(page_values, list) and all(isinstance(value, dict) for value in page_values),
                f"GitHub returned malformed pagination for {path}",
            )
            values.extend(page_values)
            if len(page_values) < 100:
                return values
        raise DraftError(f"GitHub pagination exceeded {MAX_PAGES * 100} entries for {path}")

    def post_json(
        self,
        path: str,
        body: dict[str, Any],
        *,
        expected_statuses: frozenset[int] = frozenset({201}),
    ) -> dict[str, Any] | None:
        _, payload = self._request(
            "POST",
            path,
            json_body=body,
            expected_statuses=expected_statuses,
        )
        if not payload:
            return None
        return self._json_object(payload, f"POST {path}")

    def upload_asset(self, repository: str, release_id: int, asset: ReleaseAsset) -> dict[str, Any]:
        require(asset.size <= MAX_ARTIFACT_BYTES, f"Release asset is too large: {asset.name}")
        data = asset.path.read_bytes()
        require(len(data) == asset.size, f"Release asset size changed before upload: {asset.name}")
        require(hashlib.sha256(data).hexdigest() == asset.sha256, f"Release asset digest changed: {asset.name}")
        _, payload = self._request(
            "POST",
            f"/repos/{repository}/releases/{release_id}/assets",
            query={"name": asset.name},
            raw_body=data,
            content_type=asset.content_type,
            expected_statuses=frozenset({201}),
            upload=True,
        )
        return self._json_object(payload, f"upload {asset.name}")

    def delete(self, path: str) -> None:
        self._request("DELETE", path, expected_statuses=frozenset({204}), maximum_bytes=1024)


def repository_metadata(api: GitHubApi, repository: str) -> tuple[int, str]:
    value = api.get_json(f"/repos/{repository}")
    require(str(value.get("full_name", "")) == repository, "GitHub repository identity changed")
    require(value.get("default_branch") == BASE_BRANCH, "GitHub default branch changed")
    return positive_integer(value.get("id"), "repository ID"), str(value.get("html_url", ""))


def remote_master_sha(api: GitHubApi, repository: str) -> str:
    reference = api.get_json(f"/repos/{repository}/git/ref/heads/{BASE_BRANCH}")
    target = object_value(reference.get("object"), "master reference target")
    sha = str(target.get("sha", "")).lower()
    return canonical_source_sha(sha, "remote master SHA")


def validate_run_identity(
    run: dict[str, Any],
    repository: str,
    source_sha: str,
    workflow_name: str,
    workflow_file: str,
) -> int:
    run_id = positive_integer(run.get("id"), f"{workflow_name} run ID")
    require(run.get("name") == workflow_name, f"Unexpected workflow name for run {run_id}")
    require(str(run.get("path", "")).split("@", 1)[0] == f".github/workflows/{workflow_file}", f"Unexpected workflow path for run {run_id}")
    require(run.get("event") == "workflow_dispatch", f"Run {run_id} was not explicitly dispatched")
    require(run.get("head_branch") == BASE_BRANCH, f"Run {run_id} did not execute on master")
    require(str(run.get("head_sha", "")).lower() == source_sha, f"Run {run_id} used another source SHA")
    repository_value = object_value(run.get("repository"), f"run {run_id} repository")
    require(str(repository_value.get("full_name", "")) == repository, f"Run {run_id} belongs to another repository")
    head_repository = run.get("head_repository")
    if head_repository is not None:
        require(
            str(object_value(head_repository, f"run {run_id} head repository").get("full_name", "")) == repository,
            f"Run {run_id} has an untrusted head repository",
        )
    return run_id


def verify_workflow_run(
    api: GitHubApi,
    repository: str,
    source_sha: str,
    contract: WorkflowContract,
    run_id: int,
) -> WorkflowEvidence:
    run = api.get_json(f"/repos/{repository}/actions/runs/{run_id}")
    validate_run_identity(run, repository, source_sha, contract.name, contract.file)
    require(
        run.get("status") == "completed" and run.get("conclusion") == "success",
        f"{contract.name} run {run_id} is not completed/success",
    )
    jobs = api.get_paginated(
        f"/repos/{repository}/actions/runs/{run_id}/jobs",
        key="jobs",
        query={"filter": "latest"},
    )
    actual_names = {str(job.get("name", "")) for job in jobs}
    require(
        len(jobs) == len(contract.jobs) and actual_names == set(contract.jobs),
        f"{contract.name} job inventory changed: expected={sorted(contract.jobs)}, actual={sorted(actual_names)}",
    )
    failed = sorted(
        str(job.get("name", ""))
        for job in jobs
        if job.get("status") != "completed" or job.get("conclusion") != "success"
    )
    require(not failed, f"{contract.name} contains non-success jobs: {failed}")
    url = str(run.get("html_url", ""))
    require(url == f"https://github.com/{repository}/actions/runs/{run_id}", f"Unexpected run URL for {run_id}")
    return WorkflowEvidence(contract, run_id, url, tuple(sorted(actual_names)))


def list_dispatched_runs(api: GitHubApi, repository: str, contract: WorkflowContract) -> list[dict[str, Any]]:
    return api.get_paginated(
        f"/repos/{repository}/actions/workflows/{contract.file}/runs",
        key="workflow_runs",
        query={"branch": BASE_BRANCH, "event": "workflow_dispatch"},
    )


def validate_workflow_metadata(api: GitHubApi, repository: str, contract: WorkflowContract) -> None:
    workflow = api.get_json(f"/repos/{repository}/actions/workflows/{contract.file}")
    require(workflow.get("name") == contract.name, f"Workflow name changed for {contract.file}")
    require(workflow.get("path") == f".github/workflows/{contract.file}", f"Workflow path changed for {contract.file}")
    require(workflow.get("state") == "active", f"Workflow is not active: {contract.file}")


def find_new_exact_run(
    api: GitHubApi,
    repository: str,
    source_sha: str,
    contract: WorkflowContract,
    watermark: int,
) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for run in list_dispatched_runs(api, repository, contract):
        run_id = positive_integer(run.get("id"), f"listed {contract.name} run ID")
        if run_id <= watermark:
            continue
        try:
            validate_run_identity(run, repository, source_sha, contract.name, contract.file)
        except DraftError:
            continue
        candidates.append(run)
    return max(candidates, key=lambda value: int(value["id"])) if candidates else None


def dispatch_release_gates(
    api: GitHubApi,
    repository: str,
    source_sha: str,
    mode: str,
    *,
    timeout_seconds: int = DEFAULT_GATE_TIMEOUT_SECONDS,
    poll_seconds: int = DEFAULT_POLL_SECONDS,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[WorkflowEvidence, ...]:
    repository = canonical_repository(repository)
    source_sha = canonical_source_sha(source_sha)
    require(mode == "release", f"Draft gates require release mode, found {mode!r}")
    repository_metadata(api, repository)
    require(remote_master_sha(api, repository) == source_sha, "Remote master moved before release-gate dispatch")

    pending: list[tuple[WorkflowContract, int, int | None]] = []
    for contract in WORKFLOW_CONTRACTS:
        validate_workflow_metadata(api, repository, contract)
        existing = list_dispatched_runs(api, repository, contract)
        watermark = max(
            (positive_integer(run.get("id"), f"listed {contract.name} run ID") for run in existing),
            default=0,
        )
        response = api.post_json(
            f"/repos/{repository}/actions/workflows/{contract.file}/dispatches",
            {"ref": BASE_BRANCH},
            expected_statuses=frozenset({200, 204}),
        )
        returned_id = None
        if response is not None and response.get("workflow_run_id") is not None:
            returned_id = positive_integer(response["workflow_run_id"], f"{contract.name} dispatched run ID")
            require(returned_id > watermark, f"{contract.name} dispatch returned a stale run ID")
        pending.append((contract, watermark, returned_id))

    require(remote_master_sha(api, repository) == source_sha, "Remote master moved during release-gate dispatch")
    deadline = monotonic() + timeout_seconds
    evidence: list[WorkflowEvidence] = []
    for contract, watermark, returned_id in pending:
        selected_id = returned_id
        while monotonic() <= deadline:
            if selected_id is None:
                run = find_new_exact_run(api, repository, source_sha, contract, watermark)
                if run is not None:
                    selected_id = int(run["id"])
            if selected_id is not None:
                run = api.get_optional_json(f"/repos/{repository}/actions/runs/{selected_id}")
                if run is None:
                    sleep(float(poll_seconds))
                    continue
                validate_run_identity(run, repository, source_sha, contract.name, contract.file)
                status = run.get("status")
                if status == "completed":
                    require(
                        run.get("conclusion") == "success",
                        f"{contract.name} run {selected_id} completed with {run.get('conclusion')!r}",
                    )
                    evidence.append(verify_workflow_run(api, repository, source_sha, contract, selected_id))
                    break
                require(status in {"queued", "in_progress", "pending", "waiting"}, f"Unexpected status for run {selected_id}: {status!r}")
            sleep(float(poll_seconds))
        else:
            raise DraftError(f"Timed out waiting for exact {contract.name} workflow evidence")

    require(remote_master_sha(api, repository) == source_sha, "Remote master moved while release gates ran")
    return tuple(evidence)


def verify_candidate_artifact(
    api: GitHubApi,
    repository: str,
    candidate: CandidateEvidence,
    artifact_id: int,
    artifact_digest: str,
    candidate_run_id: int,
) -> None:
    repository_id, _ = repository_metadata(api, repository)
    artifact_id = positive_integer(artifact_id, "candidate artifact ID")
    candidate_run_id = positive_integer(candidate_run_id, "candidate workflow run ID")
    artifact_digest = canonical_artifact_digest(artifact_digest)
    run = api.get_json(f"/repos/{repository}/actions/runs/{candidate_run_id}")
    validate_run_identity(
        run,
        repository,
        candidate.source_sha,
        RELEASE_WORKFLOW_NAME,
        RELEASE_WORKFLOW_FILE,
    )
    require(run.get("status") in {"queued", "in_progress"}, "Candidate workflow run is no longer active")
    artifacts = api.get_paginated(
        f"/repos/{repository}/actions/runs/{candidate_run_id}/artifacts",
        key="artifacts",
    )
    require(len(artifacts) == 1, f"Draft workflow must have exactly one candidate artifact, found {len(artifacts)}")
    artifact = artifacts[0]
    require(positive_integer(artifact.get("id"), "artifact ID") == artifact_id, "Candidate artifact ID changed")
    require(artifact.get("name") == candidate.artifact_name, "Candidate artifact name changed")
    require(artifact.get("expired") is False, "Candidate artifact expired")
    require(artifact.get("digest") == artifact_digest, "Candidate artifact digest changed")
    require(
        0 < positive_integer(artifact.get("size_in_bytes"), "candidate artifact size") <= MAX_ARTIFACT_BYTES,
        "Candidate artifact size is outside policy",
    )
    workflow_run = object_value(artifact.get("workflow_run"), "artifact workflow run")
    require(int(workflow_run.get("id", 0)) == candidate_run_id, "Artifact belongs to another workflow run")
    require(str(workflow_run.get("head_sha", "")).lower() == candidate.source_sha, "Artifact source SHA changed")
    require(int(workflow_run.get("repository_id", 0)) == repository_id, "Artifact repository ID changed")
    require(int(workflow_run.get("head_repository_id", 0)) == repository_id, "Artifact head repository changed")


def resolve_tag_commit(api: GitHubApi, repository: str, tag: str) -> str | None:
    encoded = urllib.parse.quote(tag, safe="")
    reference = api.get_optional_json(f"/repos/{repository}/git/ref/tags/{encoded}")
    if reference is None:
        return None
    target = object_value(reference.get("object"), f"tag {tag} target")
    target_type = target.get("type")
    target_sha = canonical_source_sha(str(target.get("sha", "")).lower(), f"tag {tag} target SHA")
    if target_type == "commit":
        return target_sha
    require(target_type == "tag", f"Tag {tag} points to unsupported object type {target_type!r}")
    annotated = api.get_json(f"/repos/{repository}/git/tags/{target_sha}")
    annotated_target = object_value(annotated.get("object"), f"annotated tag {tag} target")
    require(annotated_target.get("type") == "commit", f"Annotated tag {tag} does not point directly to a commit")
    return canonical_source_sha(str(annotated_target.get("sha", "")).lower(), f"annotated tag {tag} commit")


def verify_latest_release_baseline(
    api: GitHubApi,
    repository: str,
    candidate: CandidateEvidence,
) -> int:
    latest = api.get_json(f"/repos/{repository}/releases/latest")
    baseline = candidate.baseline
    release_id = positive_integer(latest.get("id"), "latest release ID")
    require(latest.get("tag_name") == baseline.tag, "Latest published Release differs from candidate baseline")
    require(latest.get("draft") is False and latest.get("prerelease") is False, "Latest release is not stable")
    require(resolve_tag_commit(api, repository, baseline.tag) == baseline.source_sha, "Latest release tag moved")
    assets = latest.get("assets")
    require(isinstance(assets, list), "Latest release has malformed assets")
    require(len(assets) == len(ABI_ORDER) + 2, "Latest release asset inventory changed")
    pattern = released_apk_pattern(candidate.context.project_name)
    found_sizes: dict[str, int] = {}
    documents: set[str] = set()
    for value in assets:
        asset = object_value(value, "latest release asset")
        name = str(asset.get("name", ""))
        match = pattern.fullmatch(name)
        if match is None:
            require(name in {"SHA256SUMS.txt", "RELEASE_NOTES.md"}, f"Unexpected latest release asset: {name}")
            documents.add(name)
            continue
        require(match.group("version") == baseline.version_name, f"Latest release APK has another version: {name}")
        abi = match.group("abi")
        require(abi not in found_sizes, f"Latest release contains duplicate {abi} APKs")
        found_sizes[abi] = positive_integer(asset.get("size"), f"latest {abi} asset size")
    require(documents == {"SHA256SUMS.txt", "RELEASE_NOTES.md"}, "Latest release documents changed")
    require(found_sizes == baseline.package_sizes, "Latest release APK sizes differ from candidate baseline")
    return release_id


def release_assets(candidate: CandidateEvidence) -> tuple[ReleaseAsset, ...]:
    values: list[ReleaseAsset] = []
    for record in candidate.records:
        values.append(
            ReleaseAsset(
                record.source,
                record.filename,
                record.size,
                record.sha256,
                "application/vnd.android.package-archive",
            ),
        )
    for name, content_type in (
        ("SHA256SUMS.txt", "text/plain"),
        ("RELEASE_NOTES.md", "text/markdown"),
    ):
        path = candidate.bundle / name
        require(path.is_file() and not path.is_symlink(), f"Missing regular release document: {name}")
        values.append(ReleaseAsset(path, name, path.stat().st_size, sha256(path), content_type))
    require(len({asset.name for asset in values}) == len(values), "Draft release asset names are not unique")
    return tuple(values)


def prepare_draft_plan(
    api: GitHubApi,
    repository: str,
    candidate: CandidateEvidence,
    build_run_id: int,
    markdown_run_id: int,
) -> DraftPlan:
    repository = canonical_repository(repository)
    repository_metadata(api, repository)
    require(remote_master_sha(api, repository) == candidate.source_sha, "Remote master moved before draft planning")
    verify_workflow_run(api, repository, candidate.source_sha, WORKFLOW_BY_KEY["build"], build_run_id)
    verify_workflow_run(api, repository, candidate.source_sha, WORKFLOW_BY_KEY["markdown"], markdown_run_id)
    baseline_release_id = verify_latest_release_baseline(api, repository, candidate)
    require(resolve_tag_commit(api, repository, candidate.tag) is None, f"Draft tag already exists: {candidate.tag}")
    releases = api.get_paginated(f"/repos/{repository}/releases")
    conflicts = [value for value in releases if value.get("tag_name") == candidate.tag]
    require(not conflicts, f"A GitHub Release already uses draft tag {candidate.tag}")
    notes_path = candidate.bundle / "RELEASE_NOTES.md"
    notes_bytes = notes_path.read_bytes()
    require(0 < len(notes_bytes) <= MAX_RELEASE_NOTES_BYTES, "Release notes size is outside policy")
    try:
        notes = notes_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise DraftError(f"Release notes are not UTF-8: {error}") from None
    require("\0" not in notes, "Release notes contain NUL")
    return DraftPlan(candidate, baseline_release_id, notes, release_assets(candidate))


def validate_uploaded_asset(value: dict[str, Any], expected: ReleaseAsset) -> None:
    require(value.get("name") == expected.name, f"Uploaded asset name changed: {expected.name}")
    require(value.get("state") == "uploaded", f"Uploaded asset is not ready: {expected.name}")
    require(int(value.get("size", -1)) == expected.size, f"Uploaded asset size changed: {expected.name}")
    require(value.get("digest") == f"sha256:{expected.sha256}", f"Uploaded asset digest changed: {expected.name}")
    require(value.get("content_type") == expected.content_type, f"Uploaded asset content type changed: {expected.name}")
    uploader = object_value(value.get("uploader"), f"uploader for {expected.name}")
    require(uploader.get("login") == EXPECTED_BOT_LOGIN, f"Unexpected uploader for {expected.name}")


def validate_draft_release(value: dict[str, Any], plan: DraftPlan, *, require_assets: bool) -> int:
    candidate = plan.candidate
    release_id = positive_integer(value.get("id"), "draft release ID")
    require(value.get("tag_name") == candidate.tag, "Draft release tag changed")
    require(value.get("target_commitish") == candidate.source_sha, "Draft target commit changed")
    require(value.get("name") == candidate.tag, "Draft release title changed")
    require(value.get("body") == plan.notes, "Draft release notes changed")
    require(value.get("draft") is True, "Release is not a draft")
    require(value.get("prerelease") is False, "Draft was marked as a prerelease")
    require(value.get("published_at") is None, "Draft unexpectedly has a publication timestamp")
    author = object_value(value.get("author"), "draft release author")
    require(author.get("login") == EXPECTED_BOT_LOGIN, "Draft release author is not github-actions[bot]")
    assets = value.get("assets")
    require(isinstance(assets, list), "Draft release has malformed assets")
    if not require_assets:
        require(not assets, "New draft unexpectedly already contains assets")
        return release_id
    actual = {str(object_value(item, "draft asset").get("name", "")): item for item in assets}
    expected = {asset.name: asset for asset in plan.assets}
    require(len(assets) == len(actual) == len(expected) and set(actual) == set(expected), "Draft asset inventory changed")
    for name, asset in expected.items():
        validate_uploaded_asset(object_value(actual[name], f"draft asset {name}"), asset)
    return release_id


def rollback_new_draft(api: GitHubApi, repository: str, release_id: int, tag: str) -> None:
    current = api.get_optional_json(f"/repos/{repository}/releases/{release_id}")
    if current is not None:
        require(current.get("draft") is True, f"Refusing to roll back non-draft Release {release_id}")
        api.delete(f"/repos/{repository}/releases/{release_id}")
    require(api.get_optional_json(f"/repos/{repository}/releases/{release_id}") is None, "Draft rollback did not remove the new Release")
    require(
        resolve_tag_commit(api, repository, tag) is None,
        f"Draft rollback removed Release {release_id}, but tag {tag} remains and requires manual review",
    )


def create_draft_release(
    api: GitHubApi,
    repository: str,
    plan: DraftPlan,
    *,
    readback_attempts: int = 6,
    readback_delay_seconds: float = 2,
    sleep: Callable[[float], None] = time.sleep,
) -> DraftResult:
    candidate = plan.candidate
    require(readback_attempts > 0, "Draft readback attempts must be positive")
    require(remote_master_sha(api, repository) == candidate.source_sha, "Remote master moved before draft creation")
    require(resolve_tag_commit(api, repository, candidate.tag) is None, f"Draft tag appeared before creation: {candidate.tag}")
    created_id: int | None = None
    try:
        created = api.post_json(
            f"/repos/{repository}/releases",
            {
                "tag_name": candidate.tag,
                "target_commitish": candidate.source_sha,
                "name": candidate.tag,
                "body": plan.notes,
                "draft": True,
                "prerelease": False,
                "generate_release_notes": False,
                "make_latest": "false",
            },
        )
        require(created is not None, "GitHub returned an empty draft Release response")
        created_id = positive_integer(created.get("id"), "new draft release ID")
        require(created_id != plan.baseline_release_id, "GitHub reused the latest published Release ID")
        validate_draft_release(created, plan, require_assets=False)
        for asset in plan.assets:
            uploaded = api.upload_asset(repository, created_id, asset)
            validate_uploaded_asset(uploaded, asset)
        readback: dict[str, Any] | None = None
        last_readback_error: DraftError | None = None
        for attempt in range(readback_attempts):
            readback = api.get_json(f"/repos/{repository}/releases/{created_id}")
            try:
                validate_draft_release(readback, plan, require_assets=True)
                last_readback_error = None
                break
            except DraftError as error:
                last_readback_error = error
                if attempt + 1 < readback_attempts:
                    sleep(readback_delay_seconds)
        require(last_readback_error is None and readback is not None, f"Draft readback did not converge: {last_readback_error}")
        latest = api.get_json(f"/repos/{repository}/releases/latest")
        require(int(latest.get("id", 0)) == plan.baseline_release_id, "Creating the draft changed the Latest Release")
        require(resolve_tag_commit(api, repository, candidate.tag) is None, "Draft creation unexpectedly created a public tag")
        require(remote_master_sha(api, repository) == candidate.source_sha, "Remote master moved before draft acceptance")
        url = str(readback.get("html_url", ""))
        require(url.startswith(f"https://github.com/{repository}/releases/"), "Draft Release URL is unexpected")
        return DraftResult(created_id, url, candidate.tag, candidate.source_sha, plan.assets)
    except Exception as error:
        if created_id is None:
            raise
        try:
            rollback_new_draft(api, repository, created_id, candidate.tag)
        except Exception as rollback_error:
            raise DraftError(
                f"Draft creation failed and rollback also failed for Release {created_id}: {rollback_error}",
            ) from error
        raise DraftError(f"Draft creation failed; newly created Release {created_id} was rolled back: {error}") from error


def write_gate_outputs(path: Path, evidence: tuple[WorkflowEvidence, ...]) -> None:
    by_key = {item.contract.key: item for item in evidence}
    require(set(by_key) == set(WORKFLOW_BY_KEY), "Release gate evidence is incomplete")
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        for key in ("build", "markdown"):
            stream.write(f"{key}_run_id={by_key[key].run_id}\n")


def write_draft_outputs(path: Path, result: DraftResult) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"release_id={result.release_id}\n")
        stream.write(f"release_url={result.release_url}\n")
        stream.write(f"tag={result.tag}\n")
        stream.write(f"asset_count={len(result.assets)}\n")


def github_token() -> str:
    value = os.environ.get("GITHUB_TOKEN", "")
    require(bool(value.strip()), "GITHUB_TOKEN is required")
    return value


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    gates = subparsers.add_parser("dispatch-gates", help="dispatch and wait for exact-SHA release gates")
    gates.add_argument("--repository", required=True)
    gates.add_argument("--source-sha", required=True)
    gates.add_argument("--mode", required=True)
    gates.add_argument("--github-output", type=Path, required=True)
    gates.add_argument("--timeout-seconds", type=int, default=DEFAULT_GATE_TIMEOUT_SECONDS)
    gates.add_argument("--poll-seconds", type=int, default=DEFAULT_POLL_SECONDS)

    draft = subparsers.add_parser("create-draft", help="verify a signed candidate and create a draft Release")
    draft.add_argument("--root", type=Path, default=ROOT)
    draft.add_argument("--bundle", type=Path, required=True)
    draft.add_argument("--repository", required=True)
    draft.add_argument("--source-sha", required=True)
    draft.add_argument("--mode", required=True)
    draft.add_argument("--expected-signer-sha256", required=True)
    draft.add_argument("--apksigner", type=Path, required=True)
    draft.add_argument("--zipalign", type=Path, required=True)
    draft.add_argument("--artifact-id", required=True)
    draft.add_argument("--artifact-digest", required=True)
    draft.add_argument("--candidate-run-id", required=True)
    draft.add_argument("--build-run-id", required=True)
    draft.add_argument("--markdown-run-id", required=True)
    draft.add_argument("--github-output", type=Path)
    draft.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        api = GitHubApi(github_token())
        if arguments.command == "dispatch-gates":
            require(arguments.timeout_seconds > 0, "Gate timeout must be positive")
            require(arguments.poll_seconds > 0, "Gate poll interval must be positive")
            evidence = dispatch_release_gates(
                api,
                arguments.repository,
                arguments.source_sha,
                arguments.mode,
                timeout_seconds=arguments.timeout_seconds,
                poll_seconds=arguments.poll_seconds,
            )
            write_gate_outputs(arguments.github_output, evidence)
            for item in evidence:
                print(
                    f"RELEASE_GATE_OK workflow={item.contract.file} run_id={item.run_id} "
                    f"jobs={len(item.job_names)} source={arguments.source_sha}",
                )
            return 0

        require(arguments.mode == "release", f"Draft creation requires release mode, found {arguments.mode!r}")
        repository = canonical_repository(arguments.repository)
        source_sha = canonical_source_sha(arguments.source_sha)
        candidate = verify_candidate_bundle(
            arguments.root,
            arguments.bundle,
            source_sha,
            arguments.expected_signer_sha256,
            arguments.apksigner,
            arguments.zipalign,
        )
        verify_candidate_artifact(
            api,
            repository,
            candidate,
            positive_integer(arguments.artifact_id, "candidate artifact ID"),
            canonical_artifact_digest(arguments.artifact_digest),
            positive_integer(arguments.candidate_run_id, "candidate run ID"),
        )
        plan = prepare_draft_plan(
            api,
            repository,
            candidate,
            positive_integer(arguments.build_run_id, "Build integrity run ID"),
            positive_integer(arguments.markdown_run_id, "Markdown integrity run ID"),
        )
        if not arguments.execute:
            print(
                f"DRAFT_READY tag={candidate.tag} source={source_sha} assets={len(plan.assets)} "
                f"manifest_sha256={candidate.manifest_sha256}",
            )
            return 0
        result = create_draft_release(api, repository, plan)
        if arguments.github_output is not None:
            write_draft_outputs(arguments.github_output, result)
        print(
            f"DRAFT_RELEASE_OK id={result.release_id} tag={result.tag} source={result.source_sha} "
            f"assets={len(result.assets)} url={result.release_url}",
        )
        return 0
    except (DraftError, ReleaseError, OSError) as error:
        print(f"DRAFT_ERROR {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
