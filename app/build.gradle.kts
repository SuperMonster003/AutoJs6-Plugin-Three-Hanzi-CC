import java.util.Properties

plugins {
    id("org.autojs.build.jvm-convention")
    id("com.android.application")
}

var isSignsValid = false

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

    signingConfigs {
        val props = Properties().also { props ->
            File("${project.rootDir}/sign.properties").takeIf { it.exists() }?.let { file ->
                file.inputStream().use { props.load(it) }
                isSignsValid = props.isNotEmpty()
            }
        }
        if (isSignsValid) {
            create("release") {
                storeFile = props["storeFile"]?.let { file(it as String) }
                keyPassword = props["keyPassword"] as String
                keyAlias = props["keyAlias"] as String
                storePassword = props["storePassword"] as String
            }
        }
    }

    buildTypes {
        val niceSigningConfig = takeIf { isSignsValid }?.let {
            signingConfigs.getByName("release")
        }
        debug {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
            niceSigningConfig?.let { signingConfig = it }
        }
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
            niceSigningConfig?.let { signingConfig = it }
        }
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
    implementation(libs.opencc)
}
