from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.release.prepare_candidate import (
    MAX_APK_GROWTH_BYTES,
    MAX_APK_GROWTH_PERCENT,
    CandidateBaseline,
    canonical_certificate_sha256,
    canonical_source_sha,
    finalize_candidate,
    load_candidate_baseline,
    maximum_candidate_size,
    verify_no_signing_material,
    verify_package_sizes,
    verify_git_source,
    verify_version_progression,
)
from scripts.release.prepare_release import (
    ABI_ORDER,
    ReleaseError,
    collect_records,
    create_bundle,
    load_release_context,
)


SOURCE_SHA = "1" * 40
BASELINE_SHA = "2" * 40
SIGNER_SHA256 = "A" * 64
PUBLISHED_SIGNER_SHA256 = (
    "31A681FCFFFB3E428420CAE280DED89292B12A3B0F59E19B7A73E32A8AE4C213"
)


class PrepareCandidateTest(unittest.TestCase):

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / ".changelog").mkdir()
        (self.root / "settings.gradle.kts").write_text(
            'rootProject.name = "autojs6-plugin-opencc"\n',
            encoding="utf-8",
        )
        (self.root / "version.properties").write_text(
            "VERSION_NAME=1.3.0\nVERSION_BUILD=20\n",
            encoding="utf-8",
        )
        changelog = {
            "changelog_label_improvement": "Improvement",
            "$data": {
                "v1.3.0": {
                    "released_date": "2026/09/03",
                    "improvement": ["Verified signed candidate construction."],
                },
            },
        }
        (self.root / ".changelog" / "lang_en.json").write_text(
            json.dumps(changelog),
            encoding="utf-8",
        )
        (self.root / "opencc-upstream.properties").write_text(
            "\n".join(
                (
                    "OPENCC_VERSION=1.4.2",
                    "OPENCC_TAG=ver.1.4.2",
                    f"OPENCC_COMMIT={'3' * 40}",
                    "OPENCC_RESOURCE_ASSET=opencc-v1.4.2-resources.zip",
                    f"OPENCC_RESOURCE_SHA256={'4' * 64}",
                    "OPENCC_RESOURCE_SIZE=1237703",
                    "",
                ),
            ),
            encoding="utf-8",
        )
        self.input_dir = self.root / "input"
        self.input_dir.mkdir()
        self.context = load_release_context(self.root)
        self.create_raw_set()
        records, foreign = collect_records(self.input_dir, self.context)
        self.assertEqual([], foreign)
        self.bundle = create_bundle(
            self.context,
            records,
            self.root / "build" / "release" / "v1.3.0",
            signer_digest=SIGNER_SHA256,
        )
        self.baseline = CandidateBaseline(
            tag="v1.3.0",
            source_sha=BASELINE_SHA,
            version_name="1.3.0",
            version_build=20,
            signer_certificate_sha256=SIGNER_SHA256,
            package_sizes={record.abi: record.size for record in records},
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def create_fake_apk(
        self,
        path: Path,
        abis: set[str],
        marker: str,
        extra_entry: str | None = None,
    ) -> None:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("AndroidManifest.xml", f"manifest-{marker}")
            archive.writestr("classes.dex", f"dex-{marker}")
            for abi in sorted(abis):
                archive.writestr(f"lib/{abi}/libopencc_jni.so", f"native-{abi}-{marker}")
            if extra_entry is not None:
                archive.writestr(extra_entry, "must-not-ship")

    def create_raw_set(self) -> None:
        all_abis = {"arm64-v8a", "armeabi-v7a", "x86_64", "x86"}
        for abi in ABI_ORDER:
            self.create_fake_apk(
                self.input_dir / f"app-{abi}-release.apk",
                all_abis if abi == "universal" else {abi},
                abi,
            )

    def baseline_json(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "release": {
                "tag": self.baseline.tag,
                "source_sha": self.baseline.source_sha,
                "version_name": self.baseline.version_name,
                "version_build": self.baseline.version_build,
                "signer_certificate_sha256": self.baseline.signer_certificate_sha256,
            },
            "package_sizes": self.baseline.package_sizes,
            "limits": {
                "max_growth_bytes": MAX_APK_GROWTH_BYTES,
                "max_growth_percent": MAX_APK_GROWTH_PERCENT,
            },
        }

    def test_finalize_candidate_is_idempotent_and_emits_exact_provenance(self) -> None:
        with patch(
            "scripts.release.prepare_candidate.verify_signatures",
            return_value=SIGNER_SHA256,
        ):
            records, manifest = finalize_candidate(
                self.context,
                self.bundle,
                SOURCE_SHA,
                20,
                SIGNER_SHA256,
                self.baseline,
                Path("unused-apksigner"),
            )
            first_payload = manifest.read_bytes()
            _, second_manifest = finalize_candidate(
                self.context,
                self.bundle,
                SOURCE_SHA,
                20,
                SIGNER_SHA256,
                self.baseline,
                Path("unused-apksigner"),
            )

        self.assertEqual(first_payload, second_manifest.read_bytes())
        data = json.loads(first_payload)
        self.assertEqual("signed-candidate-only", data["artifact_role"])
        self.assertEqual("SuperMonster003/AutoJs6-Plugin-OpenCC", data["repository"])
        self.assertEqual(SOURCE_SHA, data["source_sha"])
        self.assertEqual({"name": "1.3.0", "build": 20}, data["version"])
        self.assertEqual(SIGNER_SHA256, data["signer_certificate_sha256"])
        self.assertEqual(list(ABI_ORDER), [package["abi"] for package in data["packages"]])
        self.assertEqual(
            {record.filename for record in records}
            | {"SHA256SUMS.txt", "RELEASE_NOTES.md", "CANDIDATE.json"},
            {path.name for path in self.bundle.iterdir()},
        )

    def test_tampered_checksums_are_rejected(self) -> None:
        (self.bundle / "SHA256SUMS.txt").write_text("tampered\n", encoding="utf-8")
        with patch(
            "scripts.release.prepare_candidate.verify_signatures",
            return_value=SIGNER_SHA256,
        ), self.assertRaisesRegex(ReleaseError, "SHA256SUMS"):
            finalize_candidate(
                self.context,
                self.bundle,
                SOURCE_SHA,
                20,
                SIGNER_SHA256,
                self.baseline,
                Path("unused-apksigner"),
            )

    def test_unexpected_bundle_file_is_rejected(self) -> None:
        (self.bundle / "unexpected.txt").write_text("unexpected", encoding="utf-8")
        with patch(
            "scripts.release.prepare_candidate.verify_signatures",
            return_value=SIGNER_SHA256,
        ), self.assertRaisesRegex(ReleaseError, "inventory mismatch"):
            finalize_candidate(
                self.context,
                self.bundle,
                SOURCE_SHA,
                20,
                SIGNER_SHA256,
                self.baseline,
                Path("unused-apksigner"),
            )

    def test_signer_must_match_environment_and_published_baseline(self) -> None:
        with self.assertRaisesRegex(ReleaseError, "published baseline"):
            finalize_candidate(
                self.context,
                self.bundle,
                SOURCE_SHA,
                20,
                "B" * 64,
                self.baseline,
                Path("unused-apksigner"),
            )

    def test_apk_size_must_pass_both_growth_limits(self) -> None:
        records, _ = collect_records(self.bundle, self.context)
        abi = records[0].abi
        baseline_size = self.baseline.package_sizes[abi]
        self.assertEqual(
            min(
                baseline_size + MAX_APK_GROWTH_BYTES,
                baseline_size * (100 + MAX_APK_GROWTH_PERCENT) // 100,
            ),
            maximum_candidate_size(baseline_size),
        )
        oversized = [
            type(record)(
                abi=record.abi,
                source=record.source,
                filename=record.filename,
                crc32=record.crc32,
                sha256=record.sha256,
                size=(maximum_candidate_size(baseline_size) + 1 if record.abi == abi else record.size),
            )
            for record in records
        ]
        with self.assertRaisesRegex(ReleaseError, "too large"):
            verify_package_sizes(oversized, self.baseline)

    def test_signing_material_inside_an_apk_is_rejected(self) -> None:
        suspicious = self.input_dir / "app-x86-release.apk"
        suspicious.unlink()
        self.create_fake_apk(suspicious, {"x86"}, "x86", "assets/release-key.jks")
        records, _ = collect_records(self.input_dir, self.context)
        with self.assertRaisesRegex(ReleaseError, "Signing material is packaged"):
            verify_no_signing_material(records)

    def test_baseline_schema_and_limits_are_fail_closed(self) -> None:
        path = self.root / "baseline.json"
        data = self.baseline_json()
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(self.baseline, load_candidate_baseline(path))

        data["limits"]["max_growth_percent"] = 100  # type: ignore[index]
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ReleaseError, "percentage-growth policy"):
            load_candidate_baseline(path)

    def test_repository_baseline_records_the_published_v130_assets(self) -> None:
        repository_root = Path(__file__).resolve().parents[3]
        baseline = load_candidate_baseline(
            repository_root / "scripts" / "release" / "candidate-baseline.json",
        )
        self.assertEqual("v1.3.0", baseline.tag)
        self.assertEqual("0cd4c89f51e587473227a8d6e46c7f17d2455d56", baseline.source_sha)
        self.assertEqual(20, baseline.version_build)
        self.assertEqual(PUBLISHED_SIGNER_SHA256, baseline.signer_certificate_sha256)
        self.assertEqual(
            {
                "arm64-v8a": 1553948,
                "armeabi-v7a": 1215154,
                "x86_64": 1562729,
                "x86": 1516110,
                "universal": 3889481,
            },
            baseline.package_sizes,
        )

    def test_version_or_build_rollback_is_rejected(self) -> None:
        older_version_root = self.root / "older"
        older_version_root.mkdir()
        (older_version_root / "settings.gradle.kts").write_text(
            'rootProject.name = "autojs6-plugin-opencc"\n',
            encoding="utf-8",
        )
        (older_version_root / "version.properties").write_text(
            "VERSION_NAME=1.2.9\nVERSION_BUILD=19\n",
            encoding="utf-8",
        )
        (older_version_root / ".changelog").mkdir()
        (older_version_root / ".changelog" / "lang_en.json").write_text(
            json.dumps({"$data": {"v1.2.9": {}}}),
            encoding="utf-8",
        )
        older = load_release_context(older_version_root)
        with self.assertRaisesRegex(ReleaseError, "older than baseline"):
            verify_version_progression(older, 19, self.baseline)

    def test_git_source_requires_head_baseline_tag_cleanliness_and_submodules(self) -> None:
        responses = {
            ("rev-parse", "HEAD"): SOURCE_SHA,
            ("rev-parse", "refs/tags/v1.3.0^{commit}"): BASELINE_SHA,
            ("status", "--porcelain=v1", "--untracked-files=no"): "",
            ("submodule", "status", "--recursive"): " " + "3" * 40 + " opencc",
        }

        def output(_root: Path, *arguments: str) -> str:
            return responses[arguments]

        with patch("scripts.release.prepare_candidate.git_output", side_effect=output):
            verify_git_source(self.root, SOURCE_SHA, self.baseline)

        responses[("status", "--porcelain=v1", "--untracked-files=no")] = " M tracked.txt"
        with patch(
            "scripts.release.prepare_candidate.git_output",
            side_effect=output,
        ), self.assertRaisesRegex(ReleaseError, "Tracked source tree changed"):
            verify_git_source(self.root, SOURCE_SHA, self.baseline)

    def test_git_source_rejects_a_drifted_baseline_tag(self) -> None:
        def output(_root: Path, *arguments: str) -> str:
            if arguments == ("rev-parse", "HEAD"):
                return SOURCE_SHA
            if arguments == ("rev-parse", "refs/tags/v1.3.0^{commit}"):
                return "5" * 40
            raise AssertionError(f"Unexpected git arguments: {arguments}")

        with patch(
            "scripts.release.prepare_candidate.git_output",
            side_effect=output,
        ), self.assertRaisesRegex(ReleaseError, "baseline tag"):
            verify_git_source(self.root, SOURCE_SHA, self.baseline)

    def test_sha_and_certificate_formats_are_canonical(self) -> None:
        self.assertEqual(SOURCE_SHA, canonical_source_sha(SOURCE_SHA))
        self.assertEqual(SIGNER_SHA256, canonical_certificate_sha256(SIGNER_SHA256, "certificate"))
        with self.assertRaises(ReleaseError):
            canonical_source_sha(SOURCE_SHA.upper().replace("1", "A"))
        with self.assertRaises(ReleaseError):
            canonical_certificate_sha256("a" * 64, "certificate")


if __name__ == "__main__":
    unittest.main()
