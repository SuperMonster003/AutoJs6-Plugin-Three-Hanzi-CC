#!/usr/bin/env python3
"""Verify that the pinned OpenCC source and official resource ZIP are one release."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


LOCK_FILE = "opencc-upstream.properties"
SOURCE_DIRECTORY = Path("opencc-native/src/main/cpp/third_party/OpenCC")
ASSET_DIRECTORY = Path("opencc-native/src/main/assets/opencc")
RESOURCE_MANIFEST = "opencc-resource-manifest.json"

REQUIRED_PROPERTIES = {
    "OPENCC_VERSION",
    "OPENCC_TAG",
    "OPENCC_COMMIT",
    "OPENCC_SOURCE_URL",
    "OPENCC_RESOURCE_ASSET",
    "OPENCC_RESOURCE_SHA256",
    "OPENCC_RESOURCE_SIZE",
    "OPENCC_RESOURCE_MANIFEST_VERSION",
}

EXPECTED_CONFIGS = {
    "hk2s.json",
    "hk2sp.json",
    "hk2t.json",
    "jp2t.json",
    "s2hk.json",
    "s2hkp.json",
    "s2t.json",
    "s2tw.json",
    "s2twp.json",
    "t2hk.json",
    "t2jp.json",
    "t2s.json",
    "t2tw.json",
    "tw2s.json",
    "tw2sp.json",
    "tw2t.json",
}


class VerificationError(Exception):
    pass


def parse_properties(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise VerificationError(f"OpenCC lock file is missing: {path}")
    properties: dict[str, str] = {}
    for line_number, source_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = source_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        if "=" not in line:
            raise VerificationError(f"Malformed property at {path}:{line_number}: {source_line!r}")
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not name or not value:
            raise VerificationError(f"Empty property at {path}:{line_number}: {source_line!r}")
        if name in properties:
            raise VerificationError(f"Duplicate property {name!r} in {path}")
        properties[name] = value
    missing = REQUIRED_PROPERTIES - properties.keys()
    unexpected = properties.keys() - REQUIRED_PROPERTIES
    if missing or unexpected:
        raise VerificationError(
            f"Unexpected OpenCC lock schema: missing={sorted(missing)}, unexpected={sorted(unexpected)}",
        )
    return properties


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(source: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(source), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        raise VerificationError("git is unavailable") from None
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or str(error)
        raise VerificationError(f"git {' '.join(arguments)} failed for {source}: {detail}") from None
    return result.stdout.strip()


def normalized_repository_url(url: str) -> str:
    return url.removesuffix(".git").rstrip("/").lower()


def verify_source(root: Path, properties: dict[str, str]) -> None:
    source = root / SOURCE_DIRECTORY
    if not (source / "CMakeLists.txt").is_file():
        raise VerificationError(
            f"OpenCC submodule is missing at {source}; run git submodule update --init --recursive",
        )
    actual_commit = git(source, "rev-parse", "HEAD").lower()
    expected_commit = properties["OPENCC_COMMIT"].lower()
    if actual_commit != expected_commit:
        raise VerificationError(
            f"OpenCC source commit mismatch: expected={expected_commit}, actual={actual_commit}",
        )
    actual_tag = git(source, "describe", "--tags", "--exact-match")
    if actual_tag != properties["OPENCC_TAG"]:
        raise VerificationError(
            f"OpenCC source tag mismatch: expected={properties['OPENCC_TAG']}, actual={actual_tag}",
        )
    dirty = git(source, "status", "--porcelain", "--untracked-files=all")
    if dirty:
        raise VerificationError(f"OpenCC submodule contains local changes:\n{dirty}")
    actual_remote = git(source, "remote", "get-url", "origin")
    if normalized_repository_url(actual_remote) != normalized_repository_url(properties["OPENCC_SOURCE_URL"]):
        raise VerificationError(
            f"OpenCC source remote mismatch: expected={properties['OPENCC_SOURCE_URL']}, actual={actual_remote}",
        )


def is_safe_entry_name(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def referenced_resource_files(value: Any) -> set[str]:
    references: set[str] = set()
    if isinstance(value, dict):
        file_name = value.get("file")
        if isinstance(file_name, str):
            references.add(file_name)
        for child in value.values():
            references.update(referenced_resource_files(child))
    elif isinstance(value, list):
        for child in value:
            references.update(referenced_resource_files(child))
    return references


def require_int(properties: dict[str, str], name: str) -> int:
    try:
        return int(properties[name])
    except ValueError:
        raise VerificationError(f"{name} must be an integer, found {properties[name]!r}") from None


def verify_resource_archive(root: Path, properties: dict[str, str]) -> tuple[int, int]:
    archive_path = root / ASSET_DIRECTORY / properties["OPENCC_RESOURCE_ASSET"]
    if not archive_path.is_file():
        raise VerificationError(f"OpenCC resource archive is missing: {archive_path}")

    expected_size = require_int(properties, "OPENCC_RESOURCE_SIZE")
    actual_size = archive_path.stat().st_size
    if actual_size != expected_size:
        raise VerificationError(
            f"OpenCC resource size mismatch: expected={expected_size}, actual={actual_size}",
        )
    actual_archive_digest = sha256_file(archive_path)
    expected_archive_digest = properties["OPENCC_RESOURCE_SHA256"].lower()
    if actual_archive_digest != expected_archive_digest:
        raise VerificationError(
            f"OpenCC resource SHA-256 mismatch: expected={expected_archive_digest}, "
            f"actual={actual_archive_digest}",
        )

    try:
        archive = zipfile.ZipFile(archive_path)
    except zipfile.BadZipFile:
        raise VerificationError(f"OpenCC resource is not a valid ZIP: {archive_path}") from None

    with archive:
        corrupt_entry = archive.testzip()
        if corrupt_entry is not None:
            raise VerificationError(f"Corrupt OpenCC ZIP entry: {corrupt_entry}")

        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise VerificationError("OpenCC resource ZIP contains duplicate entry names")
        unsafe = sorted(name for name in names if not is_safe_entry_name(name))
        if unsafe:
            raise VerificationError(f"OpenCC resource ZIP contains unsafe entries: {unsafe}")
        compressed = sorted(info.filename for info in infos if info.compress_type != zipfile.ZIP_STORED)
        if compressed:
            raise VerificationError(
                "OpenCC ZipResourceProvider requires stored entries; compressed entries found: "
                f"{compressed}",
            )
        if RESOURCE_MANIFEST not in names:
            raise VerificationError(f"OpenCC resource manifest is missing: {RESOURCE_MANIFEST}")

        try:
            manifest = json.loads(archive.read(RESOURCE_MANIFEST).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise VerificationError(f"Invalid OpenCC resource manifest: {error}") from None

        expected_manifest_version = require_int(properties, "OPENCC_RESOURCE_MANIFEST_VERSION")
        if manifest.get("manifest_version") != expected_manifest_version:
            raise VerificationError(
                f"OpenCC resource manifest version mismatch: expected={expected_manifest_version}, "
                f"actual={manifest.get('manifest_version')!r}",
            )
        if manifest.get("hash_algorithm") != "sha256":
            raise VerificationError(f"Unsupported OpenCC manifest hash algorithm: {manifest.get('hash_algorithm')!r}")
        if manifest.get("source_dirty") is not False:
            raise VerificationError("OpenCC resource manifest was produced from a dirty source tree")
        if str(manifest.get("commit_id", "")).lower() != properties["OPENCC_COMMIT"].lower():
            raise VerificationError(
                f"OpenCC resource commit mismatch: expected={properties['OPENCC_COMMIT']}, "
                f"actual={manifest.get('commit_id')!r}",
            )
        if normalized_repository_url(str(manifest.get("source_url", ""))) != normalized_repository_url(
            properties["OPENCC_SOURCE_URL"],
        ):
            raise VerificationError(
                f"OpenCC resource source URL mismatch: expected={properties['OPENCC_SOURCE_URL']}, "
                f"actual={manifest.get('source_url')!r}",
            )

        manifest_entries = manifest.get("entries")
        if not isinstance(manifest_entries, dict):
            raise VerificationError("OpenCC resource manifest entries must be an object")
        archive_payload_names = set(names) - {RESOURCE_MANIFEST}
        if set(manifest_entries) != archive_payload_names:
            raise VerificationError(
                "OpenCC resource manifest inventory mismatch: "
                f"missing={sorted(archive_payload_names - set(manifest_entries))}, "
                f"unexpected={sorted(set(manifest_entries) - archive_payload_names)}",
            )

        for name in sorted(archive_payload_names):
            metadata = manifest_entries[name]
            if not isinstance(metadata, dict):
                raise VerificationError(f"OpenCC manifest metadata must be an object: {name}")
            data = archive.read(name)
            if metadata.get("size") != len(data):
                raise VerificationError(
                    f"OpenCC resource entry size mismatch for {name}: "
                    f"expected={metadata.get('size')!r}, actual={len(data)}",
                )
            digest = sha256_bytes(data)
            if str(metadata.get("sha256", "")).lower() != digest:
                raise VerificationError(
                    f"OpenCC resource entry SHA-256 mismatch for {name}: "
                    f"expected={metadata.get('sha256')!r}, actual={digest}",
                )

        configs = {name for name in archive_payload_names if name.endswith(".json")}
        if configs != EXPECTED_CONFIGS:
            raise VerificationError(
                f"Unexpected OpenCC configuration inventory: missing={sorted(EXPECTED_CONFIGS - configs)}, "
                f"unexpected={sorted(configs - EXPECTED_CONFIGS)}",
            )
        for config_name in sorted(configs):
            try:
                config = json.loads(archive.read(config_name).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise VerificationError(f"Invalid OpenCC configuration {config_name}: {error}") from None
            missing_references = referenced_resource_files(config) - archive_payload_names
            if missing_references:
                raise VerificationError(
                    f"OpenCC configuration {config_name} references missing resources: "
                    f"{sorted(missing_references)}",
                )

        return len(infos), len(configs)


def verify(root: Path) -> None:
    properties = parse_properties(root / LOCK_FILE)
    verify_source(root, properties)
    entries, configs = verify_resource_archive(root, properties)
    print(
        "OPENCC_UPSTREAM_OK "
        f"version={properties['OPENCC_VERSION']} "
        f"tag={properties['OPENCC_TAG']} "
        f"commit={properties['OPENCC_COMMIT']} "
        f"resource_sha256={properties['OPENCC_RESOURCE_SHA256']} "
        f"entries={entries} configs={configs}",
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        verify(arguments.root.resolve())
    except VerificationError as error:
        print(f"OPENCC_UPSTREAM_ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
