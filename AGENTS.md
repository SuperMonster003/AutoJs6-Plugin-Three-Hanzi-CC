# AutoJs6-Plugin-Three-Hanzi-CC

This repository owns its existing plugin implementation and contracts. Keep identity values in version.properties, Manifest and the current shared API aligned.



## Shared engineering baseline (2026-09-13)

- Apply the workspace AutoJs6 plugin conventions to code, resources, builds and tests. Preserve existing owner decisions and historical release evidence; a milestone or RC is not silently promoted to stable.
- Inspect status, branch, recent history and scoped diffs before editing. Preserve pre-existing work. Use Conventional Commits; before each commit set VERSION_BUILD to the next reachable Git commit count. The final count must match HEAD. Do not push or publish without the user's instruction.
- Root settings alone applies the public platform-versions 1.8.3 plugin before build-logic. Native alignment uses the same published version where applicable. Never use mavenLocal, sibling binary dependencies, gradle/data overrides or temporary migration backups.
- Keep signing resolution and the appendDigestToReleasedFiles task. It depends on assembleRelease and rejects incomplete signing, unexpected APK sets and unsigned APKs. Signing secrets and generated APKs remain ignored.
- All contract entry points use org.autojs.permission.PLUGIN. Preserve the no-display Wake Activity, its metadata, WAKE action and DEFAULT category, and test discovery and explicit Binder binding. OEM first-install activation must be reported separately from a manifest test.
- PluginInfo uses installed package versions, localized descriptions and accurate capabilities. Pure JVM providers explicitly return empty supportedAbis; native providers describe actual packaged ABIs.
- The app title is English and non-translatable. Maintain all ten languages, matching default/explicit English, sorted resource names and ASCII punctuation. Keep the real mipmap/ic_launcher.png.
- Edit JSON/templates rather than generated README/changelog. Keep the root README in Simplified Chinese, use the centered header, and omit IDE version badges. Changelog source stays in .changelog; generated language assets stay in app/src/main/assets/doc.
- Run py .python/generate_markdown.py and its read-only --check after document edits. Run relevant Python and JVM tests, debug and androidTest assembly, lint, and signed release collection. Platform changes additionally require the Temurin vendor simulation from the workspace conventions. Use actual application variant task names if the repository differs.
- Preserve native source/license locks, ABI inventory and 16 KB alignment checks. Existing device evidence is historical; never claim a new install, Binder or OEM test that was not executed.


## Standalone settings convention (2026-09-29)

- Follow the workspace `AUTOJS6_PLUGIN_STANDALONE_SETTINGS_AGENTS.md`: language, dark mode, theme color, launcher icon; flat grouped rows, 16/14sp text, 72dp minimum, 24dp padding, a 24dp line icon in a 40dp slot, and text-aligned dividers.
- Appearance dialogs keep draft changes local until OK. Use the shared neutral surfaces and HCT primary/onPrimary roles. Presets and a single HEX/RGB field preview the actual control colors; Cancel writes nothing.
- New launcher installs default to Auto. Keep PackageManager as the sole mode store, normalize mixed upgrade states through the internal MY_PACKAGE_REPLACED receiver, preserve unique explicit choices, and migrate mutable shortcut ownership before disabling an alias.
- Host appearance acquisition and IPC must run on a worker. Cache in process, discard stale generations, refresh only effective followed fields, and defer host-driven recreation after user interaction or while a dialog is open. Never rewrite local choices because the host is unavailable.

## Optical icon standard (2026-10-03)

- Follow `../AUTOJS6_PLUGIN_BLACK_N_WHITE_ADAPTIVE_ICON_AGENTS.md` for every standalone plugin, including the Plugin Center. `.python/icon_geometry.py` v1 is a self-contained copy of the common geometry algorithm; keep its implementation identical across the standalone plugins. Never read sibling checkouts during a build.
- Derive size from the equal-weight combination of visible bounding-box area (alpha >= 16) and alpha-weighted ink area. Target visible size is 0.52 of the canvas, with only documented optical corrections in 0.94-1.06. The adaptive ratio is always the UI ratio multiplied by 72/108. This supersedes older hardcoded UI/adaptive widths in historical notes. Preserve aspect ratio, optical placement and final nonzero-alpha safety checks.
- Current geometry and tonal parameters are authoritative in `.icons/recipe.json`; do not restore pre-Hanzi hardcoded widths.
- Generate `mipmap/ic_plugin_center.png` and its night counterpart from the same geometry as the transparent UI/launcher mode. They are transparent neutral artwork for installed and catalog entries, independent of the active launcher alias. Keep them through `raw/keep_plugin_center_icon.xml`. Existing separate brand assets retain their original purpose.
- Black, white and neutral grayscale are allowed for every plugin without per-plugin approval. Pure silhouettes default to #272727 / #D8D8D8; shaded artwork may preserve meaningful tonal details with R=G=B and matching day/night alpha. Stamp Mail is one example, not an exception. Keep light-theme artwork dark enough and dark-theme artwork light enough to remain legible. Do not introduce a filled background into the Plugin Center assets.
- Run the icon generator and its read-only `--check`, `.python/tests/test_icon_geometry.py`, existing icon regressions, and review the full set at 36/48/64 px in both themes and in launcher masks. `.github/workflows/icons.yml` verifies Windows/Linux reproducibility. Synthetic previews do not replace actual launcher verification.


## Three-series identity and standalone app (2026-10-04)

- Follow `../AUTOJS6_PLUGIN_THREE_SERIES_RENAME_AGENTS.md`, `../AUTOJS6_PLUGIN_STANDALONE_SETTINGS_AGENTS.md` and `../AUTOJS6_PLUGIN_BLACK_N_WHITE_ADAPTIVE_ICON_AGENTS.md`. The current user's rename/merge decisions override the earlier identity-preservation wording above.
- Product: `3-Hanzi CC`; repository: `AutoJs6-Plugin-Three-Hanzi-CC`; applicationId/namespace: `io.github.supermonster003.autojs6.plugin.three.hanzi.cc`; plugin ID: `three-hanzi-cc`; version: `2.0.0`. New Android identity; old apps/data are not removed or migrated automatically.
- Public capability actions, AIDL packages, transaction order and engine names describe behavior and remain compatible. Four stable launcher aliases default to Auto; settings expose language, night mode, theme color, launcher icon and bundled release history.
- Preserve the maintainer's existing `.icons/recipe.json` geometry and color parameters. Update only identity/output mappings during the rename. The nativebridge Java package and exported JNI symbols move together; upstream OpenCC names, dictionaries and the `opencc` engine/category stay unchanged. The INFO category and product ID are `three-hanzi-cc`.
- Commit `.icons/`, portable generators, icon CI, `.gitattributes` and generated resources together. Ignore only caches, local signing files and build outputs. Icon Studio drafts/backups remain outside this repository in its ignored `.studio/`.
