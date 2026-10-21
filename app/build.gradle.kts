plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.rulesstudy.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.rulesstudy.app"
        minSdk = 24
        targetSdk = 34
        // Every GitHub build gets a higher number, so each update installs over the previous version.
        val run = (System.getenv("GITHUB_RUN_NUMBER") ?: "0").toInt()
        versionCode = 100 + run
        versionName = "5.$run"
    }

    // One permanent key for every build, so each new version installs over the old one (your progress stays).
    signingConfigs {
        create("rulesstudy") {
            storeFile = file("rulesstudy.jks")
            storePassword = "rulesstudy"
            keyAlias = "rulesstudy"
            keyPassword = "rulesstudy"
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("rulesstudy")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
