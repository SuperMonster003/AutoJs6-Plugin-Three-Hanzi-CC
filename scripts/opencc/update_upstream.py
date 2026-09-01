#!/usr/bin/env python3
"""Prepare an exact, review-only OpenCC upstream upgrade in a clean checkout."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

import check_upstream
import verify_upstream


LOCK_PROPERTY_ORDER = (
    "OPENCC_VERSION",
    "OPENCC_TAG",
    "OPENCC_COMMIT",
    "OPENCC_SOURCE_URL",
    "OPENCC_RESOURCE_ASSET",
    "OPENCC_RESOURCE_SHA256",
    "OPENCC_RESOURCE_SIZE",
    "OPENCC_RESOURCE_MANIFEST_VERSION",
)
LOCK_HEADER = (
    "# Reproducible upstream lock for the OpenCC native engine and resource bundle.\n"
    "# Update all fields together; scripts/opencc/verify_upstream.py rejects mixed releases.\n"
)
RESOURCE_NAME_PATTERN = re.compile(r"opencc-v[0-9]+(?:\.[0-9]+){2}-resources\.zip")
AUTOMATION_BRANCH_PREFIX = "automation/opencc-"
MAX_RELEASE_NOTES_CHARACTERS = 12_000


class UpstreamUpdateError(Exception):
    pass


@dataclass(frozen=True)
class UpdateResult:
    update_available: bool
    message: str
    locked: dict[str, str]
    latest: dict[str, str]
    release: check_upstream.ValidatedRelease
    branch_name: str
    commit_title: str
    pull_request_body: str


def git(repository: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        raise UpstreamUpdateError("git is unavailable") from None
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or str(error)
        raise UpstreamUpdateError(
            f"git {' '.join(arguments)} failed for {repository}: {detail}",
        ) from None
    return result.stdout.strip()


def ensure_clean_worktree(root: Path) -> None:
    status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise UpstreamUpdateError(f"Refusing to update a non-clean checkout:\n{status}")


def render_lock(properties: dict[str, str]) -> bytes:
    missing = set(LOCK_PROPERTY_ORDER) - properties.keys()
    unexpected = properties.keys() - set(LOCK_PROPERTY_ORDER)
    if missing or unexpected:
        raise UpstreamUpdateError(
            f"Unexpected validated lock schema: missing={sorted(missing)}, unexpected={sorted(unexpected)}",
        )
    lines = [f"{name}={properties[name]}" for name in LOCK_PROPERTY_ORDER]
    return (LOCK_HEADER + "\n".join(lines) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def safe_resource_path(root: Path, asset_name: str) -> Path:
    if RESOURCE_NAME_PATTERN.fullmatch(asset_name) is None or Path(asset_name).name != asset_name:
        raise UpstreamUpdateError(f"Unsafe OpenCC resource asset name: {asset_name!r}")
    asset_root = (root / verify_upstream.ASSET_DIRECTORY).resolve()
    path = (asset_root / asset_name).resolve()
    try:
        path.relative_to(asset_root)
    except ValueError:
        raise UpstreamUpdateError(f"OpenCC resource asset escapes its directory: {asset_name!r}") from None
    return path


def update_submodule(root: Path, tag: str, commit: str) -> None:
    source = (root / verify_upstream.SOURCE_DIRECTORY).resolve()
    if not (source / ".git").exists() and not (source / "CMakeLists.txt").is_file():
        raise UpstreamUpdateError(
            f"OpenCC submodule is unavailable at {source}; check it out recursively before updating",
        )
    actual_remote = git(source, "remote", "get-url", "origin")
    if verify_upstream.normalized_repository_url(actual_remote) != verify_upstream.normalized_repository_url(
        "https://github.com/BYVoid/OpenCC.git",
    ):
        raise UpstreamUpdateError(f"Refusing unexpected OpenCC submodule remote: {actual_remote}")

    git(source, "fetch", "--no-tags", "origin", f"refs/tags/{tag}:refs/tags/{tag}")
    resolved_commit = git(source, "rev-parse", f"refs/tags/{tag}^{{commit}}").lower()
    if resolved_commit != commit.lower():
        raise UpstreamUpdateError(
            f"Fetched OpenCC tag commit mismatch: API={commit.lower()}, git={resolved_commit}",
        )
    git(source, "checkout", "--detach", commit)


def changed_paths(root: Path) -> set[str]:
    status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    paths: set[str] = set()
    for line in status.splitlines():
        if len(line) < 4:
            raise UpstreamUpdateError(f"Malformed git status line: {line!r}")
        path_value = line[3:]
        if " -> " in path_value:
            previous, current = path_value.split(" -> ", 1)
            paths.update((previous, current))
        else:
            paths.add(path_value)
    return paths


def expected_update_paths(locked: dict[str, str], latest: dict[str, str]) -> set[str]:
    paths = {
        verify_upstream.LOCK_FILE,
        verify_upstream.SOURCE_DIRECTORY.as_posix(),
        (verify_upstream.ASSET_DIRECTORY / locked["OPENCC_RESOURCE_ASSET"]).as_posix(),
        (verify_upstream.ASSET_DIRECTORY / latest["OPENCC_RESOURCE_ASSET"]).as_posix(),
    }
    return paths


def validate_change_inventory(root: Path, locked: dict[str, str], latest: dict[str, str]) -> None:
    expected = expected_update_paths(locked, latest)
    actual = {path.replace("\\", "/") for path in changed_paths(root)}
    if actual != expected:
        raise UpstreamUpdateError(
            f"Unexpected generated update inventory: missing={sorted(expected - actual)}, "
            f"unexpected={sorted(actual - expected)}",
        )


def apply_validated_release(
    root: Path,
    locked: dict[str, str],
    release: check_upstream.ValidatedRelease,
) -> None:
    latest = release.properties
    update_available, _ = check_upstream.compare_properties(locked, latest)
    if not update_available:
        raise UpstreamUpdateError("Refusing to apply a release that is not newer than the lock")

    ensure_clean_worktree(root)
    try:
        verify_upstream.verify(root)
    except verify_upstream.VerificationError as error:
        raise UpstreamUpdateError(f"Current OpenCC lock is invalid before update: {error}") from None

    lock_path = (root / verify_upstream.LOCK_FILE).resolve()
    source = (root / verify_upstream.SOURCE_DIRECTORY).resolve()
    old_resource = safe_resource_path(root, locked["OPENCC_RESOURCE_ASSET"])
    new_resource = safe_resource_path(root, latest["OPENCC_RESOURCE_ASSET"])
    if old_resource == new_resource:
        raise UpstreamUpdateError("A newer OpenCC release must use a new versioned resource asset name")
    if not old_resource.is_file():
        raise UpstreamUpdateError(f"Locked OpenCC resource is missing before update: {old_resource}")
    if new_resource.exists():
        raise UpstreamUpdateError(f"Refusing to replace a pre-existing future OpenCC resource: {new_resource}")

    original_commit = git(source, "rev-parse", "HEAD")
    original_lock = lock_path.read_bytes()
    original_resource = old_resource.read_bytes()
    rollback_errors: list[str] = []
    try:
        update_submodule(root, latest["OPENCC_TAG"], latest["OPENCC_COMMIT"])
        atomic_write(new_resource, release.archive_data)
        atomic_write(lock_path, render_lock(latest))
        verify_upstream.verify(root)
        old_resource.unlink()
        verify_upstream.verify(root)
        validate_change_inventory(root, locked, latest)
    except Exception as error:
        try:
            git(source, "checkout", "--detach", original_commit)
        except UpstreamUpdateError as rollback_error:
            rollback_errors.append(str(rollback_error))
        try:
            atomic_write(lock_path, original_lock)
        except OSError as rollback_error:
            rollback_errors.append(f"Unable to restore lock file: {rollback_error}")
        try:
            atomic_write(old_resource, original_resource)
        except OSError as rollback_error:
            rollback_errors.append(f"Unable to restore original resource: {rollback_error}")
        try:
            if new_resource.exists():
                new_resource.unlink()
        except OSError as rollback_error:
            rollback_errors.append(f"Unable to remove staged resource: {rollback_error}")
        detail = f"; rollback errors: {'; '.join(rollback_errors)}" if rollback_errors else ""
        if isinstance(error, UpstreamUpdateError):
            raise UpstreamUpdateError(f"{error}{detail}") from None
        if isinstance(error, verify_upstream.VerificationError):
            raise UpstreamUpdateError(f"Generated OpenCC update failed verification: {error}{detail}") from None
        raise UpstreamUpdateError(f"Unable to apply validated OpenCC update: {error}{detail}") from None


def quoted_upstream_notes(notes: str) -> str:
    value = notes.strip() or "No upstream release notes were provided."
    if len(value) > MAX_RELEASE_NOTES_CHARACTERS:
        value = value[:MAX_RELEASE_NOTES_CHARACTERS].rstrip() + "\n\n[Release notes truncated; use the upstream link.]"
    value = value.replace("@", "@<!-- -->")
    return "\n".join(f"> {line}" if line else ">" for line in value.splitlines())


def render_pull_request_body(
    locked: dict[str, str],
    release: check_upstream.ValidatedRelease,
) -> str:
    latest = release.properties
    old_tag = urllib.parse.quote(locked["OPENCC_TAG"], safe="")
    new_tag = urllib.parse.quote(latest["OPENCC_TAG"], safe="")
    compare_url = f"https://github.com/BYVoid/OpenCC/compare/{old_tag}...{new_tag}"
    return f"""## Validated upstream release

| Field | Locked | Proposed |
|---|---|---|
| Version | `{locked['OPENCC_VERSION']}` | `{latest['OPENCC_VERSION']}` |
| Tag | `{locked['OPENCC_TAG']}` | `{latest['OPENCC_TAG']}` |
| Commit | `{locked['OPENCC_COMMIT']}` | `{latest['OPENCC_COMMIT']}` |
| Resource | `{locked['OPENCC_RESOURCE_ASSET']}` | `{latest['OPENCC_RESOURCE_ASSET']}` |
| Resource bytes | `{locked['OPENCC_RESOURCE_SIZE']}` | `{latest['OPENCC_RESOURCE_SIZE']}` |
| Resource SHA-256 | `{locked['OPENCC_RESOURCE_SHA256']}` | `{latest['OPENCC_RESOURCE_SHA256']}` |

- Upstream release: {release.release_url}
- Upstream source comparison: {compare_url}
- Published at: `{release.published_at or 'unknown'}`

The automation resolved the formal `ver.*` tag to its final commit, matched the GitHub asset digest and
size, downloaded the resource ZIP, and verified its manifest commit, source URL, complete file inventory,
per-file SHA-256 values, stored-entry requirement, and 16 supported configuration files before changing
the submodule pointer, lock file, or bundled resource.

## Upstream release summary

{quoted_upstream_notes(release.release_body)}

## Required human review and merge gates

- [ ] Review the upstream source and license changes; update `THIRD_PARTY_NOTICES.md` if needed.
- [ ] Review every changed or failed conversion fixture individually. Never blanket-accept dictionary output drift.
- [ ] Require the dispatched Build integrity run: four ABIs, debug/release APK audits, Binder tests, RELRO,
      16 KB ELF/ZIP alignment, and a real 16 KB emulator must all pass.
- [ ] Require the dispatched Markdown integrity run and review the reported APK byte sizes.
- [ ] Update migration notes, localized changelog/docs, and release metadata before any later public release.
- [ ] Merge manually only after review. This automation never enables auto-merge and never creates a release.

Generated by `.github/workflows/opencc-upstream.yml` and `scripts/opencc/update_upstream.py`.
"""


def prepare_update(root: Path, api_base: str) -> UpdateResult:
    ensure_clean_worktree(root)
    try:
        verify_upstream.verify(root)
        locked = verify_upstream.parse_properties(root / verify_upstream.LOCK_FILE)
    except verify_upstream.VerificationError as error:
        raise UpstreamUpdateError(str(error)) from None

    release = check_upstream.download_validated_release(
        api_base.rstrip("/"),
        locked["OPENCC_SOURCE_URL"],
    )
    update_available, message = check_upstream.compare_properties(locked, release.properties)
    if not update_available:
        return UpdateResult(False, message, locked, release.properties, release, "", "", "")

    apply_validated_release(root, locked, release)
    version = release.properties["OPENCC_VERSION"]
    title = f"chore(deps): upgrade OpenCC to {version}"
    return UpdateResult(
        True,
        message,
        locked,
        release.properties,
        release,
        f"{AUTOMATION_BRANCH_PREFIX}{version}",
        title,
        render_pull_request_body(locked, release),
    )


def append_workflow_outputs(result: UpdateResult) -> None:
    path_value = os.environ.get("GITHUB_OUTPUT", "").strip()
    if not path_value:
        return
    outputs = {
        "update_available": str(result.update_available).lower(),
        "locked_version": result.locked["OPENCC_VERSION"],
        "latest_version": result.latest["OPENCC_VERSION"],
        "latest_tag": result.latest["OPENCC_TAG"],
        "latest_commit": result.latest["OPENCC_COMMIT"],
        "latest_asset": result.latest["OPENCC_RESOURCE_ASSET"],
        "latest_resource_sha256": result.latest["OPENCC_RESOURCE_SHA256"],
        "branch_name": result.branch_name,
        "commit_title": result.commit_title,
    }
    with Path(path_value).open("a", encoding="utf-8") as output:
        for name, value in outputs.items():
            if "\n" in value or "\r" in value:
                raise UpstreamUpdateError(f"Workflow output {name} unexpectedly contains a newline")
            output.write(f"{name}={value}\n")


def append_workflow_summary(result: UpdateResult) -> None:
    path_value = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if not path_value:
        return
    with Path(path_value).open("a", encoding="utf-8") as summary:
        summary.write("## OpenCC upstream upgrade preparation\n\n")
        summary.write(f"`{result.message}`\n\n")
        if result.update_available:
            summary.write(f"Prepared branch `{result.branch_name}` with `{result.commit_title}`.\n")
        else:
            summary.write("The validated formal release exactly matches the repository lock; no files changed.\n")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--api-base", default=check_upstream.DEFAULT_API_BASE, help="GitHub repository API URL")
    parser.add_argument(
        "--pr-body-file",
        type=Path,
        help="write the generated pull request body here when an update is prepared",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        result = prepare_update(arguments.root.resolve(), arguments.api_base)
        if result.update_available and arguments.pr_body_file is not None:
            atomic_write(arguments.pr_body_file.resolve(), result.pull_request_body.encode("utf-8"))
        append_workflow_outputs(result)
        append_workflow_summary(result)
    except (UpstreamUpdateError, check_upstream.UpstreamCheckError) as error:
        print(f"OPENCC_UPSTREAM_UPDATE_ERROR {error}", file=sys.stderr)
        return 1
    print(result.message)
    if result.update_available:
        print(
            "OPENCC_UPSTREAM_PREPARED "
            f"branch={result.branch_name} tag={result.latest['OPENCC_TAG']} "
            f"commit={result.latest['OPENCC_COMMIT']} resource_sha256={result.latest['OPENCC_RESOURCE_SHA256']}",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
