import java.util.Properties

plugins {
    id("org.autojs.build.versions")
    id("org.autojs.build.jvm-convention")
    id("com.android.library")
}

val upstream = Properties().apply {
    rootProject.file("opencc-upstream.properties").inputStream().use(::load)
}

fun upstreamProperty(name: String): String = requireNotNull(upstream.getProperty(name)) {
    "Missing $name in opencc-upstream.properties"
}

fun quotedBuildConfigValue(value: String): String = "\"${value.replace("\\", "\\\\").replace("\"", "\\\"")}\""

android {
    namespace = "io.github.supermonster003.autojs6.plugin.opencc.nativebridge"
    compileSdk = versions.sdkVersionCompile
    ndkVersion = "28.2.13676358"

    defaultConfig {
        minSdk = versions.sdkVersionMin
        consumerProguardFiles("consumer-rules.pro")

        buildConfigField(
            "String",
            "OPENCC_VERSION",
            quotedBuildConfigValue(upstreamProperty("OPENCC_VERSION")),
        )
        buildConfigField(
            "String",
            "OPENCC_TAG",
            quotedBuildConfigValue(upstreamProperty("OPENCC_TAG")),
        )
        buildConfigField(
            "String",
            "OPENCC_COMMIT",
            quotedBuildConfigValue(upstreamProperty("OPENCC_COMMIT")),
        )
        buildConfigField(
            "String",
            "OPENCC_RESOURCE_ASSET",
            quotedBuildConfigValue(upstreamProperty("OPENCC_RESOURCE_ASSET")),
        )
        buildConfigField(
            "String",
            "OPENCC_RESOURCE_ASSET_PATH",
            quotedBuildConfigValue("opencc/${upstreamProperty("OPENCC_RESOURCE_ASSET")}"),
        )
        buildConfigField(
            "String",
            "OPENCC_RESOURCE_SHA256",
            quotedBuildConfigValue(upstreamProperty("OPENCC_RESOURCE_SHA256")),
        )
        buildConfigField(
            "long",
            "OPENCC_RESOURCE_SIZE",
            "${upstreamProperty("OPENCC_RESOURCE_SIZE")}L",
        )

        externalNativeBuild {
            cmake {
                arguments += listOf(
                    "-DANDROID_STL=c++_static",
                    "-DOPENCC_PINNED_VERSION=${upstreamProperty("OPENCC_VERSION")}",
                    "-DOPENCC_PINNED_COMMIT=${upstreamProperty("OPENCC_COMMIT")}",
                )
                cppFlags += listOf("-std=c++17", "-fexceptions", "-frtti")
            }
        }
    }

    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
            version = "3.22.1"
        }
    }

    buildFeatures {
        buildConfig = true
    }
}

val verifyOpenccUpstream by tasks.registering(Exec::class) {
    group = "verification"
    description = "Verifies the pinned OpenCC source and official resource bundle"
    workingDir = rootProject.projectDir
    commandLine(
        "python",
        "scripts/opencc/verify_upstream.py",
        "--root",
        rootProject.projectDir.absolutePath,
    )
}

tasks.named("preBuild").configure {
    dependsOn(verifyOpenccUpstream)
}
