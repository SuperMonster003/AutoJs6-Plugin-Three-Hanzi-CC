#!/usr/bin/env python3
"""Finalize a signed, workflow-artifact-only OpenCC release candidate."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.release.prepare_release import (  # noqa: E402
    ABI_ORDER,
    PackageRecord,
    ReleaseContext,
    ReleaseError,
    collect_records,
    find_apksigner,
    load_properties,
    load_release_context,
    render_release_notes,
    sha256,
    verify_signatures,
)


BASELINE_SCHEMA_VERSION = 1
CANDIDATE_SCHEMA_VERSION = 1
EXPECTED_REPOSITORY = "SuperMonster003/AutoJs6-Plugin-OpenCC"
MAX_BASELINE_BYTES = 64 * 1024
MAX_APK_GROWTH_BYTES = 512 * 1024
MAX_APK_GROWTH_PERCENT = 25
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
SHA256_PATTERN = re.compile(r"[0-9A-F]{64}")
VERSION_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]+){2}")
CANDIDATE_MANIFEST = "CANDIDATE.json"
DOCUMENT_NAMES = ("SHA256SUMS.txt", "RELEASE_NOTES.md")
FORBIDDEN_SIGNING_ENTRY_NAMES = {
    "sign.properties",
}
FORBIDDEN_SIGNING_ENTRY_SUFFIXES = (
    ".jks",
    ".keystore",
    ".p12",
    ".pfx",
    ".pem",
    ".pk8",
)


@dataclass(frozen=True)
class CandidateBaseline:
    tag: str
    source_sha: str
    version_name: str
    version_build: int
    signer_certificate_sha256: str
    package_sizes: dict[str, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseError(message)


def require_exact_keys(value: dict[str, Any], expected: set[str], description: str) -> None:
    actual = set(value)
    require(
        actual == expected,
        f"{description} keys mismatch: missing={sorted(expected - actual)}, "
        f"unexpected={sorted(actual - expected)}",
    )


def canonical_source_sha(value: object, description: str = "source SHA") -> str:
    require(isinstance(value, str) and SHA_PATTERN.fullmatch(value) is not None, f"Malformed {description}")
    return value


def canonical_certificate_sha256(value: object, description: str) -> str:
    require(
        isinstance(value, str) and SHA256_PATTERN.fullmatch(value) is not None,
        f"Malformed {description}",
    )
    return value


def canonical_version(value: object, description: str) -> str:
    require(
        isinstance(value, str) and VERSION_PATTERN.fullmatch(value) is not None,
        f"Malformed {description}",
    )
    require(
        all(str(int(part)) == part for part in value.split(".")),
        f"Non-canonical {description}",
    )
    return value


def canonical_positive_integer(value: object, description: str) -> int:
    require(type(value) is int and value > 0, f"{description} must be a positive integer")
    return value


def load_candidate_baseline(path: Path) -> CandidateBaseline:
    path = path.resolve()
    require(path.is_file(), f"Candidate size baseline is missing: {path}")
    require(path.stat().st_size <= MAX_BASELINE_BYTES, f"Candidate size baseline is too large: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReleaseError(f"Invalid candidate size baseline: {error}") from None
    require(isinstance(data, dict), "Candidate size baseline root must be an object")
    require_exact_keys(data, {"schema_version", "release", "package_sizes", "limits"}, "Baseline")
    require(
        type(data["schema_version"]) is int and data["schema_version"] == BASELINE_SCHEMA_VERSION,
        "Unsupported candidate baseline schema",
    )

    release = data["release"]
    require(isinstance(release, dict), "Candidate baseline release must be an object")
    require_exact_keys(
        release,
        {"tag", "source_sha", "version_name", "version_build", "signer_certificate_sha256"},
        "Baseline release",
    )
    version_name = canonical_version(release["version_name"], "baseline version name")
    require(release["tag"] == f"v{version_name}", "Candidate baseline tag/version mismatch")

    package_sizes = data["package_sizes"]
    require(isinstance(package_sizes, dict), "Candidate baseline package_sizes must be an object")
    require_exact_keys(package_sizes, set(ABI_ORDER), "Baseline package_sizes")
    canonical_sizes = {
        abi: canonical_positive_integer(package_sizes[abi], f"Baseline size for {abi}")
        for abi in ABI_ORDER
    }

    limits = data["limits"]
    require(isinstance(limits, dict), "Candidate baseline limits must be an object")
    require_exact_keys(limits, {"max_growth_bytes", "max_growth_percent"}, "Baseline limits")
    require(
        limits["max_growth_bytes"] == MAX_APK_GROWTH_BYTES,
        "Candidate baseline byte-growth policy differs from the controller",
    )
    require(
        limits["max_growth_percent"] == MAX_APK_GROWTH_PERCENT,
        "Candidate baseline percentage-growth policy differs from the controller",
    )

    return CandidateBaseline(
        tag=release["tag"],
        source_sha=canonical_source_sha(release["source_sha"], "baseline source SHA"),
        version_name=version_name,
        version_build=canonical_positive_integer(release["version_build"], "Baseline version build"),
        signer_certificate_sha256=canonical_certificate_sha256(
            release["signer_certificate_sha256"],
            "baseline signer certificate SHA-256",
        ),
        package_sizes=canonical_sizes,
    )


def current_version_build(root: Path) -> int:
    value = load_properties(root / "version.properties").get("VERSION_BUILD", "")
    require(value.isdigit() and str(int(value)) == value and int(value) > 0, "VERSION_BUILD is not canonical")
    return int(value)


def version_tuple(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def verify_version_progression(context: ReleaseContext, version_build: int, baseline: CandidateBaseline) -> None:
    canonical_version(context.version_name, "candidate version name")
    canonical_positive_integer(version_build, "Candidate version build")
    require(
        version_tuple(context.version_name) >= version_tuple(baseline.version_name),
        f"Candidate version {context.version_name} is older than baseline {baseline.version_name}",
    )
    require(
        version_build >= baseline.version_build,
        f"Candidate build {version_build} is older than baseline build {baseline.version_build}",
    )


def git_output(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    require(result.returncode == 0, f"git {' '.join(arguments)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def verify_git_source(root: Path, source_sha: str, baseline: CandidateBaseline) -> None:
    source_sha = canonical_source_sha(source_sha)
    require(git_output(root, "rev-parse", "HEAD") == source_sha, "Candidate source SHA differs from HEAD")
    require(
        git_output(root, "rev-parse", f"refs/tags/{baseline.tag}^{{commit}}") == baseline.source_sha,
        "Candidate baseline tag no longer resolves to its recorded source SHA",
    )
    status = git_output(root, "status", "--porcelain=v1", "--untracked-files=no")
    require(not status, f"Tracked source tree changed during candidate construction: {status}")
    submodules = git_output(root, "submodule", "status", "--recursive")
    unsafe = [line for line in submodules.splitlines() if line.startswith(("-", "+", "U"))]
    require(not unsafe, f"Candidate submodule checkout is incomplete or changed: {unsafe}")


def maximum_candidate_size(baseline_size: int) -> int:
    percentage_limit = baseline_size * (100 + MAX_APK_GROWTH_PERCENT) // 100
    byte_limit = baseline_size + MAX_APK_GROWTH_BYTES
    return min(percentage_limit, byte_limit)


def verify_package_sizes(records: list[PackageRecord], baseline: CandidateBaseline) -> dict[str, int]:
    maximum_sizes: dict[str, int] = {}
    require([record.abi for record in records] == list(ABI_ORDER), "Candidate package order is not canonical")
    for record in records:
        baseline_size = baseline.package_sizes[record.abi]
        maximum_size = maximum_candidate_size(baseline_size)
        require(
            record.size <= maximum_size,
            f"Candidate {record.abi} APK is too large: actual={record.size}, baseline={baseline_size}, "
            f"maximum={maximum_size}",
        )
        maximum_sizes[record.abi] = maximum_size
    return maximum_sizes


def verify_no_signing_material(records: list[PackageRecord]) -> None:
    for record in records:
        try:
            with zipfile.ZipFile(record.source) as archive:
                forbidden = []
                for name in archive.namelist():
                    basename = name.rsplit("/", 1)[-1].lower()
                    if basename in FORBIDDEN_SIGNING_ENTRY_NAMES or basename.endswith(
                        FORBIDDEN_SIGNING_ENTRY_SUFFIXES,
                    ):
                        forbidden.append(name)
        except zipfile.BadZipFile:
            raise ReleaseError(f"Not a valid APK ZIP archive: {record.source}") from None
        require(not forbidden, f"Signing material is packaged in {record.filename}: {sorted(forbidden)}")


def verify_bundle_documents(
    context: ReleaseContext,
    records: list[PackageRecord],
    signer_digest: str,
    bundle: Path,
) -> None:
    checksums = bundle / "SHA256SUMS.txt"
    notes = bundle / "RELEASE_NOTES.md"
    require(checksums.is_file(), f"Candidate checksums are missing: {checksums}")
    require(notes.is_file(), f"Candidate release notes are missing: {notes}")
    try:
        actual_checksums = checksums.read_text(encoding="utf-8")
        actual_notes = notes.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ReleaseError(f"Candidate document is not valid UTF-8: {error}") from None
    expected_checksums = "".join(f"{record.sha256}  {record.filename}\n" for record in records)
    require(
        actual_checksums == expected_checksums,
        "Candidate SHA256SUMS.txt differs from the verified APK inventory",
    )
    expected_notes = render_release_notes(context, records, signer_digest)
    require(
        actual_notes == expected_notes,
        "Candidate RELEASE_NOTES.md differs from the verified release context",
    )


def load_upstream_metadata(root: Path) -> dict[str, object]:
    properties = load_properties(root / "opencc-upstream.properties")
    required = {
        "OPENCC_VERSION",
        "OPENCC_TAG",
        "OPENCC_COMMIT",
        "OPENCC_RESOURCE_ASSET",
        "OPENCC_RESOURCE_SHA256",
        "OPENCC_RESOURCE_SIZE",
    }
    missing = required - set(properties)
    require(not missing, f"OpenCC upstream lock is missing candidate metadata: {sorted(missing)}")
    resource_size = properties["OPENCC_RESOURCE_SIZE"]
    require(resource_size.isdigit() and int(resource_size) > 0, "OpenCC resource size is invalid")
    require(
        re.fullmatch(r"[0-9a-f]{64}", properties["OPENCC_RESOURCE_SHA256"]) is not None,
        "OpenCC resource SHA-256 is invalid",
    )
    canonical_source_sha(properties["OPENCC_COMMIT"], "OpenCC commit")
    return {
        "version": properties["OPENCC_VERSION"],
        "tag": properties["OPENCC_TAG"],
        "commit": properties["OPENCC_COMMIT"],
        "resource_asset": properties["OPENCC_RESOURCE_ASSET"],
        "resource_size": int(resource_size),
        "resource_sha256": properties["OPENCC_RESOURCE_SHA256"],
    }


def candidate_manifest_data(
    context: ReleaseContext,
    bundle: Path,
    source_sha: str,
    version_build: int,
    signer_digest: str,
    records: list[PackageRecord],
    baseline: CandidateBaseline,
    maximum_sizes: dict[str, int],
) -> dict[str, object]:
    documents = {
        name: {
            "size": (bundle / name).stat().st_size,
            "sha256": sha256(bundle / name),
        }
        for name in DOCUMENT_NAMES
    }
    return {
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "artifact_role": "signed-candidate-only",
        "repository": EXPECTED_REPOSITORY,
        "source_sha": source_sha,
        "version": {"name": context.version_name, "build": version_build},
        "opencc": load_upstream_metadata(context.root),
        "signer_certificate_sha256": signer_digest,
        "size_policy": {
            "baseline_tag": baseline.tag,
            "baseline_source_sha": baseline.source_sha,
            "max_growth_bytes": MAX_APK_GROWTH_BYTES,
            "max_growth_percent": MAX_APK_GROWTH_PERCENT,
        },
        "packages": [
            {
                "abi": record.abi,
                "file": record.filename,
                "size": record.size,
                "sha256": record.sha256,
                "crc32": record.crc32,
                "baseline_size": baseline.package_sizes[record.abi],
                "maximum_size": maximum_sizes[record.abi],
            }
            for record in records
        ],
        "documents": documents,
    }


def write_candidate_manifest(bundle: Path, data: dict[str, object]) -> Path:
    destination = bundle / CANDIDATE_MANIFEST
    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        prefix=f".{CANDIDATE_MANIFEST}.",
        dir=bundle,
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        stream.write(payload)
    try:
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return destination


def verify_bundle_inventory(bundle: Path, records: list[PackageRecord]) -> None:
    expected = {record.filename for record in records} | set(DOCUMENT_NAMES) | {CANDIDATE_MANIFEST}
    entries = list(bundle.iterdir())
    unsafe = [entry.name for entry in entries if not entry.is_file() or entry.is_symlink()]
    require(not unsafe, f"Candidate bundle contains non-regular entries: {sorted(unsafe)}")
    actual = {entry.name for entry in entries}
    require(
        actual == expected,
        f"Candidate bundle inventory mismatch: missing={sorted(expected - actual)}, "
        f"unexpected={sorted(actual - expected)}",
    )


def finalize_candidate(
    context: ReleaseContext,
    bundle: Path,
    source_sha: str,
    version_build: int,
    expected_signer_digest: str,
    baseline: CandidateBaseline,
    apksigner: Path,
) -> tuple[list[PackageRecord], Path]:
    source_sha = canonical_source_sha(source_sha)
    expected_signer_digest = canonical_certificate_sha256(
        expected_signer_digest,
        "expected signer certificate SHA-256",
    )
    require(
        expected_signer_digest == baseline.signer_certificate_sha256,
        "Environment signer certificate differs from the published baseline",
    )
    verify_version_progression(context, version_build, baseline)
    records, foreign_versions = collect_records(bundle, context)
    require(not foreign_versions, f"Candidate bundle contains foreign-version APKs: {foreign_versions}")
    signer_digest = verify_signatures(records, apksigner)
    require(
        signer_digest == expected_signer_digest,
        f"Candidate signer certificate changed: expected={expected_signer_digest}, actual={signer_digest}",
    )
    verify_no_signing_material(records)
    maximum_sizes = verify_package_sizes(records, baseline)
    verify_bundle_documents(context, records, signer_digest, bundle)
    manifest = write_candidate_manifest(
        bundle,
        candidate_manifest_data(
            context,
            bundle,
            source_sha,
            version_build,
            signer_digest,
            records,
            baseline,
            maximum_sizes,
        ),
    )
    verify_bundle_inventory(bundle, records)
    return records, manifest


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--bundle", type=Path, help="prepared bundle; defaults to build/release/v<version>")
    parser.add_argument("--source-sha", required=True, help="exact checked-out master commit SHA")
    parser.add_argument(
        "--expected-signer-sha256",
        required=True,
        help="expected release signer certificate SHA-256",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="published release size/signing baseline",
    )
    parser.add_argument("--apksigner", type=Path, help="explicit path to apksigner or apksigner.bat")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        root = arguments.root.resolve()
        context = load_release_context(root)
        version_build = current_version_build(root)
        baseline_path = arguments.baseline or root / "scripts" / "release" / "candidate-baseline.json"
        baseline = load_candidate_baseline(baseline_path)
        verify_git_source(root, arguments.source_sha, baseline)
        bundle = (arguments.bundle or root / "build" / "release" / f"v{context.version_name}").resolve()
        require(bundle.is_dir(), f"Candidate bundle is missing: {bundle}")
        records, manifest = finalize_candidate(
            context,
            bundle,
            arguments.source_sha,
            version_build,
            arguments.expected_signer_sha256,
            baseline,
            find_apksigner(arguments.apksigner),
        )
        for record in records:
            print(
                f"CANDIDATE_PACKAGE_OK abi={record.abi} file={record.filename} "
                f"bytes={record.size} sha256={record.sha256}",
            )
        print(
            f"CANDIDATE_OK source={arguments.source_sha} version={context.version_name} "
            f"build={version_build} packages={len(records)} manifest_sha256={sha256(manifest)}",
        )
        return 0
    except (ReleaseError, OSError) as error:
        print(f"CANDIDATE_ERROR {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
