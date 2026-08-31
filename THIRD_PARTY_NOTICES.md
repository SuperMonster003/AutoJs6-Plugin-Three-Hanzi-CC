# Third-party notices

This file records third-party code compiled into the official OpenCC native backend. The plugin
itself remains licensed under the Mozilla Public License 2.0; the components below retain their
own licenses.

## OpenCC

- Project: Open Chinese Convert (OpenCC)
- Source: <https://github.com/BYVoid/OpenCC>
- Pinned release: `ver.1.4.2`
- Pinned commit: `025f371dc76b598d77384fbdab90c937471844d8`
- Copyright: Carbo Kuo and OpenCC contributors
- License: Apache License 2.0
- License text: `opencc-native/src/main/cpp/third_party/OpenCC/LICENSE`

The official resource ZIP is produced from the same source commit and is distributed under the
OpenCC project terms.

## Marisa Trie

- Component: marisa-trie 0.3.1, bundled by OpenCC
- Source: <https://github.com/s-yata/marisa-trie>
- Copyright: 2010–2025 Susumu Yata
- License offered upstream: BSD-2-Clause OR LGPL-2.1-or-later
- License selected for this distribution: BSD-2-Clause
- License text: `opencc-native/src/main/cpp/third_party/OpenCC/deps/marisa-0.3.1/COPYING.md`

## Darts Clone

- Component: Darts Clone 0.32h, bundled by OpenCC
- Source: <https://github.com/s-yata/darts-clone>
- Copyright: 2008–2014 Susumu Yata
- License: BSD-2-Clause
- License text: `opencc-native/src/main/cpp/third_party/OpenCC/deps/darts-clone-0.32h/COPYING.md`

## RapidJSON

- Component: RapidJSON 1.1.0-compatible vendored headers, bundled by OpenCC
- Source: <https://github.com/Tencent/rapidjson>
- Copyright: 2015 THL A29 Limited, a Tencent company, and Milo Yip
- License: MIT
- License notice: retained at the beginning of the vendored RapidJSON headers, including
  `opencc-native/src/main/cpp/third_party/OpenCC/deps/rapidjson-1.1.0/rapidjson/rapidjson.h`

Only the components needed by the OpenCC core dependency graph are linked into
`libopencc_jni.so`. OpenCC's optional tests, benchmarks, CLI tools, Python bindings, Node.js
bindings and Jieba plugin are disabled for the Android build.
