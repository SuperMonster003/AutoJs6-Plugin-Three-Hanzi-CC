import java.util.*

plugins {
    id("org.autojs.build.utils")
    id("org.autojs.build.versions")
    id("org.autojs.build.signs")
    id("org.autojs.build.jvm-convention")
    id("com.android.application")
}

val globalApplicationId = "io.github.supermonster003.autojs6.plugin.opencc"

var isSignsValid = false

android {
    namespace = globalApplicationId
    compileSdk = versions.sdkVersionCompile

    defaultConfig {
        applicationId = globalApplicationId

        minSdk = versions.sdkVersionMin
        targetSdk = versions.sdkVersionTarget

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        versionCode = versions.appVersionCode
        versionName = versions.appVersionName

        resValue("string", "app_name", "OpenCC")
        resValue("string", "plugin_author", "SuperMonster003")
        resValue("string", "plugin_id", "opencc")
        resValue("string", "plugin_engine", "opencc")
        resValue("string", "plugin_variant", "default")
        resValue("string", "plugin_version_date", utils.getDateString("MMM d, yyyy", "GMT+08:00"))
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

    splits {
        abi {
            isEnable = true
            reset()
            include("arm64-v8a", "armeabi-v7a", "x86_64", "x86")
            isUniversalApk = true
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
    implementation(files("$rootDir/libs/common-plugin-api.aar"))
    implementation(files("$rootDir/libs/opencc-api.aar"))
    implementation(libs.opencc)

    testImplementation(libs.junit)
    androidTestImplementation(libs.test.ext.junit)
    androidTestImplementation(libs.test.runner)
}

tasks {
    withType(JavaCompile::class.java) {
        options.encoding = "UTF-8"
    }

    register<Copy>("appendDigestToReleasedFiles") {
        description = "Appends CRC32 digest to released APK files"

        val ext = utils.FILE_EXTENSION_APK
        val src = layout.buildDirectory.dir("outputs/apk/release")
        val dst = layout.projectDirectory.dir("releases")
        val expectedInputFiles = setOf(
            "app-arm64-v8a-release.$ext",
            "app-armeabi-v7a-release.$ext",
            "app-universal-release.$ext",
            "app-x86_64-release.$ext",
            "app-x86-release.$ext",
        )

        dependsOn("assembleRelease")
        inputs.property("versionName", versions.appVersionName)

        doFirst {
            check(isSignsValid) {
                "Release signing configuration is missing or incomplete; refusing to collect unsigned APKs"
            }
            val actualInputFiles = src.get().asFile.listFiles { file ->
                file.isFile && file.extension == ext
            }.orEmpty().mapTo(mutableSetOf()) { it.name }
            check(actualInputFiles == expectedInputFiles) {
                "Expected exactly ${expectedInputFiles.sorted()}, but found ${actualInputFiles.sorted()}"
            }
        }

        from(src)
        into(dst)
        include("*.$ext")

        rename { name ->
            val abi = name.replace(Regex("^app-(.+?)-release(\\.$ext)$"), "$1")
            val releasedFileNamePrefix = "${rootProject.name}-v${versions.appVersionName}-$abi"
            utils.digestCRC32(src.get().file(name).asFile).let { digest ->
                "$releasedFileNamePrefix-$digest.$ext"
            }
        }

        doLast { println("Destination: ${dst.asFile}") }
    }
}
