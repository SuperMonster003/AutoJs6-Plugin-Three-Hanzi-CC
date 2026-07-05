plugins {
    id("org.autojs.build.jvm-convention")
    id("com.android.application")
}

android {
    namespace = "io.github.supermonster003.autojs6.plugin.opencc"
    compileSdk = 36

    defaultConfig {
        applicationId = namespace
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0"

        resValue("string", "app_name", "OpenCC Plugin")
        resValue("string", "plugin_id", "opencc")
        resValue("string", "plugin_engine", "opencc")
        resValue("string", "plugin_variant", "default")
        resValue("string", "plugin_author", "SuperMonster003")
        resValue("string", "plugin_version_date", "Jul 5, 2026")
    }

    buildFeatures {
        aidl = true
        resValues = true
    }

    packaging {
        jniLibs.useLegacyPackaging = true
    }
}

dependencies {
    implementation(files("../../AutoJs6/plugin-api/common-plugin-api/build/outputs/aar/common-plugin-api-debug.aar"))
    implementation(files("../../AutoJs6/plugin-api/opencc-api/build/outputs/aar/opencc-api-debug.aar"))
    implementation("com.github.brooklet:android-opencc:1.2.2")
}
