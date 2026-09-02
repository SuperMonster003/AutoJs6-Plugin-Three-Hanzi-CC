#!/usr/bin/env python3
"""Verify that an Android split build produced the exact expected APK set."""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
import zipfile
from pathlib import Path


EXPECTED_VARIANTS = {
    "arm64-v8a": {"arm64-v8a"},
    "armeabi-v7a": {"armeabi-v7a"},
    "x86_64": {"x86_64"},
    "x86": {"x86"},
    "universal": {"arm64-v8a", "armeabi-v7a", "x86_64", "x86"},
}

EXPECTED_NATIVE_LIBRARY = "libopencc_jni.so"
FORBIDDEN_NATIVE_LIBRARIES = {
    "libChineseConverter.so",
    "libopencc.so",
    "libc++_shared.so",
}
FORBIDDEN_DEX_MARKERS = {
    b"Lcom/zqc/opencc/android/lib/": "legacy android-opencc classes",
    b"com/zqc/opencc/android/lib/ChineseConverter": "legacy ChineseConverter JNI reference",
}
REQUIRED_DEX_MARKERS = {
    b"Lio/github/supermonster003/autojs6/plugin/opencc/OpenccActivity;": (
        "standalone OpenccActivity class descriptor"
    ),
    b"Lio/github/supermonster003/autojs6/plugin/opencc/nativebridge/OpenccNativeEngine;": (
        "OpenccNativeEngine class descriptor"
    ),
    b"nativeConvert": "OpenccNativeEngine.nativeConvert JNI method",
    b"nativeClearCache": "OpenccNativeEngine.nativeClearCache JNI method",
}
PT_LOAD = 1
PT_GNU_RELRO = 0x6474E552
MINIMUM_ELF_ALIGNMENT = 16 * 1024
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class VerificationError(Exception):
    pass


def load_upstream_lock() -> dict[str, str]:
    path = REPOSITORY_ROOT / "opencc-upstream.properties"
    properties: dict[str, str] = {}
    for source_line in path.read_text(encoding="utf-8").splitlines():
        line = source_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        name, value = line.split("=", 1)
        properties[name.strip()] = value.strip()
    return properties


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack_from(byte_order: str, format_code: str, data: bytes, offset: int) -> tuple[int, ...]:
    try:
        return struct.unpack_from(byte_order + format_code, data, offset)
    except struct.error as error:
        raise VerificationError(f"Truncated ELF structure at offset {offset}: {error}") from None


def verify_elf(data: bytes, label: str) -> int:
    if len(data) < 64 or data[:4] != b"\x7fELF":
        raise VerificationError(f"Not a valid ELF shared library: {label}")

    elf_class = data[4]
    byte_order_marker = data[5]
    if byte_order_marker == 1:
        byte_order = "<"
    elif byte_order_marker == 2:
        byte_order = ">"
    else:
        raise VerificationError(f"Unsupported ELF byte order in {label}: {byte_order_marker}")

    if elf_class == 1:
        program_header_offset = unpack_from(byte_order, "I", data, 28)[0]
        program_header_entry_size = unpack_from(byte_order, "H", data, 42)[0]
        program_header_count = unpack_from(byte_order, "H", data, 44)[0]
        minimum_entry_size = 32

        def program_header(index: int) -> tuple[int, int, int]:
            offset = program_header_offset + index * program_header_entry_size
            program_type = unpack_from(byte_order, "I", data, offset)[0]
            file_offset = unpack_from(byte_order, "I", data, offset + 4)[0]
            virtual_address = unpack_from(byte_order, "I", data, offset + 8)[0]
            alignment = unpack_from(byte_order, "I", data, offset + 28)[0]
            return program_type, file_offset - virtual_address, alignment

    elif elf_class == 2:
        program_header_offset = unpack_from(byte_order, "Q", data, 32)[0]
        program_header_entry_size = unpack_from(byte_order, "H", data, 54)[0]
        program_header_count = unpack_from(byte_order, "H", data, 56)[0]
        minimum_entry_size = 56

        def program_header(index: int) -> tuple[int, int, int]:
            offset = program_header_offset + index * program_header_entry_size
            program_type = unpack_from(byte_order, "I", data, offset)[0]
            file_offset = unpack_from(byte_order, "Q", data, offset + 8)[0]
            virtual_address = unpack_from(byte_order, "Q", data, offset + 16)[0]
            alignment = unpack_from(byte_order, "Q", data, offset + 48)[0]
            return program_type, file_offset - virtual_address, alignment

    else:
        raise VerificationError(f"Unsupported ELF class in {label}: {elf_class}")

    if program_header_entry_size < minimum_entry_size:
        raise VerificationError(
            f"Invalid ELF program header size in {label}: {program_header_entry_size}",
        )
    if program_header_offset + program_header_entry_size * program_header_count > len(data):
        raise VerificationError(f"ELF program headers exceed file bounds in {label}")

    load_alignments: list[int] = []
    has_relro = False
    for index in range(program_header_count):
        program_type, offset_delta, alignment = program_header(index)
        if program_type == PT_LOAD:
            if alignment < MINIMUM_ELF_ALIGNMENT:
                raise VerificationError(
                    f"ELF LOAD alignment is below 16 KB in {label}: 0x{alignment:x}",
                )
            if offset_delta % alignment != 0:
                raise VerificationError(
                    f"ELF LOAD offset/vaddr congruence is invalid in {label}: "
                    f"delta={offset_delta}, align=0x{alignment:x}",
                )
            load_alignments.append(alignment)
        elif program_type == PT_GNU_RELRO:
            has_relro = True

    if not load_alignments:
        raise VerificationError(f"ELF contains no LOAD segments: {label}")
    if not has_relro:
        raise VerificationError(f"ELF is missing GNU_RELRO: {label}")
    return min(load_alignments)


def verify_apk(path: Path, expected_abis: set[str], upstream: dict[str, str]) -> tuple[set[str], int]:
    try:
        with zipfile.ZipFile(path) as archive:
            corrupt_entry = archive.testzip()
            if corrupt_entry is not None:
                raise VerificationError(f"Corrupt ZIP entry in {path}: {corrupt_entry}")

            native_infos = {
                info.filename: info
                for info in archive.infolist()
                if info.filename.startswith("lib/") and info.filename.endswith(".so")
            }
            expected_entries = {
                f"lib/{abi}/{EXPECTED_NATIVE_LIBRARY}"
                for abi in expected_abis
            }
            if set(native_infos) != expected_entries:
                raise VerificationError(
                    f"Unexpected native library inventory in {path.name}: "
                    f"missing={sorted(expected_entries - set(native_infos))}, "
                    f"unexpected={sorted(set(native_infos) - expected_entries)}",
                )
            forbidden = sorted(
                name
                for name in native_infos
                if pure_path_name(name) in FORBIDDEN_NATIVE_LIBRARIES
            )
            if forbidden:
                raise VerificationError(f"Forbidden legacy native libraries in {path.name}: {forbidden}")

            minimum_alignment = 1 << 63
            for name, info in native_infos.items():
                if info.compress_type != zipfile.ZIP_STORED:
                    raise VerificationError(f"Native library is compressed in {path.name}: {name}")
                minimum_alignment = min(minimum_alignment, verify_elf(archive.read(name), f"{path.name}!/{name}"))

            resource_entry = f"assets/opencc/{upstream['OPENCC_RESOURCE_ASSET']}"
            names = set(archive.namelist())
            if resource_entry not in names:
                raise VerificationError(f"Pinned OpenCC resource is missing from {path.name}: {resource_entry}")
            legacy_resources = sorted(
                name for name in names if name.startswith("assets/openccdata/")
            )
            if legacy_resources:
                raise VerificationError(
                    f"Legacy android-opencc resources remain in {path.name}: {legacy_resources[:5]}",
                )
            dex_entries = sorted(
                name for name in names if name.startswith("classes") and name.endswith(".dex")
            )
            if not dex_entries:
                raise VerificationError(f"APK contains no DEX files: {path.name}")
            dex_payloads = {dex_entry: archive.read(dex_entry) for dex_entry in dex_entries}
            dex_payload = b"".join(dex_payloads.values())
            for dex_entry, dex_data in dex_payloads.items():
                for marker, description in FORBIDDEN_DEX_MARKERS.items():
                    if marker in dex_data:
                        raise VerificationError(
                            f"{description} remain in {path.name}!/{dex_entry}",
                        )
            for marker, description in REQUIRED_DEX_MARKERS.items():
                if marker not in dex_payload:
                    raise VerificationError(f"R8/DEX output is missing {description} in {path.name}")
            resource_data = archive.read(resource_entry)
            if len(resource_data) != int(upstream["OPENCC_RESOURCE_SIZE"]):
                raise VerificationError(
                    f"OpenCC resource size mismatch in {path.name}: "
                    f"expected={upstream['OPENCC_RESOURCE_SIZE']}, actual={len(resource_data)}",
                )
            digest = sha256(resource_data)
            if digest != upstream["OPENCC_RESOURCE_SHA256"]:
                raise VerificationError(
                    f"OpenCC resource SHA-256 mismatch in {path.name}: "
                    f"expected={upstream['OPENCC_RESOURCE_SHA256']}, actual={digest}",
                )

            actual_abis = {name.split("/", 2)[1] for name in native_infos}
            return actual_abis, minimum_alignment
    except zipfile.BadZipFile:
        raise VerificationError(f"Not a valid APK ZIP archive: {path}") from None


def pure_path_name(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def expected_apks(build_type: str, unsigned: bool = False) -> dict[str, set[str]]:
    if unsigned and build_type != "release":
        raise VerificationError("Unsigned APK naming is supported only for release builds")
    suffix = f"{build_type}-unsigned" if unsigned else build_type
    return {
        f"app-{variant}-{suffix}.apk": abis
        for variant, abis in EXPECTED_VARIANTS.items()
    }


def verify_instrumentation_apk(path: Path) -> None:
    if not path.is_file():
        raise VerificationError(f"Instrumentation APK is missing: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            corrupt_entry = archive.testzip()
            if corrupt_entry is not None:
                raise VerificationError(
                    f"Corrupt ZIP entry in instrumentation APK {path.name}: {corrupt_entry}",
                )

            names = set(archive.namelist())
            native_entries = sorted(
                name for name in names if name.startswith("lib/") and name.endswith(".so")
            )
            if native_entries:
                raise VerificationError(
                    f"Instrumentation APK must not package native libraries: {native_entries}",
                )
            legacy_resources = sorted(name for name in names if name.startswith("assets/openccdata/"))
            if legacy_resources:
                raise VerificationError(
                    "Legacy android-opencc resources remain in instrumentation APK: "
                    f"{legacy_resources[:5]}",
                )

            dex_entries = sorted(
                name for name in names if name.startswith("classes") and name.endswith(".dex")
            )
            if not dex_entries:
                raise VerificationError(f"Instrumentation APK contains no DEX files: {path.name}")
            for dex_entry in dex_entries:
                dex_data = archive.read(dex_entry)
                for marker, description in FORBIDDEN_DEX_MARKERS.items():
                    if marker in dex_data:
                        raise VerificationError(
                            f"{description} remain in instrumentation APK {path.name}!/{dex_entry}",
                        )
    except zipfile.BadZipFile:
        raise VerificationError(f"Not a valid instrumentation APK ZIP archive: {path}") from None

    print(
        f"INSTRUMENTATION_APK_OK {path.name} "
        "legacy_classes=0 native_libraries=0 legacy_resources=0",
    )


def verify(directory: Path, build_type: str = "debug", unsigned: bool = False) -> None:
    if not directory.is_dir():
        raise VerificationError(f"APK output directory is missing: {directory}")

    expected_variants = expected_apks(build_type, unsigned)
    actual = {path.name for path in directory.glob("*.apk") if path.is_file()}
    expected = set(expected_variants)
    if actual != expected:
        release_kind = "unsigned release" if unsigned else build_type
        raise VerificationError(
            f"Unexpected {release_kind} APK inventory: missing={sorted(expected - actual)}, "
            f"unexpected={sorted(actual - expected)}",
        )

    upstream = load_upstream_lock()
    for filename, expected_abis in expected_variants.items():
        path = directory / filename
        actual_abis, minimum_alignment = verify_apk(path, expected_abis, upstream)
        if actual_abis != expected_abis:
            raise VerificationError(
                f"Unexpected native ABI set in {filename}: "
                f"expected={sorted(expected_abis)}, actual={sorted(actual_abis)}",
            )
        print(
            f"APK_OK {filename} abis={','.join(sorted(actual_abis))} "
            f"native={EXPECTED_NATIVE_LIBRARY} min_elf_align=0x{minimum_alignment:x} "
            f"opencc={upstream['OPENCC_VERSION']} bytes={path.stat().st_size}",
        )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="directory containing APK outputs")
    parser.add_argument(
        "--build-type",
        choices=("debug", "release"),
        default="debug",
        help="APK build type (default: debug)",
    )
    parser.add_argument(
        "--instrumentation-apk",
        type=Path,
        help="optional instrumentation APK that must contain no native or retired legacy backend payload",
    )
    parser.add_argument(
        "--unsigned",
        action="store_true",
        help="expect Gradle's *-release-unsigned.apk filenames (valid only with --build-type release)",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        verify(arguments.directory.resolve(), arguments.build_type, arguments.unsigned)
        if arguments.instrumentation_apk is not None:
            verify_instrumentation_apk(arguments.instrumentation_apk.resolve())
    except VerificationError as error:
        print(f"APK_ERROR {error}", file=sys.stderr)
        return 1
    print(f"APK_OK variants={len(EXPECTED_VARIANTS)} build_type={arguments.build_type}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
