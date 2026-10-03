"""Generate separate transparent UI icons and adaptive/legacy launcher icons.

The original 80 px OpenCC artwork is retained in icons/opencc-original.png. Its dark
glyph is separated from the white contour using luminance multiplied by alpha, then
recolored without retaining an opaque contour. Run with --check to verify without writes.
Auto is the default launcher choice. Explicit light/dark and best-effort automatic modes
have independent resources; transparent launcher icons follow the launcher configuration; brand UI assets stay separate.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageChops, ImageOps
import icon_geometry as geometry

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "app/src/main/res"
SOURCE = ROOT / ".python/icons/opencc-original.png"
SIZE = 432
SCALE = 4
DAY_GLYPH = (0x27, 0x27, 0x27)
NIGHT_GLYPH = (0xD8, 0xD8, 0xD8)
NIGHT_BACKGROUND = (0x21, 0x21, 0x21, 255)
DAY_BACKGROUND = (0xFA, 0xFA, 0xFA, 255)


def source_alpha() -> Image.Image:
    source = Image.open(SOURCE).convert("RGBA")
    alpha = ImageChops.multiply(source.getchannel("A"), ImageOps.invert(source.convert("L")))
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("Icon source has no visible artwork")
    alpha = alpha.crop(bounds)
    return alpha


# Optical geometry v1; ratios are derived, not tuned independently by surface.
OPTICAL_X = 0.0
OPTICAL_Y = 0.0
OPTICAL_SCALE = 1.0
UI_GLYPH, ADAPTIVE_GLYPH = geometry.normalized_ratios(source_alpha(), OPTICAL_SCALE)


def render(alpha, ratio, color, background=None):
    return geometry.render(alpha, ratio, color, background,
                           adaptive=ratio == ADAPTIVE_GLYPH,
                           optical_x=OPTICAL_X, optical_y=OPTICAL_Y)


def generated_files() -> dict[Path, bytes]:
    alpha = source_alpha()
    images = {
        "mipmap/ic_launcher_transparent.png": render(alpha, UI_GLYPH, DAY_GLYPH),
        "mipmap-night/ic_launcher_transparent.png": render(alpha, UI_GLYPH, NIGHT_GLYPH),
        "mipmap/ic_launcher_system.png": render(alpha, UI_GLYPH, NIGHT_GLYPH, NIGHT_BACKGROUND),
        "mipmap/ic_launcher_system_foreground.png": render(alpha, ADAPTIVE_GLYPH, NIGHT_GLYPH),
        "mipmap/ic_launcher_system_light.png": render(alpha, UI_GLYPH, DAY_GLYPH, DAY_BACKGROUND),
        "mipmap/ic_launcher_system_light_foreground.png": render(alpha, ADAPTIVE_GLYPH, DAY_GLYPH),
        "mipmap/ic_launcher_system_monochrome.png": render(alpha, ADAPTIVE_GLYPH, (0, 0, 0)),
    }
    images["mipmap/ic_plugin_center.png"] = images["mipmap/ic_launcher_transparent.png"]
    images["mipmap-night/ic_plugin_center.png"] = images["mipmap-night/ic_launcher_transparent.png"]
    result = {}
    for name, image in images.items():
        result[RES / name] = geometry.encode_png(image)
    def adaptive(foreground: str, background: str) -> bytes:
        return f'''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/{background}"/>
    <foreground android:drawable="@mipmap/{foreground}"/>
    <monochrome android:drawable="@mipmap/ic_launcher_system_monochrome"/>
</adaptive-icon>
'''.encode("utf-8")
    for name, background in (("ic_launcher_system", "ic_launcher_system_background"), ("ic_launcher_system_light", "ic_launcher_system_background_light")):
        result[RES / "mipmap-anydpi-v26" / f"{name}.xml"] = adaptive(f"{name}_foreground", background)
    for name, color in (("ic_launcher_system_background", "#212121"), ("ic_launcher_system_background_light", "#FAFAFA")):
        result[RES / "values" / f"{name}.xml"] = (
            '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
            f'    <color name="{name}">{color}</color>\n</resources>\n'
        ).encode("utf-8")
    # Keep Auto's own resource ID in the compiled manifest. Resource aliases in
    # values/ are eagerly resolved by PackageManager and freeze one theme's ID.
    for qualifier, target, background in (("", "ic_launcher_system", "ic_launcher_system_background"), ("-notnight", "ic_launcher_system_light", "ic_launcher_system_background_light")):
        result[RES / f"mipmap{qualifier}" / "ic_launcher_system_auto.xml"] = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            f'<bitmap xmlns:android="http://schemas.android.com/apk/res/android" android:src="@mipmap/{target}"/>\n'
        ).encode("utf-8")
        result[RES / f"mipmap{qualifier}-anydpi-v26" / "ic_launcher_system_auto.xml"] = adaptive(f"{target}_foreground", background)
    result[RES / "mipmap/ic_launcher.png"] = SOURCE.read_bytes()
    result[RES / "mipmap-night/ic_launcher.png"] = (SOURCE.parent / "opencc-original-night.png").read_bytes()
    result[RES / "raw/keep_plugin_center_icon.xml"] = geometry.KEEP_RESOURCE
    return result


def obsolete_files() -> list[Path]:
    # The pre-existing brand assets belong to application/README/About, independently
    # of the selectable launcher aliases, and must remain intact.
    return [path for path in (RES / "values/ic_launcher_system_auto.xml", RES / "values-notnight/ic_launcher_system_auto.xml") if path.is_file()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check all generated resources without changing files")
    options = parser.parse_args()
    outputs = generated_files()
    stale = [path for path, expected in outputs.items() if not path.is_file() or path.read_bytes() != expected]
    obsolete = obsolete_files()
    if options.check:
        if stale or obsolete:
            raise SystemExit("Stale icon resources: " + ", ".join(str(p.relative_to(ROOT)) for p in stale + obsolete))
        print(f"Verified {len(outputs)} icon resources")
        return
    for path in obsolete:
        if not path.resolve().is_relative_to(RES.resolve()):
            raise ValueError("Icon output escaped resource directory")
        path.unlink()
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f"Generated {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
