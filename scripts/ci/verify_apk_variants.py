#!/usr/bin/env python3
"""Verify that an Android split build produced the exact expected APK set."""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
import zipfile
from dataclasses import dataclass, field
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
APPLICATION_ID = "io.github.supermonster003.autojs6.plugin.opencc"
PLUGIN_PERMISSION = "org.autojs.permission.PLUGIN"
OPENCC_API_SHA256 = "5f3001e28fb4c4967b0a4faeb4547a41a679b35cbd209d272a6a79f7ba00ab45"
NO_STRING_INDEX = 0xFFFFFFFF
RES_XML_TYPE = 0x0003
RES_STRING_POOL_TYPE = 0x0001
RES_XML_START_ELEMENT_TYPE = 0x0102
RES_XML_END_ELEMENT_TYPE = 0x0103
UTF8_FLAG = 0x00000100
TYPE_STRING = 0x03
TYPE_INT_BOOLEAN = 0x12


class VerificationError(Exception):
    pass


@dataclass
class ManifestElement:
    name: str
    attributes: dict[str, object]
    children: list["ManifestElement"] = field(default_factory=list)


def verify_api_artifact() -> None:
    path = REPOSITORY_ROOT / "libs" / "opencc-api.aar"
    if not path.is_file():
        raise VerificationError(f"Pinned opencc-api artifact is missing: {path}")
    digest = sha256(path.read_bytes())
    if digest != OPENCC_API_SHA256:
        raise VerificationError(
            "opencc-api artifact changed without a reviewed compatibility snapshot: "
            f"expected={OPENCC_API_SHA256}, actual={digest}",
        )


def _chunk_header(data: bytes, offset: int, label: str) -> tuple[int, int, int]:
    if offset < 0 or offset + 8 > len(data):
        raise VerificationError(f"Truncated {label} chunk header at offset {offset}")
    chunk_type, header_size, chunk_size = struct.unpack_from("<HHI", data, offset)
    if header_size < 8 or chunk_size < header_size or offset + chunk_size > len(data):
        raise VerificationError(
            f"Invalid {label} chunk bounds at offset {offset}: "
            f"header={header_size}, size={chunk_size}, data={len(data)}",
        )
    return chunk_type, header_size, chunk_size


def _length8(data: bytes, offset: int, limit: int) -> tuple[int, int]:
    if offset >= limit:
        raise VerificationError("Truncated UTF-8 string length in AndroidManifest.xml")
    first = data[offset]
    if first & 0x80:
        if offset + 1 >= limit:
            raise VerificationError("Truncated two-byte UTF-8 string length in AndroidManifest.xml")
        return ((first & 0x7F) << 8) | data[offset + 1], offset + 2
    return first, offset + 1


def _length16(data: bytes, offset: int, limit: int) -> tuple[int, int]:
    if offset + 2 > limit:
        raise VerificationError("Truncated UTF-16 string length in AndroidManifest.xml")
    first = struct.unpack_from("<H", data, offset)[0]
    if first & 0x8000:
        if offset + 4 > limit:
            raise VerificationError("Truncated four-byte UTF-16 string length in AndroidManifest.xml")
        second = struct.unpack_from("<H", data, offset + 2)[0]
        return ((first & 0x7FFF) << 16) | second, offset + 4
    return first, offset + 2


def _parse_string_pool(data: bytes, offset: int, header_size: int, chunk_size: int) -> list[str]:
    if header_size < 28:
        raise VerificationError("AndroidManifest.xml string-pool header is too short")
    string_count, style_count, flags, strings_start, styles_start = struct.unpack_from(
        "<IIIII",
        data,
        offset + 8,
    )
    offsets_end = offset + header_size + (string_count + style_count) * 4
    if offsets_end > offset + chunk_size:
        raise VerificationError("AndroidManifest.xml string-pool offsets exceed chunk bounds")
    strings_base = offset + strings_start
    strings_limit = offset + (styles_start if styles_start else chunk_size)
    if strings_base < offset + header_size or strings_base > strings_limit:
        raise VerificationError("AndroidManifest.xml string-pool data offset is invalid")

    values: list[str] = []
    for index in range(string_count):
        relative = struct.unpack_from("<I", data, offset + header_size + index * 4)[0]
        position = strings_base + relative
        if position < strings_base or position >= strings_limit:
            raise VerificationError(f"AndroidManifest.xml string {index} is outside the string pool")
        if flags & UTF8_FLAG:
            _, position = _length8(data, position, strings_limit)
            byte_length, position = _length8(data, position, strings_limit)
            end = position + byte_length
            if end >= strings_limit:
                raise VerificationError(f"AndroidManifest.xml UTF-8 string {index} is truncated")
            try:
                value = data[position:end].decode("utf-8")
            except UnicodeDecodeError as error:
                raise VerificationError(
                    f"AndroidManifest.xml UTF-8 string {index} is invalid: {error}",
                ) from None
        else:
            code_unit_length, position = _length16(data, position, strings_limit)
            end = position + code_unit_length * 2
            if end + 2 > strings_limit:
                raise VerificationError(f"AndroidManifest.xml UTF-16 string {index} is truncated")
            try:
                value = data[position:end].decode("utf-16-le")
            except UnicodeDecodeError as error:
                raise VerificationError(
                    f"AndroidManifest.xml UTF-16 string {index} is invalid: {error}",
                ) from None
        values.append(value)
    return values


def _pool_string(strings: list[str], index: int, description: str) -> str:
    if index == NO_STRING_INDEX or index >= len(strings):
        raise VerificationError(f"Invalid AndroidManifest.xml string index for {description}: {index}")
    return strings[index]


def _attribute_value(data: bytes, offset: int, strings: list[str]) -> object:
    raw_value = struct.unpack_from("<I", data, offset + 8)[0]
    if raw_value != NO_STRING_INDEX:
        return _pool_string(strings, raw_value, "raw attribute value")
    value_size = struct.unpack_from("<H", data, offset + 12)[0]
    if value_size < 8:
        raise VerificationError(f"Invalid AndroidManifest.xml typed value size: {value_size}")
    data_type = data[offset + 15]
    value = struct.unpack_from("<I", data, offset + 16)[0]
    if data_type == TYPE_STRING:
        return _pool_string(strings, value, "typed attribute value")
    if data_type == TYPE_INT_BOOLEAN:
        return value != 0
    return value


def parse_binary_manifest(data: bytes) -> ManifestElement:
    chunk_type, header_size, chunk_size = _chunk_header(data, 0, "AndroidManifest.xml")
    if chunk_type != RES_XML_TYPE:
        raise VerificationError(f"AndroidManifest.xml has unexpected root chunk type: 0x{chunk_type:04x}")
    if chunk_size != len(data):
        raise VerificationError(
            f"AndroidManifest.xml size mismatch: header={chunk_size}, actual={len(data)}",
        )

    strings: list[str] | None = None
    roots: list[ManifestElement] = []
    stack: list[ManifestElement] = []
    offset = header_size
    while offset < chunk_size:
        child_type, child_header_size, child_size = _chunk_header(data, offset, "AndroidManifest.xml child")
        if child_type == RES_STRING_POOL_TYPE:
            if strings is not None:
                raise VerificationError("AndroidManifest.xml contains multiple string pools")
            strings = _parse_string_pool(data, offset, child_header_size, child_size)
        elif child_type == RES_XML_START_ELEMENT_TYPE:
            if strings is None:
                raise VerificationError("AndroidManifest.xml element appears before its string pool")
            extension = offset + child_header_size
            if extension + 20 > offset + child_size:
                raise VerificationError("AndroidManifest.xml start element is truncated")
            name_index = struct.unpack_from("<I", data, extension + 4)[0]
            attribute_start, attribute_size, attribute_count = struct.unpack_from(
                "<HHH",
                data,
                extension + 8,
            )
            if attribute_size < 20:
                raise VerificationError(
                    f"AndroidManifest.xml attribute size is too small: {attribute_size}",
                )
            attributes_offset = extension + attribute_start
            if attributes_offset + attribute_size * attribute_count > offset + child_size:
                raise VerificationError("AndroidManifest.xml attributes exceed element bounds")
            attributes: dict[str, object] = {}
            for index in range(attribute_count):
                attribute_offset = attributes_offset + index * attribute_size
                name = _pool_string(
                    strings,
                    struct.unpack_from("<I", data, attribute_offset + 4)[0],
                    "attribute name",
                )
                if name in attributes:
                    raise VerificationError(f"Duplicate AndroidManifest.xml attribute: {name}")
                attributes[name] = _attribute_value(data, attribute_offset, strings)
            element = ManifestElement(
                _pool_string(strings, name_index, "element name"),
                attributes,
            )
            if stack:
                stack[-1].children.append(element)
            else:
                roots.append(element)
            stack.append(element)
        elif child_type == RES_XML_END_ELEMENT_TYPE:
            if strings is None or not stack:
                raise VerificationError("AndroidManifest.xml contains an unmatched end element")
            extension = offset + child_header_size
            if extension + 8 > offset + child_size:
                raise VerificationError("AndroidManifest.xml end element is truncated")
            name = _pool_string(
                strings,
                struct.unpack_from("<I", data, extension + 4)[0],
                "end-element name",
            )
            if stack[-1].name != name:
                raise VerificationError(
                    f"AndroidManifest.xml closes {name!r} while {stack[-1].name!r} is open",
                )
            stack.pop()
        offset += child_size

    if stack:
        raise VerificationError(f"AndroidManifest.xml leaves element open: {stack[-1].name}")
    if len(roots) != 1:
        raise VerificationError(f"AndroidManifest.xml must have exactly one root element, found {len(roots)}")
    return roots[0]


def _children(element: ManifestElement, name: str) -> list[ManifestElement]:
    return [child for child in element.children if child.name == name]


def _component_name(package_name: str, declared_name: object) -> str:
    if not isinstance(declared_name, str) or not declared_name:
        raise VerificationError(f"Manifest component has an invalid name: {declared_name!r}")
    if declared_name.startswith("."):
        return package_name + declared_name
    if "." not in declared_name:
        return f"{package_name}.{declared_name}"
    return declared_name


def _component_map(application: ManifestElement, element_name: str) -> dict[str, ManifestElement]:
    package_name = APPLICATION_ID
    components: dict[str, ManifestElement] = {}
    for element in _children(application, element_name):
        name = _component_name(package_name, element.attributes.get("name"))
        if name in components:
            raise VerificationError(f"Manifest declares duplicate {element_name}: {name}")
        components[name] = element
    return components


def _intent_filters(component: ManifestElement) -> list[tuple[frozenset[str], frozenset[str]]]:
    signatures: list[tuple[frozenset[str], frozenset[str]]] = []
    for intent_filter in _children(component, "intent-filter"):
        unexpected = sorted(
            child.name for child in intent_filter.children if child.name not in {"action", "category"}
        )
        if unexpected:
            raise VerificationError(
                f"Manifest intent-filter for {component.attributes.get('name')} contains data or "
                f"unexpected elements: {unexpected}",
            )
        actions = frozenset(
            str(action.attributes.get("name")) for action in _children(intent_filter, "action")
        )
        categories = frozenset(
            str(category.attributes.get("name")) for category in _children(intent_filter, "category")
        )
        signatures.append((actions, categories))
    return signatures


def _require_attributes(
    element: ManifestElement,
    description: str,
    expected: dict[str, object],
    absent: set[str] = frozenset(),
) -> None:
    for name, value in expected.items():
        actual = element.attributes.get(name)
        if actual != value:
            raise VerificationError(
                f"Manifest {description} attribute {name!r} mismatch: expected={value!r}, actual={actual!r}",
            )
    present = sorted(name for name in absent if name in element.attributes)
    if present:
        raise VerificationError(f"Manifest {description} unexpectedly declares attributes: {present}")


def verify_manifest_tree(root: ManifestElement, label: str) -> None:
    if root.name != "manifest":
        raise VerificationError(f"{label} manifest root is {root.name!r}, expected 'manifest'")
    package_name = root.attributes.get("package")
    if package_name != APPLICATION_ID:
        raise VerificationError(
            f"{label} applicationId mismatch: expected={APPLICATION_ID}, actual={package_name!r}",
        )

    permission_elements = [
        child for child in root.children if child.name.startswith("uses-permission")
    ]
    requested_permissions = {element.attributes.get("name") for element in permission_elements}
    if requested_permissions != {PLUGIN_PERMISSION}:
        raise VerificationError(
            f"{label} requested permissions mismatch: "
            f"expected={[PLUGIN_PERMISSION]}, actual={sorted(map(str, requested_permissions))}",
        )

    applications = _children(root, "application")
    if len(applications) != 1:
        raise VerificationError(f"{label} must declare exactly one application element")
    application = applications[0]
    _require_attributes(
        application,
        "application",
        {"allowBackup": False, "usesCleartextTraffic": False},
        {"permission", "process", "taskAffinity", "allowTaskReparenting"},
    )

    disallowed_components = {
        name: len(_children(application, name))
        for name in ("activity-alias", "receiver", "provider")
        if _children(application, name)
    }
    if disallowed_components:
        raise VerificationError(f"{label} contains unexpected exported-surface components: {disallowed_components}")

    activities = _component_map(application, "activity")
    expected_activity_names = {
        f"{APPLICATION_ID}.OpenccActivity",
        f"{APPLICATION_ID}.WakeActivity",
    }
    if set(activities) != expected_activity_names:
        raise VerificationError(
            f"{label} activity inventory mismatch: expected={sorted(expected_activity_names)}, "
            f"actual={sorted(activities)}",
        )

    launcher = activities[f"{APPLICATION_ID}.OpenccActivity"]
    _require_attributes(
        launcher,
        "OpenccActivity",
        {"exported": True},
        {
            "permission",
            "process",
            "taskAffinity",
            "allowTaskReparenting",
            "documentLaunchMode",
            "excludeFromRecents",
            "finishOnTaskLaunch",
            "launchMode",
            "noHistory",
        },
    )
    expected_launcher_filter = [
        (frozenset({"android.intent.action.MAIN"}), frozenset({"android.intent.category.LAUNCHER"})),
    ]
    if _intent_filters(launcher) != expected_launcher_filter:
        raise VerificationError(
            f"{label} OpenccActivity intent filters must contain only MAIN/LAUNCHER",
        )

    wake = activities[f"{APPLICATION_ID}.WakeActivity"]
    _require_attributes(
        wake,
        "WakeActivity",
        {
            "exported": True,
            "permission": PLUGIN_PERMISSION,
            "excludeFromRecents": True,
            "finishOnTaskLaunch": True,
        },
        {"process", "taskAffinity", "allowTaskReparenting", "documentLaunchMode", "noHistory"},
    )
    expected_wake_filter = [
        (
            frozenset({"org.autojs.plugin.action.WAKE"}),
            frozenset({"android.intent.category.DEFAULT"}),
        ),
    ]
    if _intent_filters(wake) != expected_wake_filter:
        raise VerificationError(f"{label} WakeActivity intent filters changed")

    services = _component_map(application, "service")
    expected_service_name = f"{APPLICATION_ID}.OpenccPluginService"
    if set(services) != {expected_service_name}:
        raise VerificationError(
            f"{label} service inventory mismatch: expected={[expected_service_name]}, actual={sorted(services)}",
        )
    service = services[expected_service_name]
    _require_attributes(
        service,
        "OpenccPluginService",
        {"exported": True, "permission": PLUGIN_PERMISSION},
        {"process", "isolatedProcess", "stopWithTask"},
    )
    expected_service_filter = [
        (frozenset({"org.autojs.plugin.OPENCC"}), frozenset({"opencc"})),
    ]
    if _intent_filters(service) != expected_service_filter:
        raise VerificationError(f"{label} OpenccPluginService intent filters changed")


def verify_manifest(data: bytes, label: str) -> None:
    verify_manifest_tree(parse_binary_manifest(data), label)


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

            manifest_entry = "AndroidManifest.xml"
            if manifest_entry not in names:
                raise VerificationError(f"APK manifest is missing from {path.name}")
            verify_manifest(archive.read(manifest_entry), path.name)

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

    verify_api_artifact()
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
