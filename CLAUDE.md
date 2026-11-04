# ROADFM — 작업 가이드

- 기획 기준 문서: `docs/ROADFM_master_2026-11-04.md`. 기능 ID(F-01~F-06)·우선순위(P0~P2)는 이 문서를 따른다.
- `apps/vehicle/`(Kotlin/Compose, 패키지 `com.roadfm.car`)와 `backend/`(Spring Boot, 패키지 `com.roadfm.api`)는 각각 독립 Gradle 빌드다. `apps/mobile/`은 향후(Vue+Capacitor).
- DB 스키마는 `backend/src/main/resources/db/migration`(Flyway)에서만 변경. `database/`는 compose·init 스크립트용.
- Pleos SDK API 시그니처를 추측해서 쓰지 않는다. 공식 문서 확인 후 연동.
- 민감정보(비밀번호·API 키·서명 키·실사용자 위치 데이터)는 커밋하지 않는다. 설정에 기본값으로도 넣지 않고 `.env`/환경변수로만.
- 빌드 확인: `apps/vehicle/gradlew assembleDebug`, `backend/gradlew build`.
