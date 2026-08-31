#include <jni.h>

#include "ResourceProvider.hpp"
#include "SimpleConverter.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <exception>
#include <limits>
#include <memory>
#include <mutex>
#include <string>
#include <string_view>
#include <unordered_map>

namespace {

constexpr std::uint32_t kReplacementCharacter = 0xfffd;

constexpr std::array<std::string_view, 14> kAllowedConfigs = {
    "hk2s.json",
    "hk2t.json",
    "jp2t.json",
    "s2hk.json",
    "s2t.json",
    "s2tw.json",
    "s2twp.json",
    "t2hk.json",
    "t2s.json",
    "t2tw.json",
    "t2jp.json",
    "tw2s.json",
    "tw2t.json",
    "tw2sp.json",
};

std::mutex gConverterMutex;
std::string gResourceArchivePath;
std::shared_ptr<opencc::ZipResourceProvider> gResourceProvider;
std::unordered_map<std::string, std::unique_ptr<opencc::SimpleConverter>> gConverters;

void AppendUtf8(std::uint32_t codePoint, std::string& output) {
  if (codePoint <= 0x7f) {
    output.push_back(static_cast<char>(codePoint));
  } else if (codePoint <= 0x7ff) {
    output.push_back(static_cast<char>(0xc0 | (codePoint >> 6)));
    output.push_back(static_cast<char>(0x80 | (codePoint & 0x3f)));
  } else if (codePoint <= 0xffff) {
    output.push_back(static_cast<char>(0xe0 | (codePoint >> 12)));
    output.push_back(static_cast<char>(0x80 | ((codePoint >> 6) & 0x3f)));
    output.push_back(static_cast<char>(0x80 | (codePoint & 0x3f)));
  } else {
    output.push_back(static_cast<char>(0xf0 | (codePoint >> 18)));
    output.push_back(static_cast<char>(0x80 | ((codePoint >> 12) & 0x3f)));
    output.push_back(static_cast<char>(0x80 | ((codePoint >> 6) & 0x3f)));
    output.push_back(static_cast<char>(0x80 | (codePoint & 0x3f)));
  }
}

bool JavaStringToUtf8(JNIEnv* env, jstring input, std::string& output) {
  if (input == nullptr) {
    return false;
  }

  const jsize length = env->GetStringLength(input);
  const jchar* characters = env->GetStringChars(input, nullptr);
  if (characters == nullptr) {
    return false;
  }

  output.clear();
  output.reserve(static_cast<std::size_t>(length) * 3);
  for (jsize index = 0; index < length; ++index) {
    std::uint32_t codePoint = characters[index];
    if (codePoint >= 0xd800 && codePoint <= 0xdbff) {
      if (index + 1 < length) {
        const std::uint32_t low = characters[index + 1];
        if (low >= 0xdc00 && low <= 0xdfff) {
          codePoint = 0x10000 + ((codePoint - 0xd800) << 10) + (low - 0xdc00);
          ++index;
        } else {
          codePoint = kReplacementCharacter;
        }
      } else {
        codePoint = kReplacementCharacter;
      }
    } else if (codePoint >= 0xdc00 && codePoint <= 0xdfff) {
      codePoint = kReplacementCharacter;
    }
    AppendUtf8(codePoint, output);
  }

  env->ReleaseStringChars(input, characters);
  return true;
}

void AppendUtf16(std::uint32_t codePoint, std::u16string& output) {
  if (codePoint <= 0xffff) {
    output.push_back(static_cast<char16_t>(codePoint));
    return;
  }
  codePoint -= 0x10000;
  output.push_back(static_cast<char16_t>(0xd800 + (codePoint >> 10)));
  output.push_back(static_cast<char16_t>(0xdc00 + (codePoint & 0x3ff)));
}

jstring Utf8ToJavaString(JNIEnv* env, const std::string& input) {
  std::u16string output;
  output.reserve(input.size());

  for (std::size_t index = 0; index < input.size();) {
    const auto lead = static_cast<std::uint8_t>(input[index]);
    std::uint32_t codePoint = 0;
    std::size_t sequenceLength = 0;
    std::uint32_t minimum = 0;

    if (lead <= 0x7f) {
      codePoint = lead;
      sequenceLength = 1;
      minimum = 0;
    } else if ((lead & 0xe0) == 0xc0) {
      codePoint = lead & 0x1f;
      sequenceLength = 2;
      minimum = 0x80;
    } else if ((lead & 0xf0) == 0xe0) {
      codePoint = lead & 0x0f;
      sequenceLength = 3;
      minimum = 0x800;
    } else if ((lead & 0xf8) == 0xf0) {
      codePoint = lead & 0x07;
      sequenceLength = 4;
      minimum = 0x10000;
    } else {
      AppendUtf16(kReplacementCharacter, output);
      ++index;
      continue;
    }

    bool valid = index + sequenceLength <= input.size();
    if (valid) {
      for (std::size_t offset = 1; offset < sequenceLength; ++offset) {
        const auto continuation = static_cast<std::uint8_t>(input[index + offset]);
        if ((continuation & 0xc0) != 0x80) {
          valid = false;
          break;
        }
        codePoint = (codePoint << 6) | (continuation & 0x3f);
      }
    }

    if (!valid || codePoint < minimum || codePoint > 0x10ffff
        || (codePoint >= 0xd800 && codePoint <= 0xdfff)) {
      AppendUtf16(kReplacementCharacter, output);
      ++index;
      continue;
    }

    AppendUtf16(codePoint, output);
    index += sequenceLength;
  }

  if (output.size() > static_cast<std::size_t>(std::numeric_limits<jsize>::max())) {
    return nullptr;
  }

  static_assert(sizeof(char16_t) == sizeof(jchar), "JNI UTF-16 code unit size mismatch");
  const jchar empty = 0;
  const jchar* characters = output.empty()
      ? &empty
      : reinterpret_cast<const jchar*>(output.data());
  return env->NewString(characters, static_cast<jsize>(output.size()));
}

void ThrowJavaException(JNIEnv* env, const char* className, const std::string& message) {
  jclass exceptionClass = env->FindClass(className);
  if (exceptionClass != nullptr) {
    env->ThrowNew(exceptionClass, message.c_str());
    env->DeleteLocalRef(exceptionClass);
  }
}

bool IsAllowedConfig(const std::string& configFile) {
  return std::find(kAllowedConfigs.begin(), kAllowedConfigs.end(), configFile)
      != kAllowedConfigs.end();
}

opencc::SimpleConverter& GetConverterLocked(
    const std::string& configFile,
    const std::string& resourceArchivePath) {
  if (gResourceProvider == nullptr || gResourceArchivePath != resourceArchivePath) {
    auto provider = std::make_shared<opencc::ZipResourceProvider>(resourceArchivePath);
    gConverters.clear();
    gResourceProvider = std::move(provider);
    gResourceArchivePath = resourceArchivePath;
  }

  auto existing = gConverters.find(configFile);
  if (existing != gConverters.end()) {
    return *existing->second;
  }

  auto converter = std::make_unique<opencc::SimpleConverter>(configFile, gResourceProvider);
  opencc::SimpleConverter* result = converter.get();
  gConverters.emplace(configFile, std::move(converter));
  return *result;
}

}  // namespace

extern "C" JNIEXPORT jstring JNICALL
Java_io_github_supermonster003_autojs6_plugin_opencc_nativebridge_OpenccNativeEngine_nativeConvert(
    JNIEnv* env,
    jclass,
    jstring text,
    jstring configFile,
    jstring resourceArchivePath) {
  if (text == nullptr || configFile == nullptr || resourceArchivePath == nullptr) {
    ThrowJavaException(env, "java/lang/NullPointerException", "OpenCC native arguments must not be null");
    return nullptr;
  }

  std::string input;
  std::string config;
  std::string archivePath;
  if (!JavaStringToUtf8(env, text, input)
      || !JavaStringToUtf8(env, configFile, config)
      || !JavaStringToUtf8(env, resourceArchivePath, archivePath)) {
    return nullptr;
  }

  if (!IsAllowedConfig(config)) {
    ThrowJavaException(
        env,
        "java/lang/IllegalArgumentException",
        "Unsupported OpenCC configuration: " + config);
    return nullptr;
  }
  if (archivePath.empty()) {
    ThrowJavaException(env, "java/lang/IllegalStateException", "OpenCC resource archive path is empty");
    return nullptr;
  }

  try {
    std::string converted;
    {
      std::lock_guard<std::mutex> lock(gConverterMutex);
      converted = GetConverterLocked(config, archivePath).Convert(input);
    }
    jstring result = Utf8ToJavaString(env, converted);
    if (result == nullptr && !env->ExceptionCheck()) {
      ThrowJavaException(
          env,
          "java/lang/IllegalStateException",
          "Converted OpenCC text exceeds the JNI string limit");
    }
    return result;
  } catch (const std::exception& error) {
    ThrowJavaException(
        env,
        "java/lang/IllegalStateException",
        std::string("OpenCC ") + OPENCC_PINNED_VERSION + " conversion failed: " + error.what());
    return nullptr;
  } catch (...) {
    ThrowJavaException(
        env,
        "java/lang/IllegalStateException",
        std::string("OpenCC ") + OPENCC_PINNED_VERSION + " conversion failed with an unknown native error");
    return nullptr;
  }
}

extern "C" JNIEXPORT void JNICALL
Java_io_github_supermonster003_autojs6_plugin_opencc_nativebridge_OpenccNativeEngine_nativeClearCache(
    JNIEnv*,
    jclass) {
  std::lock_guard<std::mutex> lock(gConverterMutex);
  gConverters.clear();
  gResourceProvider.reset();
  gResourceArchivePath.clear();
}
