#!/usr/bin/env python3
"""Verify that an Android split build produced the exact expected APK set."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path


EXPECTED_APKS = {
    "app-arm64-v8a-debug.apk": {"arm64-v8a"},
    "app-armeabi-v7a-debug.apk": {"armeabi-v7a"},
    "app-x86_64-debug.apk": {"x86_64"},
    "app-x86-debug.apk": {"x86"},
    "app-universal-debug.apk": {"arm64-v8a", "armeabi-v7a", "x86_64", "x86"},
}


class VerificationError(Exception):
    pass


def native_abis(path: Path) -> set[str]:
    try:
        with zipfile.ZipFile(path) as archive:
            corrupt_entry = archive.testzip()
            if corrupt_entry is not None:
                raise VerificationError(f"Corrupt ZIP entry in {path}: {corrupt_entry}")
            return {
                name.split("/", 2)[1]
                for name in archive.namelist()
                if name.startswith("lib/") and name.count("/") >= 2 and name.endswith(".so")
            }
    except zipfile.BadZipFile:
        raise VerificationError(f"Not a valid APK ZIP archive: {path}") from None


def verify(directory: Path) -> None:
    if not directory.is_dir():
        raise VerificationError(f"APK output directory is missing: {directory}")

    actual = {path.name for path in directory.glob("*.apk") if path.is_file()}
    expected = set(EXPECTED_APKS)
    if actual != expected:
        raise VerificationError(
            f"Unexpected debug APK inventory: missing={sorted(expected - actual)}, "
            f"unexpected={sorted(actual - expected)}",
        )

    for filename, expected_abis in EXPECTED_APKS.items():
        path = directory / filename
        actual_abis = native_abis(path)
        if actual_abis != expected_abis:
            raise VerificationError(
                f"Unexpected native ABI set in {filename}: "
                f"expected={sorted(expected_abis)}, actual={sorted(actual_abis)}",
            )
        print(f"APK_OK {filename} abis={','.join(sorted(actual_abis))} bytes={path.stat().st_size}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="directory containing debug APK outputs")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        verify(arguments.directory.resolve())
    except VerificationError as error:
        print(f"APK_ERROR {error}", file=sys.stderr)
        return 1
    print(f"APK_OK variants={len(EXPECTED_APKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
