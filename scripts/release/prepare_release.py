#!/usr/bin/env python3
"""Build and prepare a verified five-APK release bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import zlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ABI_ORDER = ("arm64-v8a", "armeabi-v7a", "x86_64", "x86", "universal")
NATIVE_ABIS = {"arm64-v8a", "armeabi-v7a", "x86_64", "x86"}
CATEGORY_ORDER = ("hint", "feature", "fix", "improvement", "dependency")


class ReleaseError(Exception):
    pass


@dataclass(frozen=True)
class ReleaseContext:
    root: Path
    project_name: str
    version_name: str
    changelog: dict[str, Any]
    release_entry: dict[str, Any]


@dataclass(frozen=True)
class PackageRecord:
    abi: str
    source: Path
    filename: str
    crc32: str
    sha256: str
    size: int


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseError(message)


def load_properties(path: Path) -> dict[str, str]:
    require(path.is_file(), f"Missing properties file: {path}")
    properties: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        key, separator, value = line.partition("=")
        require(bool(separator), f"Invalid properties line in {path}: {raw_line!r}")
        require(key.strip() not in properties, f"Duplicate property {key.strip()!r} in {path}")
        properties[key.strip()] = value.strip()
    return properties


def load_release_context(root: Path) -> ReleaseContext:
    root = root.resolve()
    settings_path = root / "settings.gradle.kts"
    require(settings_path.is_file(), f"Missing Gradle settings: {settings_path}")
    settings = settings_path.read_text(encoding="utf-8")
    project_match = re.search(r'rootProject\.name\s*=\s*"([^"]+)"', settings)
    require(project_match is not None, "Cannot determine rootProject.name from settings.gradle.kts")
    project_name = project_match.group(1)

    properties = load_properties(root / "version.properties")
    version_name = properties.get("VERSION_NAME", "")
    require(bool(version_name), "VERSION_NAME is missing from version.properties")

    changelog_path = root / ".changelog" / "lang_en.json"
    require(changelog_path.is_file(), f"Missing English changelog source: {changelog_path}")
    try:
        changelog = json.loads(changelog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ReleaseError(f"Invalid English changelog JSON: {error}") from None
    require(isinstance(changelog, dict), "English changelog root must be an object")
    data = changelog.get("$data")
    require(isinstance(data, dict) and data, "English changelog has no release entries")
    version_label = f"v{version_name}"
    newest_label = next(iter(data))
    require(
        newest_label == version_label,
        f"Newest English changelog entry {newest_label!r} does not match {version_label!r}",
    )
    release_entry = data.get(version_label)
    require(isinstance(release_entry, dict), f"Missing English changelog entry for {version_label}")
    return ReleaseContext(root, project_name, version_name, changelog, release_entry)


def run_release_build(context: ReleaseContext) -> None:
    wrapper = context.root / ("gradlew.bat" if os.name == "nt" else "gradlew")
    require(wrapper.is_file(), f"Missing Gradle wrapper: {wrapper}")
    if os.name == "nt":
        command = ["cmd.exe", "/d", "/c", str(wrapper), ":app:assembleRelease", "--stacktrace"]
    else:
        command = [str(wrapper), ":app:assembleRelease", "--stacktrace"]
    print("Running signed release build...")
    try:
        subprocess.run(command, cwd=context.root, check=True)
    except subprocess.CalledProcessError as error:
        raise ReleaseError(f"Gradle release build failed with exit code {error.returncode}") from None


def raw_apk_names() -> dict[str, str]:
    return {abi: f"app-{abi}-release.apk" for abi in ABI_ORDER}


def released_apk_pattern(project_name: str) -> re.Pattern[str]:
    abi_pattern = "|".join(re.escape(abi) for abi in ABI_ORDER)
    return re.compile(
        rf"^{re.escape(project_name)}-v(?P<version>.+?)-(?P<abi>{abi_pattern})-"
        rf"(?P<crc>[0-9a-fA-F]{{8}})\.apk$",
    )


def crc32(path: Path) -> str:
    value = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value = zlib.crc32(block, value)
    return f"{value & 0xFFFFFFFF:08x}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def discover_apks(input_dir: Path, context: ReleaseContext) -> tuple[dict[str, Path], list[Path]]:
    input_dir = input_dir.resolve()
    require(input_dir.is_dir(), f"Release APK directory is missing: {input_dir}")
    apk_files = sorted(path for path in input_dir.glob("*.apk") if path.is_file())
    require(bool(apk_files), f"No APK files found in {input_dir}")

    raw_names = raw_apk_names()
    raw_name_set = set(raw_names.values())
    actual_names = {path.name for path in apk_files}
    raw_candidates = actual_names & raw_name_set
    if raw_candidates:
        require(
            actual_names == raw_name_set,
            f"Raw release APK inventory mismatch: missing={sorted(raw_name_set - actual_names)}, "
            f"unexpected={sorted(actual_names - raw_name_set)}",
        )
        return {abi: input_dir / filename for abi, filename in raw_names.items()}, []

    pattern = released_apk_pattern(context.project_name)
    candidates: dict[str, list[Path]] = defaultdict(list)
    foreign_versions: list[Path] = []
    malformed_current: list[str] = []
    current_prefix = f"{context.project_name}-v{context.version_name}-"
    for path in apk_files:
        match = pattern.match(path.name)
        if match is None:
            if path.name.startswith(current_prefix):
                malformed_current.append(path.name)
            else:
                foreign_versions.append(path)
            continue
        if match.group("version") != context.version_name:
            foreign_versions.append(path)
            continue
        candidates[match.group("abi")].append(path)

    require(not malformed_current, f"Malformed current-version APK names: {sorted(malformed_current)}")
    missing = [abi for abi in ABI_ORDER if not candidates[abi]]
    duplicates = {abi: [path.name for path in paths] for abi, paths in candidates.items() if len(paths) > 1}
    require(not missing, f"Missing current-version APKs for ABIs: {missing}")
    require(not duplicates, f"Duplicate current-version APKs detected: {duplicates}")
    return {abi: candidates[abi][0] for abi in ABI_ORDER}, foreign_versions


def expected_native_abis(abi: str) -> set[str]:
    return NATIVE_ABIS if abi == "universal" else {abi}


def validate_apk(path: Path, abi: str, context: ReleaseContext) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            corrupt_entry = archive.testzip()
            require(corrupt_entry is None, f"Corrupt ZIP entry in {path.name}: {corrupt_entry}")
            names = archive.namelist()
            require("AndroidManifest.xml" in names, f"AndroidManifest.xml is missing from {path.name}")
            native_abis = {
                name.split("/", 2)[1]
                for name in names
                if name.startswith("lib/") and name.count("/") >= 2 and name.endswith(".so")
            }
    except zipfile.BadZipFile:
        raise ReleaseError(f"Not a valid APK ZIP archive: {path}") from None

    expected = expected_native_abis(abi)
    require(
        native_abis == expected,
        f"Unexpected native ABI set in {path.name}: expected={sorted(expected)}, actual={sorted(native_abis)}",
    )

    match = released_apk_pattern(context.project_name).match(path.name)
    if match is not None:
        expected_crc = match.group("crc").lower()
        actual_crc = crc32(path)
        require(
            actual_crc == expected_crc,
            f"CRC32 filename mismatch for {path.name}: expected={expected_crc}, actual={actual_crc}",
        )


def collect_records(input_dir: Path, context: ReleaseContext) -> tuple[list[PackageRecord], list[Path]]:
    discovered, foreign_versions = discover_apks(input_dir, context)
    records: list[PackageRecord] = []
    for abi in ABI_ORDER:
        source = discovered[abi]
        validate_apk(source, abi, context)
        package_crc = crc32(source)
        filename = f"{context.project_name}-v{context.version_name}-{abi}-{package_crc}.apk"
        records.append(
            PackageRecord(
                abi=abi,
                source=source,
                filename=filename,
                crc32=package_crc,
                sha256=sha256(source),
                size=source.stat().st_size,
            ),
        )
    return records, foreign_versions


def version_sort_key(path: Path) -> tuple[int, ...]:
    parts = re.findall(r"\d+", path.parent.name)
    return tuple(int(part) for part in parts)


def find_apksigner(explicit: Path | None = None) -> Path:
    if explicit is not None:
        candidate = explicit.expanduser().resolve()
        require(candidate.is_file(), f"apksigner does not exist: {candidate}")
        return candidate

    command = shutil.which("apksigner") or shutil.which("apksigner.bat")
    if command:
        return Path(command).resolve()

    executable = "apksigner.bat" if os.name == "nt" else "apksigner"
    candidates: list[Path] = []
    for variable in ("ANDROID_SDK_ROOT", "ANDROID_HOME"):
        value = os.environ.get(variable)
        if not value:
            continue
        build_tools = Path(value).expanduser() / "build-tools"
        if build_tools.is_dir():
            candidates.extend(path for path in build_tools.glob(f"*/{executable}") if path.is_file())
    require(bool(candidates), "Cannot locate apksigner; set ANDROID_SDK_ROOT or ANDROID_HOME")
    return max(candidates, key=version_sort_key).resolve()


def apksigner_command(apksigner: Path, apk: Path) -> list[str]:
    arguments = [str(apksigner), "verify", "--verbose", "--print-certs", str(apk)]
    if os.name == "nt" and apksigner.suffix.lower() in (".bat", ".cmd"):
        return ["cmd.exe", "/d", "/c", *arguments]
    return arguments


def signer_digest_from_output(output: str) -> str:
    pattern = re.compile(
        r"(?:Signer #\d+|V\d+(?:\.\d+)? Signer):? certificate SHA-256 digest:\s*([0-9a-fA-F]+)",
    )
    match = pattern.search(output)
    require(match is not None, "Cannot read signer certificate digest from apksigner output")
    return match.group(1).upper()


def verify_signatures(records: list[PackageRecord], apksigner: Path) -> str:
    certificate_digests: dict[str, str] = {}
    for record in records:
        result = subprocess.run(
            apksigner_command(apksigner, record.source),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = f"{result.stdout}\n{result.stderr}"
        require(result.returncode == 0, f"Signature verification failed for {record.source.name}: {output.strip()}")
        try:
            certificate_digests[record.abi] = signer_digest_from_output(output)
        except ReleaseError:
            raise ReleaseError(f"Cannot read signer certificate digest from {record.source.name}") from None
    unique_digests = set(certificate_digests.values())
    require(
        len(unique_digests) == 1,
        f"APK signer certificate mismatch across ABI variants: {certificate_digests}",
    )
    return next(iter(unique_digests))


def render_release_notes(
    context: ReleaseContext,
    records: list[PackageRecord],
    signer_digest: str | None,
) -> str:
    date = str(context.release_entry.get("released_date", "")).replace("/", "-")
    lines = [
        f"# {context.project_name} v{context.version_name}",
        "",
        f"Release date: {date}",
        "",
        "Generated from the English changelog source at `.changelog/lang_en.json`.",
    ]
    for category in CATEGORY_ORDER:
        entries = context.release_entry.get(category, [])
        if not entries:
            continue
        label = context.changelog.get(f"changelog_label_{category}", category.title())
        lines.extend(("", f"## {label}", ""))
        lines.extend(f"- {entry}" for entry in entries)

    lines.extend(("", "## Packages", "", "| ABI | File | Size (bytes) | SHA-256 |", "|---|---|---:|---|"))
    for record in records:
        lines.append(f"| `{record.abi}` | `{record.filename}` | {record.size} | `{record.sha256}` |")

    lines.extend(("", "## Verification", "", "- Verify all package hashes with `SHA256SUMS.txt`."))
    if signer_digest is not None:
        lines.append(f"- Signer certificate SHA-256: `{signer_digest}`")
    return "\n".join(lines).rstrip() + "\n"


def output_is_safe_to_replace(output_dir: Path, context: ReleaseContext) -> bool:
    release_root = (context.root / "build" / "release").resolve()
    try:
        output_dir.resolve().relative_to(release_root)
    except ValueError:
        return False
    return output_dir.resolve() != release_root


def create_bundle(
    context: ReleaseContext,
    records: list[PackageRecord],
    output_dir: Path,
    signer_digest: str | None,
    overwrite: bool = False,
) -> Path:
    output_dir = output_dir.resolve()
    require(not output_dir.exists() or overwrite, f"Output directory already exists: {output_dir}")
    if output_dir.exists():
        require(
            output_is_safe_to_replace(output_dir, context),
            f"Refusing to replace output outside the project build/release directory: {output_dir}",
        )

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}-", dir=output_dir.parent))
    try:
        for record in records:
            destination = stage / record.filename
            shutil.copy2(record.source, destination)
            require(sha256(destination) == record.sha256, f"SHA-256 changed while copying {record.filename}")

        checksum_lines = [f"{record.sha256}  {record.filename}" for record in records]
        (stage / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8", newline="\n")
        (stage / "RELEASE_NOTES.md").write_text(
            render_release_notes(context, records, signer_digest),
            encoding="utf-8",
            newline="\n",
        )

        if output_dir.exists():
            shutil.rmtree(output_dir)
        stage.replace(output_dir)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    return output_dir


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="APK source directory; defaults to Gradle release outputs")
    parser.add_argument("--output", type=Path, help="bundle directory; defaults to build/release/v<version>")
    parser.add_argument("--skip-build", action="store_true", help="use existing APKs without running assembleRelease")
    parser.add_argument("--apksigner", type=Path, help="explicit path to apksigner or apksigner.bat")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing bundle under build/release")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    root = Path(__file__).resolve().parents[2]
    try:
        context = load_release_context(root)
        if not arguments.skip_build:
            run_release_build(context)

        input_dir = (arguments.input or root / "app" / "build" / "outputs" / "apk" / "release").resolve()
        output_dir = (arguments.output or root / "build" / "release" / f"v{context.version_name}").resolve()
        records, foreign_versions = collect_records(input_dir, context)
        for path in foreign_versions:
            print(f"Ignoring foreign-version APK: {path.name}")

        signer = find_apksigner(arguments.apksigner)
        signer_digest = verify_signatures(records, signer)
        print(f"SIGNER_OK sha256={signer_digest}")

        bundle = create_bundle(context, records, output_dir, signer_digest, arguments.overwrite)
        for record in records:
            print(
                f"PACKAGE_OK abi={record.abi} file={record.filename} "
                f"bytes={record.size} sha256={record.sha256}",
            )
        print(f"RELEASE_OK version={context.version_name} packages={len(records)} output={bundle}")
        return 0
    except (ReleaseError, OSError) as error:
        print(f"RELEASE_ERROR {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
