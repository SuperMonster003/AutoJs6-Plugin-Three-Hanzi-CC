import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


spec = importlib.util.spec_from_file_location("generate_markdown", Path(__file__).with_name("generate_markdown.py"))
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class AndroidResourceRenderingTest(unittest.TestCase):
    def render(self, strings):
        return ET.fromstring(generator.render_android_strings({
            "text_plugin_synopsis": "Offline Chinese conversion",
            "android_strings": strings,
        }))

    def test_resource_names_are_sorted_including_plugin_description(self):
        resources = self.render({"standalone_z": "Last", "error_unsupported_conversion_type": "Unsupported: %1$s", "standalone_a": "First"})
        names = [resource.attrib["name"] for resource in resources]
        self.assertEqual(sorted(names), names)
        self.assertEqual(4, len(names))

    def test_ascii_ellipsis_has_lint_annotation_and_preserves_arguments(self):
        resources = self.render({"standalone_progress": "Converting %1$s..."})
        progress = resources.find("string[@name='standalone_progress']")
        self.assertEqual("Converting %1$s...", progress.text)
        self.assertEqual("TypographyEllipsis", progress.attrib["{http://schemas.android.com/tools}ignore"])

    def test_non_ascii_punctuation_is_rejected_instead_of_silently_rewritten(self):
        for punctuation in ("\u2026", "\u060c", "\u2019", "\u00b7"):
            with self.subTest(punctuation=punctuation), self.assertRaises(Exception):
                self.render({"standalone_text": "Text" + punctuation})

    def test_localized_letters_and_android_escaping_are_preserved(self):
        resources = self.render({"standalone_text": "日本語 français العربية <&> 'quoted'"})
        text = resources.find("string[@name='standalone_text']").text
        self.assertEqual("日本語 français العربية <&> \\'quoted\\'", text)


if __name__ == "__main__":
    unittest.main()
