cmake_minimum_required(VERSION 3.22.1)

project(opencc_jni LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(OPENCC_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/OpenCC")
if(NOT EXISTS "${OPENCC_SOURCE_DIR}/CMakeLists.txt")
  message(FATAL_ERROR
    "OpenCC source is missing. Initialize the pinned submodule before building: "
    "git submodule update --init --recursive"
  )
endif()

# Build only the library dependency graph needed by the JNI target. The upstream
# data directory defines host-side dictionary generators that cannot run during
# an Android cross-build; EXCLUDE_FROM_ALL keeps those targets out of this graph.
set(BUILD_SHARED_LIBS OFF CACHE BOOL "Build OpenCC statically" FORCE)
set(OPENCC_ENABLE_INSTALL OFF CACHE BOOL "Disable OpenCC install targets" FORCE)
set(BUILD_DOCUMENTATION OFF CACHE BOOL "Disable OpenCC documentation" FORCE)
set(ENABLE_GTEST OFF CACHE BOOL "Disable OpenCC tests" FORCE)
set(ENABLE_BENCHMARK OFF CACHE BOOL "Disable OpenCC benchmarks" FORCE)
set(BUILD_OPENCC_JIEBA_PLUGIN OFF CACHE BOOL "Disable the optional Jieba plugin" FORCE)
set(BUILD_PYTHON OFF CACHE BOOL "Disable Python bindings" FORCE)
set(USE_SYSTEM_MARISA OFF CACHE BOOL "Use the pinned bundled Marisa" FORCE)

add_subdirectory(
  "${OPENCC_SOURCE_DIR}"
  "${CMAKE_CURRENT_BINARY_DIR}/opencc"
  EXCLUDE_FROM_ALL
)

add_library(opencc_jni SHARED opencc_jni.cpp)

target_link_libraries(opencc_jni PRIVATE OpenCC::OpenCC)

target_compile_options(opencc_jni PRIVATE
  -Wall
  -Wextra
  -Wpedantic
  -ffunction-sections
  -fdata-sections
)

target_compile_definitions(opencc_jni PRIVATE
  OPENCC_PINNED_VERSION="${OPENCC_PINNED_VERSION}"
  OPENCC_PINNED_COMMIT="${OPENCC_PINNED_COMMIT}"
)

# NDK r28+ already emits flexible-page-size binaries by default. Keep the
# linker requirements explicit so a future toolchain change cannot silently
# regress the final JNI ELF alignment.
target_link_options(opencc_jni PRIVATE
  "-Wl,--gc-sections"
  "-Wl,--exclude-libs,ALL"
  "-Wl,-z,max-page-size=16384"
  "-Wl,-z,common-page-size=16384"
  "-Wl,-z,relro"
  "-Wl,-z,now"
)

set_target_properties(opencc_jni PROPERTIES
  CXX_VISIBILITY_PRESET hidden
  VISIBILITY_INLINES_HIDDEN YES
)
