# Screenshot capture notes

These documentation assets are original Android runtime captures. They are checked byte-for-byte by
`.python/generate_markdown.py`, including their PNG format, dimensions, SHA-256, inventory, and single
reference from the multilingual README template.

## Standalone App captures

- Build: M5-D debug candidate with official OpenCC 1.4.2 resources
- Capture date: 2026-09-03
- Runtime: Android 16 / API 36 / x86_64 / 16 KB memory pages
- Emulator display override: 1080 x 2400 at 360 dpi; captured bitmap: 1080 x 1920
- Fixture: `OpenccDocumentationScreenshotTest.capturePopulatedStandaloneScreen`
- Processing: the PNG files written by Android `UiAutomation.takeScreenshot()` were pulled byte-for-byte;
  there was no crop, compositing, resizing, color adjustment, or AI editing
- Privacy review: the fixture uses only fixed repository test text; no account, notification, user file,
  clipboard content, device identifier, or network data is visible

| File | Locale and accessibility state | Verified state |
|---|---|---|
| `standalone-phone-light.png` | English, day theme, font scale 1.0 | A completed offline S2T conversion with source, type, result, and explicit actions |
| `standalone-rtl-large-dark.png` | Arabic, night theme, font scale 1.7 | RTL mirroring and large text without clipped controls; the page remains vertically scrollable |

## Plugin-center capture

- Plugin: OpenCC 1.0.2, version code 17
- Capture date: 2026-08-31
- Viewport: 720 x 1280
- Theme: dark
- Locale: English
- Processing: copied byte-for-byte from the supplied PNG, with no crop, compositing, color adjustment,
  or AI editing
- Privacy review: no accounts, notifications, user files, or device identifiers are visible; other rows
  contain installed-plugin metadata only
- PNG metadata: one embedded ICC color profile; no EXIF, text, or comment metadata detected; alpha channel
  is fully opaque

| File | Verified state |
|---|---|
| `plugin-center-enabled.png` | OpenCC 1.0.2 (17) is listed in the AutoJs6 plugin center and its switch is enabled |

## SHA-256

```text
EA87F97D5CA5A82B95F0FF397E90AC564AF59205BAFBF86F7C761AB77F364E01  plugin-center-enabled.png
BC9A577A0CF9892BAE81B66CD2DD137C578BF6C8C71156C4503978CF5662ED4C  standalone-phone-light.png
BCCBF805931990C056AB1E78E628F63F0DAE733081827AE899E1BC31D4900F6F  standalone-rtl-large-dark.png
```
