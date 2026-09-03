#!/usr/bin/env python3
"""Prepare and verify the non-release OpenCC upgrade acceptance fixture.

This module exists only to exercise the remote M4-D-2/M4-D-3 plumbing while
there is no newer formal OpenCC release.  Its deliberately non-official tag,
reserved version, draft pull request, and pr-only evaluator form independent
barriers against promotion into ``master``.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import os
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

import check_upstream
import update_upstream
import verify_upstream


FIXTURE_ID = "post-1.4.2-direct-child"
FIXTURE_VERSION = "999.4.2"
FIXTURE_TAG = f"controlled-ver.{FIXTURE_VERSION}"
FIXTURE_COMMIT = "b8bf091a83e7b318945352a8298127ecd0158643"
FIXTURE_ASSET = f"opencc-v{FIXTURE_VERSION}-resources.zip"
FIXTURE_ARCHIVE_SIZE = 1_237_814
FIXTURE_ARCHIVE_SHA256 = "dbcd3cf917e960db3562e663f4baf3fcadc21d2b38102937fa266b4b2cdc809e"
FIXTURE_BRANCH = f"automation/opencc-{FIXTURE_VERSION}"
FIXTURE_TITLE = f"test(ci): exercise controlled OpenCC upgrade fixture {FIXTURE_VERSION}"
FIXTURE_MARKER = {
    "fixture_id": FIXTURE_ID,
    "production_release": False,
}

BASE_PROPERTIES = {
    "OPENCC_VERSION": "1.4.2",
    "OPENCC_TAG": "ver.1.4.2",
    "OPENCC_COMMIT": "025f371dc76b598d77384fbdab90c937471844d8",
    "OPENCC_SOURCE_URL": "https://github.com/BYVoid/OpenCC.git",
    "OPENCC_RESOURCE_ASSET": "opencc-v1.4.2-resources.zip",
    "OPENCC_RESOURCE_SHA256": "9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5",
    "OPENCC_RESOURCE_SIZE": "1237703",
    "OPENCC_RESOURCE_MANIFEST_VERSION": "1",
}

FIXTURE_PROPERTIES = {
    **BASE_PROPERTIES,
    "OPENCC_VERSION": FIXTURE_VERSION,
    "OPENCC_TAG": FIXTURE_TAG,
    "OPENCC_COMMIT": FIXTURE_COMMIT,
    "OPENCC_RESOURCE_ASSET": FIXTURE_ASSET,
    "OPENCC_RESOURCE_SHA256": FIXTURE_ARCHIVE_SHA256,
    "OPENCC_RESOURCE_SIZE": str(FIXTURE_ARCHIVE_SIZE),
}


class ControlledAcceptanceError(Exception):
    pass


@dataclass(frozen=True)
class AcceptanceResult:
    message: str
    locked: dict[str, str]
    proposed: dict[str, str]
    branch_name: str
    commit_title: str
    pull_request_body: str


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ControlledAcceptanceError(reason)


def exact_properties(actual: dict[str, str], expected: dict[str, str], description: str) -> None:
    if actual != expected:
        keys = sorted(actual.keys() | expected.keys())
        drift = [
            f"{key}={expected.get(key)!r}->{actual.get(key)!r}"
            for key in keys
            if actual.get(key) != expected.get(key)
        ]
        raise ControlledAcceptanceError(f"{description} drifted: {', '.join(drift)}")


def official_release(api_base: str, source_url: str) -> check_upstream.ValidatedRelease:
    release = check_upstream.download_validated_release(api_base.rstrip("/"), source_url)
    exact_properties(release.properties, BASE_PROPERTIES, "latest formal OpenCC release")
    return release


def validate_fixture_commit_payload(commit: dict[str, object]) -> None:
    require(str(commit.get("sha", "")).lower() == FIXTURE_COMMIT, "controlled fixture commit SHA drifted")
    parents = commit.get("parents")
    require(isinstance(parents, list) and len(parents) == 1, "controlled fixture must have one parent")
    parent = parents[0] if isinstance(parents[0], dict) else {}
    require(
        str(parent.get("sha", "")).lower() == BASE_PROPERTIES["OPENCC_COMMIT"],
        "controlled fixture is no longer a direct child of the locked release",
    )
    expected_url = f"https://github.com/BYVoid/OpenCC/commit/{FIXTURE_COMMIT}"
    require(commit.get("html_url") == expected_url, "controlled fixture commit URL is unexpected")


def validate_fixture_commit(api_base: str) -> None:
    commit = check_upstream.read_json(f"{api_base.rstrip('/')}/commits/{FIXTURE_COMMIT}")
    validate_fixture_commit_payload(commit)


def rewrite_archive_manifest(
    base_archive: bytes,
    base_commit: str,
    fixture_commit: str,
    marker: dict[str, object],
) -> bytes:
    try:
        with zipfile.ZipFile(io.BytesIO(base_archive)) as source:
            require(source.testzip() is None, "base resource ZIP is corrupt")
            manifest = json.loads(source.read(verify_upstream.RESOURCE_MANIFEST).decode("utf-8"))
            require(isinstance(manifest, dict), "base resource manifest is not an object")
            require(
                str(manifest.get("commit_id", "")).lower() == base_commit.lower(),
                "base resource manifest commit drifted",
            )
            require("controlled_acceptance" not in manifest, "base resource already contains a fixture marker")
            manifest["commit_id"] = fixture_commit
            manifest["controlled_acceptance"] = dict(marker)
            manifest_data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

            output = io.BytesIO()
            with zipfile.ZipFile(output, "w", allowZip64=True) as target:
                target.comment = source.comment
                for info in source.infolist():
                    data = manifest_data if info.filename == verify_upstream.RESOURCE_MANIFEST else source.read(info.filename)
                    target.writestr(copy.copy(info), data)
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        raise ControlledAcceptanceError(f"unable to derive controlled resource fixture: {error}") from None

    return output.getvalue()


def build_fixture_archive(base_archive: bytes) -> bytes:
    require(len(base_archive) == int(BASE_PROPERTIES["OPENCC_RESOURCE_SIZE"]), "base resource size drifted")
    require(
        hashlib.sha256(base_archive).hexdigest() == BASE_PROPERTIES["OPENCC_RESOURCE_SHA256"],
        "base resource digest drifted",
    )
    archive = rewrite_archive_manifest(
        base_archive,
        BASE_PROPERTIES["OPENCC_COMMIT"],
        FIXTURE_COMMIT,
        FIXTURE_MARKER,
    )

    require(len(archive) == FIXTURE_ARCHIVE_SIZE, "controlled resource size is not reproducible")
    require(
        hashlib.sha256(archive).hexdigest() == FIXTURE_ARCHIVE_SHA256,
        "controlled resource digest is not reproducible",
    )
    return archive


def inspect_archive_marker(archive_path: Path) -> None:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            manifest = json.loads(archive.read(verify_upstream.RESOURCE_MANIFEST).decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        raise ControlledAcceptanceError(f"unable to read controlled resource marker: {error}") from None
    require(isinstance(manifest, dict), "controlled resource manifest is not an object")
    require(manifest.get("controlled_acceptance") == FIXTURE_MARKER, "controlled resource marker drifted")


def verify_source(root: Path) -> None:
    source = (root / verify_upstream.SOURCE_DIRECTORY).resolve()
    require((source / "CMakeLists.txt").is_file(), f"controlled OpenCC source is missing: {source}")
    actual_commit = update_upstream.git(source, "rev-parse", "HEAD").lower()
    require(actual_commit == FIXTURE_COMMIT, "controlled OpenCC source commit drifted")
    parent_commit = update_upstream.git(source, "rev-parse", "HEAD^").lower()
    require(
        parent_commit == BASE_PROPERTIES["OPENCC_COMMIT"],
        "controlled OpenCC source is not a direct child of the locked release",
    )
    remote = update_upstream.git(source, "remote", "get-url", "origin")
    require(
        verify_upstream.normalized_repository_url(remote)
        == verify_upstream.normalized_repository_url(BASE_PROPERTIES["OPENCC_SOURCE_URL"]),
        f"controlled OpenCC source remote is unexpected: {remote}",
    )
    dirty = update_upstream.git(source, "status", "--porcelain", "--untracked-files=all")
    require(not dirty, f"controlled OpenCC source contains local changes:\n{dirty}")
    tags = update_upstream.git(source, "tag", "--points-at", "HEAD").splitlines()
    require(FIXTURE_TAG not in tags, "controlled marker unexpectedly became an upstream Git tag")


def verify(root: Path) -> None:
    try:
        properties = verify_upstream.parse_properties(root / verify_upstream.LOCK_FILE)
    except verify_upstream.VerificationError as error:
        raise ControlledAcceptanceError(str(error)) from None
    exact_properties(properties, FIXTURE_PROPERTIES, "controlled OpenCC lock")
    verify_source(root)
    try:
        entries, configs = verify_upstream.verify_resource_archive(root, properties)
    except verify_upstream.VerificationError as error:
        raise ControlledAcceptanceError(str(error)) from None
    archive_path = root / verify_upstream.ASSET_DIRECTORY / FIXTURE_ASSET
    inspect_archive_marker(archive_path)
    print(
        "OPENCC_CONTROLLED_ACCEPTANCE_OK "
        f"fixture={FIXTURE_ID} version={FIXTURE_VERSION} commit={FIXTURE_COMMIT} "
        f"resource_sha256={FIXTURE_ARCHIVE_SHA256} entries={entries} configs={configs}",
    )


def inspect(root: Path, api_base: str) -> AcceptanceResult:
    try:
        locked = verify_upstream.parse_properties(root / verify_upstream.LOCK_FILE)
        exact_properties(locked, BASE_PROPERTIES, "controlled acceptance base lock")
        verify_upstream.verify_resource_archive(root, locked)
    except verify_upstream.VerificationError as error:
        raise ControlledAcceptanceError(str(error)) from None
    release = official_release(api_base, locked["OPENCC_SOURCE_URL"])
    require(release.archive_data == (root / verify_upstream.ASSET_DIRECTORY / locked["OPENCC_RESOURCE_ASSET"]).read_bytes(),
            "repository base resource differs from the latest formal release")
    build_fixture_archive(release.archive_data)
    validate_fixture_commit(api_base)
    return AcceptanceResult(
        (
            "OPENCC_CONTROLLED_ACCEPTANCE_AVAILABLE "
            f"base={locked['OPENCC_VERSION']} fixture={FIXTURE_VERSION} commit={FIXTURE_COMMIT} "
            f"resource_sha256={FIXTURE_ARCHIVE_SHA256}"
        ),
        locked,
        dict(FIXTURE_PROPERTIES),
        FIXTURE_BRANCH,
        FIXTURE_TITLE,
        render_pull_request_body(),
    )


def fetch_fixture_source(root: Path) -> None:
    source = (root / verify_upstream.SOURCE_DIRECTORY).resolve()
    remote = update_upstream.git(source, "remote", "get-url", "origin")
    require(
        verify_upstream.normalized_repository_url(remote)
        == verify_upstream.normalized_repository_url(BASE_PROPERTIES["OPENCC_SOURCE_URL"]),
        f"refusing unexpected OpenCC submodule remote: {remote}",
    )
    update_upstream.git(source, "fetch", "--no-tags", "origin", FIXTURE_COMMIT)
    fetched = update_upstream.git(source, "rev-parse", "FETCH_HEAD^{commit}").lower()
    require(fetched == FIXTURE_COMMIT, "fetched controlled fixture commit drifted")
    parent = update_upstream.git(source, "rev-parse", f"{FIXTURE_COMMIT}^").lower()
    require(parent == BASE_PROPERTIES["OPENCC_COMMIT"], "fetched controlled fixture parent drifted")
    update_upstream.git(source, "checkout", "--detach", FIXTURE_COMMIT)


def render_pull_request_body() -> str:
    commit_url = f"https://github.com/BYVoid/OpenCC/commit/{FIXTURE_COMMIT}"
    return f"""## Controlled M4-D-2 / M4-D-3 acceptance fixture

> [!CAUTION]
> This is a deliberately non-release **draft** used only to validate the remote automation plumbing.
> It must never be merged, tagged, released, or used by the plugin index.

| Field | Formal lock | Controlled fixture |
|---|---|---|
| Version | `{BASE_PROPERTIES['OPENCC_VERSION']}` | `{FIXTURE_VERSION}` (reserved test namespace) |
| Tag | `{BASE_PROPERTIES['OPENCC_TAG']}` | `{FIXTURE_TAG}` (deliberately not a formal `ver.*` tag) |
| Commit | `{BASE_PROPERTIES['OPENCC_COMMIT']}` | `{FIXTURE_COMMIT}` |
| Resource | `{BASE_PROPERTIES['OPENCC_RESOURCE_ASSET']}` | `{FIXTURE_ASSET}` |
| Resource bytes | `{BASE_PROPERTIES['OPENCC_RESOURCE_SIZE']}` | `{FIXTURE_ARCHIVE_SIZE}` |
| Resource SHA-256 | `{BASE_PROPERTIES['OPENCC_RESOURCE_SHA256']}` | `{FIXTURE_ARCHIVE_SHA256}` |

- Formal latest release revalidated during preparation: `ver.1.4.2`
- Controlled upstream commit: {commit_url}
- Fixture identity: `{FIXTURE_ID}`

The selected commit is the first direct child of the locked 1.4.2 release commit in the official
BYVoid/OpenCC repository. Its declared license evidence is unchanged. The resource payload is copied
byte-for-byte from the official 1.4.2 asset; only the manifest commit and an explicit
`controlled_acceptance` marker are changed, then the stored-entry ZIP is rebuilt deterministically.

## Acceptance invariants

- [ ] The PR remains a draft and open throughout success and failure replays.
- [ ] The branch has one direct `github-actions[bot]` commit and exactly four dependency paths.
- [ ] Explicit controlled Build integrity and ordinary Markdown integrity runs bind this exact head SHA.
- [ ] A repeated preparation run detects this open PR and leaves its head SHA unchanged.
- [ ] The production evaluator rejects the non-release tag/draft without write side effects.
- [ ] The controlled evaluator may report eligible only in repository policy `pr-only`.
- [ ] `merge`, `release`, and `--execute` remain hard-disabled for this fixture.

Generated by `.github/workflows/opencc-upstream.yml` and
`scripts/opencc/controlled_acceptance.py`. Close the PR and delete its branch after evidence is recorded.
"""


def prepare(root: Path, api_base: str) -> AcceptanceResult:
    update_upstream.ensure_clean_worktree(root)
    try:
        verify_upstream.verify(root)
    except verify_upstream.VerificationError as error:
        raise ControlledAcceptanceError(f"base OpenCC lock is invalid before fixture preparation: {error}") from None
    result = inspect(root, api_base)

    lock_path = (root / verify_upstream.LOCK_FILE).resolve()
    source = (root / verify_upstream.SOURCE_DIRECTORY).resolve()
    old_resource = update_upstream.safe_resource_path(root, BASE_PROPERTIES["OPENCC_RESOURCE_ASSET"])
    new_resource = update_upstream.safe_resource_path(root, FIXTURE_ASSET)
    require(old_resource.is_file(), f"controlled fixture base resource is missing: {old_resource}")
    require(not new_resource.exists(), f"refusing to replace a pre-existing controlled resource: {new_resource}")

    original_commit = update_upstream.git(source, "rev-parse", "HEAD")
    original_lock = lock_path.read_bytes()
    original_resource = old_resource.read_bytes()
    rollback_errors: list[str] = []
    try:
        archive = build_fixture_archive(original_resource)
        fetch_fixture_source(root)
        update_upstream.atomic_write(new_resource, archive)
        update_upstream.atomic_write(lock_path, update_upstream.render_lock(FIXTURE_PROPERTIES))
        old_resource.unlink()
        verify(root)
        update_upstream.validate_change_inventory(root, BASE_PROPERTIES, FIXTURE_PROPERTIES)
    except Exception as error:
        try:
            update_upstream.git(source, "checkout", "--detach", original_commit)
        except update_upstream.UpstreamUpdateError as rollback_error:
            rollback_errors.append(str(rollback_error))
        try:
            update_upstream.atomic_write(lock_path, original_lock)
            update_upstream.atomic_write(old_resource, original_resource)
        except OSError as rollback_error:
            rollback_errors.append(f"unable to restore fixture inputs: {rollback_error}")
        try:
            if new_resource.exists():
                new_resource.unlink()
        except OSError as rollback_error:
            rollback_errors.append(f"unable to remove controlled resource: {rollback_error}")
        detail = f"; rollback errors: {'; '.join(rollback_errors)}" if rollback_errors else ""
        if isinstance(error, ControlledAcceptanceError):
            raise ControlledAcceptanceError(f"{error}{detail}") from None
        if isinstance(error, (update_upstream.UpstreamUpdateError, verify_upstream.VerificationError)):
            raise ControlledAcceptanceError(f"unable to prepare controlled fixture: {error}{detail}") from None
        raise ControlledAcceptanceError(f"unable to prepare controlled fixture: {error}{detail}") from None
    return result


def append_workflow_outputs(result: AcceptanceResult) -> None:
    path_value = os.environ.get("GITHUB_OUTPUT", "").strip()
    if not path_value:
        return
    outputs = {
        "update_available": "true",
        "candidate_kind": "controlled",
        "locked_version": result.locked["OPENCC_VERSION"],
        "latest_version": result.proposed["OPENCC_VERSION"],
        "latest_tag": result.proposed["OPENCC_TAG"],
        "latest_commit": result.proposed["OPENCC_COMMIT"],
        "latest_asset": result.proposed["OPENCC_RESOURCE_ASSET"],
        "latest_resource_sha256": result.proposed["OPENCC_RESOURCE_SHA256"],
        "branch_name": result.branch_name,
        "commit_title": result.commit_title,
    }
    with Path(path_value).open("a", encoding="utf-8") as output:
        for name, value in outputs.items():
            require("\n" not in value and "\r" not in value, f"workflow output {name} contains a newline")
            output.write(f"{name}={value}\n")


def append_workflow_summary(result: AcceptanceResult, operation: str) -> None:
    path_value = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if not path_value:
        return
    with Path(path_value).open("a", encoding="utf-8") as summary:
        summary.write("## Controlled OpenCC automation acceptance\n\n")
        summary.write(f"- Operation: `{operation}`\n")
        summary.write(f"- Fixture: `{FIXTURE_ID}`\n")
        summary.write(f"- Branch: `{result.branch_name}`\n")
        summary.write("- Safety: draft-only, `pr-only`, deliberately non-release tag\n")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("inspect", "prepare", "verify"))
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--api-base", default=check_upstream.DEFAULT_API_BASE, help="OpenCC GitHub API URL")
    parser.add_argument("--pr-body-file", type=Path, help="write the controlled draft body here")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    root = arguments.root.resolve()
    try:
        if arguments.operation == "verify":
            verify(root)
            return 0
        result = inspect(root, arguments.api_base) if arguments.operation == "inspect" else prepare(root, arguments.api_base)
        if arguments.operation == "prepare" and arguments.pr_body_file is not None:
            update_upstream.atomic_write(arguments.pr_body_file.resolve(), result.pull_request_body.encode("utf-8"))
        append_workflow_outputs(result)
        append_workflow_summary(result, arguments.operation)
    except (ControlledAcceptanceError, check_upstream.UpstreamCheckError, update_upstream.UpstreamUpdateError) as error:
        print(f"OPENCC_CONTROLLED_ACCEPTANCE_ERROR {error}", file=sys.stderr)
        return 1
    print(result.message)
    if arguments.operation == "prepare":
        print(
            "OPENCC_CONTROLLED_ACCEPTANCE_PREPARED "
            f"branch={result.branch_name} commit={FIXTURE_COMMIT} resource_sha256={FIXTURE_ARCHIVE_SHA256}",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
