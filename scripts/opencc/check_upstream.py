#!/usr/bin/env python3
"""Validate the latest official OpenCC release and compare it with the lock file."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

import verify_upstream


DEFAULT_API_BASE = "https://api.github.com/repos/BYVoid/OpenCC"
VERSION_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]+){2}")
USER_AGENT = "AutoJs6-Plugin-OpenCC-upstream-checker/1"


class UpstreamCheckError(Exception):
    pass


def version_tuple(version: str) -> tuple[int, int, int]:
    if VERSION_PATTERN.fullmatch(version) is None:
        raise UpstreamCheckError(f"Unsupported OpenCC version format: {version!r}")
    return tuple(int(part) for part in version.split("."))  # type: ignore[return-value]


def request_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def read_url(url: str, maximum_bytes: int | None = None) -> bytes:
    request = urllib.request.Request(url, headers=request_headers())
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if maximum_bytes is None:
                return response.read()
            data = response.read(maximum_bytes + 1)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
        raise UpstreamCheckError(f"Unable to read {url}: {error}") from None
    if len(data) > maximum_bytes:
        raise UpstreamCheckError(f"Response exceeds the expected size limit for {url}")
    return data


def read_json(url: str) -> dict[str, Any]:
    try:
        value = json.loads(read_url(url).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise UpstreamCheckError(f"Invalid GitHub JSON response from {url}: {error}") from None
    if not isinstance(value, dict):
        raise UpstreamCheckError(f"GitHub response must be an object: {url}")
    return value


def resolve_tag_commit(api_base: str, tag: str) -> str:
    encoded_tag = urllib.parse.quote(tag, safe="")
    reference = read_json(f"{api_base}/git/ref/tags/{encoded_tag}")
    target = reference.get("object")
    for _ in range(8):
        if not isinstance(target, dict):
            raise UpstreamCheckError(f"Malformed Git object for tag {tag}")
        object_type = target.get("type")
        sha = str(target.get("sha", "")).lower()
        if re.fullmatch(r"[0-9a-f]{40}", sha) is None:
            raise UpstreamCheckError(f"Malformed Git SHA for tag {tag}: {sha!r}")
        if object_type == "commit":
            return sha
        if object_type != "tag":
            raise UpstreamCheckError(f"Tag {tag} resolves to unsupported Git object type: {object_type!r}")
        target = read_json(f"{api_base}/git/tags/{sha}").get("object")
    raise UpstreamCheckError(f"Tag {tag} contains too many nested tag objects")


def release_asset(release: dict[str, Any], expected_name: str) -> dict[str, Any]:
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise UpstreamCheckError("Latest OpenCC release has no asset list")
    matches = [asset for asset in assets if isinstance(asset, dict) and asset.get("name") == expected_name]
    if len(matches) != 1:
        raise UpstreamCheckError(
            f"Expected exactly one official resource asset {expected_name!r}, found {len(matches)}",
        )
    return matches[0]


def validate_release(api_base: str, source_url: str) -> dict[str, str]:
    release = read_json(f"{api_base}/releases/latest")
    if release.get("draft") is not False or release.get("prerelease") is not False:
        raise UpstreamCheckError("GitHub latest release must be a published, non-prerelease release")

    tag = str(release.get("tag_name", ""))
    if not tag.startswith("ver."):
        raise UpstreamCheckError(f"Unexpected OpenCC release tag: {tag!r}")
    version = tag.removeprefix("ver.")
    version_tuple(version)
    expected_asset_name = f"opencc-v{version}-resources.zip"
    asset = release_asset(release, expected_asset_name)

    try:
        asset_size = int(asset["size"])
    except (KeyError, TypeError, ValueError):
        raise UpstreamCheckError(f"Invalid size for GitHub asset {expected_asset_name}") from None
    if asset_size <= 0 or asset_size > 64 * 1024 * 1024:
        raise UpstreamCheckError(f"Unsafe GitHub asset size for {expected_asset_name}: {asset_size}")

    digest_value = str(asset.get("digest", ""))
    if not digest_value.startswith("sha256:"):
        raise UpstreamCheckError(f"GitHub asset has no SHA-256 digest: {expected_asset_name}")
    github_digest = digest_value.removeprefix("sha256:").lower()
    if re.fullmatch(r"[0-9a-f]{64}", github_digest) is None:
        raise UpstreamCheckError(f"Malformed GitHub asset digest: {digest_value!r}")

    download_url = str(asset.get("browser_download_url", ""))
    expected_prefix = f"https://github.com/BYVoid/OpenCC/releases/download/{tag}/"
    if not download_url.startswith(expected_prefix):
        raise UpstreamCheckError(f"Unexpected OpenCC asset download URL: {download_url!r}")
    archive_data = read_url(download_url, maximum_bytes=asset_size)
    if len(archive_data) != asset_size:
        raise UpstreamCheckError(
            f"Downloaded resource size mismatch: expected={asset_size}, actual={len(archive_data)}",
        )
    actual_digest = hashlib.sha256(archive_data).hexdigest()
    if actual_digest != github_digest:
        raise UpstreamCheckError(
            f"Downloaded resource digest mismatch: GitHub={github_digest}, actual={actual_digest}",
        )

    commit = resolve_tag_commit(api_base, tag)
    try:
        with zipfile.ZipFile(io.BytesIO(archive_data)) as archive:
            manifest = json.loads(archive.read(verify_upstream.RESOURCE_MANIFEST).decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        raise UpstreamCheckError(f"Invalid official OpenCC resource manifest: {error}") from None
    manifest_version = manifest.get("manifest_version")
    if not isinstance(manifest_version, int):
        raise UpstreamCheckError(f"Invalid resource manifest version: {manifest_version!r}")

    properties = {
        "OPENCC_VERSION": version,
        "OPENCC_TAG": tag,
        "OPENCC_COMMIT": commit,
        "OPENCC_SOURCE_URL": source_url,
        "OPENCC_RESOURCE_ASSET": expected_asset_name,
        "OPENCC_RESOURCE_SHA256": actual_digest,
        "OPENCC_RESOURCE_SIZE": str(asset_size),
        "OPENCC_RESOURCE_MANIFEST_VERSION": str(manifest_version),
    }
    with tempfile.TemporaryDirectory(prefix="opencc-upstream-check-") as temporary:
        root = Path(temporary)
        asset_directory = root / verify_upstream.ASSET_DIRECTORY
        asset_directory.mkdir(parents=True)
        (asset_directory / expected_asset_name).write_bytes(archive_data)
        try:
            verify_upstream.verify_resource_archive(root, properties)
        except verify_upstream.VerificationError as error:
            raise UpstreamCheckError(str(error)) from None
    return properties


def compare(root: Path, api_base: str) -> tuple[bool, str]:
    try:
        locked = verify_upstream.parse_properties(root / verify_upstream.LOCK_FILE)
    except verify_upstream.VerificationError as error:
        raise UpstreamCheckError(str(error)) from None
    latest = validate_release(api_base.rstrip("/"), locked["OPENCC_SOURCE_URL"])

    locked_version = version_tuple(locked["OPENCC_VERSION"])
    latest_version = version_tuple(latest["OPENCC_VERSION"])
    if latest_version < locked_version:
        raise UpstreamCheckError(
            f"GitHub latest version {latest['OPENCC_VERSION']} is older than locked version "
            f"{locked['OPENCC_VERSION']}",
        )
    if latest_version == locked_version:
        drift = {
            key: (locked[key], latest[key])
            for key in sorted(verify_upstream.REQUIRED_PROPERTIES)
            if locked[key].lower() != latest[key].lower()
        }
        if drift:
            details = ", ".join(f"{key}={old!r}->{new!r}" for key, (old, new) in drift.items())
            raise UpstreamCheckError(f"Locked release metadata drifted from GitHub: {details}")
        return False, (
            "OPENCC_UPSTREAM_CURRENT "
            f"version={locked['OPENCC_VERSION']} tag={locked['OPENCC_TAG']} "
            f"commit={locked['OPENCC_COMMIT']} resource_sha256={locked['OPENCC_RESOURCE_SHA256']}"
        )

    return True, (
        "OPENCC_UPSTREAM_UPDATE "
        f"locked={locked['OPENCC_VERSION']} latest={latest['OPENCC_VERSION']} "
        f"tag={latest['OPENCC_TAG']} commit={latest['OPENCC_COMMIT']} "
        f"resource_sha256={latest['OPENCC_RESOURCE_SHA256']}"
    )


def append_workflow_summary(message: str) -> None:
    path_value = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if not path_value:
        return
    with Path(path_value).open("a", encoding="utf-8") as summary:
        summary.write("## OpenCC upstream check\n\n")
        summary.write(f"`{message}`\n")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="GitHub repository API URL")
    parser.add_argument(
        "--fail-on-update",
        action="store_true",
        help="return exit code 3 when a newer validated release is available",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        update_available, message = compare(arguments.root.resolve(), arguments.api_base)
    except UpstreamCheckError as error:
        print(f"OPENCC_UPSTREAM_CHECK_ERROR {error}", file=sys.stderr)
        return 1
    print(message)
    append_workflow_summary(message)
    if update_available and arguments.fail_on_update:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
