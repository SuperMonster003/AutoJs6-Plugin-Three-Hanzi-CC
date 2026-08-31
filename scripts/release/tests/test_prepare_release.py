from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.release.prepare_release import (
    ABI_ORDER,
    ReleaseError,
    collect_records,
    crc32,
    create_bundle,
    load_release_context,
    sha256,
    signer_digest_from_output,
)


class PrepareReleaseTest(unittest.TestCase):

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / ".changelog").mkdir()
        (self.root / "settings.gradle.kts").write_text(
            'rootProject.name = "autojs6-plugin-opencc"\n',
            encoding="utf-8",
        )
        (self.root / "version.properties").write_text("VERSION_NAME=1.2.3\n", encoding="utf-8")
        changelog = {
            "changelog_label_hint": "Hint",
            "changelog_label_feature": "Feature",
            "changelog_label_fix": "Fix",
            "changelog_label_improvement": "Improvement",
            "changelog_label_dependency": "Dependency",
            "$data": {
                "v1.2.3": {
                    "released_date": "2026/08/31",
                    "improvement": ["Verified release tooling."],
                },
            },
        }
        (self.root / ".changelog" / "lang_en.json").write_text(
            json.dumps(changelog),
            encoding="utf-8",
        )
        self.input_dir = self.root / "input"
        self.input_dir.mkdir()
        self.context = load_release_context(self.root)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def create_fake_apk(self, path: Path, abis: set[str], marker: str = "fixture") -> None:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("AndroidManifest.xml", f"manifest-{marker}")
            archive.writestr("classes.dex", f"dex-{marker}")
            for abi in sorted(abis):
                archive.writestr(f"lib/{abi}/libChineseConverter.so", f"native-{abi}-{marker}")

    def create_raw_set(self) -> None:
        for abi in ABI_ORDER:
            native_abis = {"arm64-v8a", "armeabi-v7a", "x86_64", "x86"} if abi == "universal" else {abi}
            self.create_fake_apk(self.input_dir / f"app-{abi}-release.apk", native_abis, abi)

    def create_released_set(self) -> None:
        for abi in ABI_ORDER:
            native_abis = {"arm64-v8a", "armeabi-v7a", "x86_64", "x86"} if abi == "universal" else {abi}
            temporary = self.input_dir / f"{abi}.tmp"
            self.create_fake_apk(temporary, native_abis, abi)
            final = self.input_dir / f"autojs6-plugin-opencc-v1.2.3-{abi}-{crc32(temporary)}.apk"
            temporary.rename(final)

    def test_complete_set_generates_exact_bundle_checksums_and_notes(self) -> None:
        self.create_raw_set()
        records, foreign = collect_records(self.input_dir, self.context)
        self.assertEqual([], foreign)
        self.assertEqual(list(ABI_ORDER), [record.abi for record in records])

        output = create_bundle(
            self.context,
            records,
            self.root / "build" / "release" / "v1.2.3",
            signer_digest="A" * 64,
        )
        self.assertEqual(
            {record.filename for record in records} | {"SHA256SUMS.txt", "RELEASE_NOTES.md"},
            {path.name for path in output.iterdir()},
        )
        checksum_lines = (output / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            [f"{sha256(output / record.filename)}  {record.filename}" for record in records],
            checksum_lines,
        )
        notes = (output / "RELEASE_NOTES.md").read_text(encoding="utf-8")
        self.assertIn("Verified release tooling.", notes)
        self.assertIn("Signer certificate SHA-256", notes)
        self.assertIn("`arm64-v8a`", notes)
        self.assertIn("`universal`", notes)

    def test_missing_raw_abi_is_rejected(self) -> None:
        self.create_raw_set()
        (self.input_dir / "app-x86-release.apk").unlink()
        with self.assertRaisesRegex(ReleaseError, "inventory mismatch"):
            collect_records(self.input_dir, self.context)

    def test_duplicate_current_version_abi_is_rejected(self) -> None:
        self.create_released_set()
        duplicate = self.input_dir / "duplicate.tmp"
        self.create_fake_apk(duplicate, {"arm64-v8a"}, "duplicate")
        duplicate.rename(
            self.input_dir / f"autojs6-plugin-opencc-v1.2.3-arm64-v8a-{crc32(duplicate)}.apk",
        )
        with self.assertRaisesRegex(ReleaseError, "Duplicate current-version APKs"):
            collect_records(self.input_dir, self.context)

    def test_wrong_native_abi_is_rejected(self) -> None:
        self.create_raw_set()
        wrong = self.input_dir / "app-arm64-v8a-release.apk"
        wrong.unlink()
        self.create_fake_apk(wrong, {"x86_64"}, "wrong-abi")
        with self.assertRaisesRegex(ReleaseError, "Unexpected native ABI set"):
            collect_records(self.input_dir, self.context)

    def test_crc_filename_mismatch_is_rejected(self) -> None:
        self.create_released_set()
        arm64 = next(self.input_dir.glob("*-arm64-v8a-*.apk"))
        with arm64.open("ab") as stream:
            stream.write(b"changed-after-naming")
        with self.assertRaisesRegex(ReleaseError, "CRC32 filename mismatch"):
            collect_records(self.input_dir, self.context)

    def test_other_versions_are_excluded_from_current_bundle(self) -> None:
        self.create_released_set()
        foreign = self.input_dir / "foreign.tmp"
        self.create_fake_apk(foreign, {"x86_64"}, "old-version")
        foreign_name = self.input_dir / f"autojs6-plugin-opencc-v1.2.2-x86_64-{crc32(foreign)}.apk"
        foreign.rename(foreign_name)

        records, foreign_versions = collect_records(self.input_dir, self.context)
        self.assertEqual(list(ABI_ORDER), [record.abi for record in records])
        self.assertEqual([foreign_name], foreign_versions)

    def test_apksigner_digest_parser_supports_legacy_and_scheme_labels(self) -> None:
        digest = "31a681fcfffb3e428420cae280ded89292b12a3b0f59e19b7a73e32a8ae4c213"
        self.assertEqual(
            digest.upper(),
            signer_digest_from_output(f"Signer #1 certificate SHA-256 digest: {digest}"),
        )
        self.assertEqual(
            digest.upper(),
            signer_digest_from_output(f"V2 Signer: certificate SHA-256 digest: {digest}"),
        )


if __name__ == "__main__":
    unittest.main()
