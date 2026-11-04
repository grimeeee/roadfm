pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        // TODO: Pleos Connect SDK 저장소 — Playground 프로젝트 승인 후 공식 문서 안내대로 추가
    }
}
rootProject.name = "ROADFM"
include(":app")
