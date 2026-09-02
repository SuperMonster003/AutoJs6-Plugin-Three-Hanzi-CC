from __future__ import annotations

import importlib.util
import json
import unittest
import xml.etree.ElementTree as ElementTree
from copy import deepcopy
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
GENERATOR_PATH = REPOSITORY_ROOT / ".python" / "generate_markdown.py"
SPEC = importlib.util.spec_from_file_location("opencc_generate_markdown", GENERATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load localization generator: {GENERATOR_PATH}")
generate_markdown = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_markdown)


class LocalizedArtifactsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.string_sources = json.loads(
            (REPOSITORY_ROOT / ".readme" / "android_strings.json").read_text(encoding="utf-8"),
        )

    def test_single_source_builds_the_exact_documentation_and_android_inventory(self) -> None:
        artifacts = generate_markdown.build_artifacts(REPOSITORY_ROOT)
        self.assertEqual(generate_markdown.EXPECTED_ARTIFACT_COUNT, len(artifacts))
        relative_paths = {path.relative_to(REPOSITORY_ROOT).as_posix() for path in artifacts}
        self.assertIn("README.md", relative_paths)
        self.assertIn(".readme/README-ar.md", relative_paths)
        self.assertIn("app/src/main/res/raw/plugin_instruction.md", relative_paths)
        self.assertIn("app/src/main/res/values/strings.xml", relative_paths)
        self.assertIn("app/src/main/res/values-ar/strings.xml", relative_paths)

    def test_android_strings_require_exact_locale_and_key_parity(self) -> None:
        generate_markdown.validate_android_string_sources(self.string_sources)

        missing_locale = deepcopy(self.string_sources)
        del missing_locale["ar"]
        with self.assertRaisesRegex(generate_markdown.MarkdownGenerationError, "languages differ"):
            generate_markdown.validate_android_string_sources(missing_locale)

        missing_key = deepcopy(self.string_sources)
        del missing_key["fr"]["standalone_paste_action"]
        with self.assertRaisesRegex(generate_markdown.MarkdownGenerationError, "key mismatch"):
            generate_markdown.validate_android_string_sources(missing_key)

    def test_platform_locale_config_lists_the_same_ten_locales(self) -> None:
        root = ElementTree.parse(
            REPOSITORY_ROOT / "app" / "src" / "main" / "res" / "xml" / "locales_config.xml",
        ).getroot()
        android_name = "{http://schemas.android.com/apk/res/android}name"
        configured = {element.attrib[android_name] for element in root.findall("locale")}
        self.assertEqual(set(generate_markdown.LANGUAGE_CODES), configured)

    def test_android_format_arguments_cannot_drift_between_locales(self) -> None:
        changed = deepcopy(self.string_sources)
        changed["es"]["standalone_status_failed"] = "Error de conversión"
        with self.assertRaisesRegex(generate_markdown.MarkdownGenerationError, "format arguments differ"):
            generate_markdown.validate_android_string_sources(changed)

    def test_every_documented_screenshot_is_pinned_and_referenced_once(self) -> None:
        template = (REPOSITORY_ROOT / ".readme" / "template_readme.md").read_text(encoding="utf-8")
        generate_markdown.validate_screenshot_assets(REPOSITORY_ROOT, template)
        self.assertEqual(
            {
                "plugin-center-enabled.png",
                "standalone-phone-light.png",
                "standalone-rtl-large-dark.png",
            },
            {spec[0] for spec in generate_markdown.SCREENSHOT_SPECS},
        )


if __name__ == "__main__":
    unittest.main()
