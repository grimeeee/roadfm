# ROADFM (로디엠)

> 지나가는 길마다, 새로운 이야기가 흐르다.

Pleos Connect 차량용 앱 기반 위치 기반 관광 오디오 가이드 서비스. 현대자동차그룹 차량용 앱 개발 공모전 출품작.
기획 마스터 문서: [`docs/ROADFM_master_2026-11-04.md`](docs/ROADFM_master_2026-11-04.md)

## 구조

```text
roadfm/
├─ apps/
│  ├─ vehicle/     🚗 차량 앱 (Kotlin · Jetpack Compose)  — 패키지 com.roadfm.car
│  └─ mobile/      📱 모바일 앱 (Vue 3 + Capacitor, 향후)
├─ backend/        Spring Boot 3.5 · Java 21               — 패키지 com.roadfm.api
├─ database/       PostgreSQL + PostGIS (docker-compose, init 스크립트)
├─ docs/           기획서 · API 문서
├─ prototypes/     디자인 프로토타입
└─ .env.example    비밀값 템플릿 (실제 값은 .env — 커밋 금지)
```

## 시작하기

```powershell
copy .env.example .env      # 값 채우기

# DB
docker compose --env-file .env -f database/docker-compose.yml up -d

# 백엔드  (DB 없이 띄우려면 --args="--spring.profiles.active=nodb")
cd backend; ./gradlew bootRun

# 차량 앱
cd apps/vehicle; ./gradlew assembleDebug
```

- 차량 앱은 Android Studio 로 `apps/vehicle/` 을 열어도 된다. 에뮬레이터에서 백엔드 주소는 `http://10.0.2.2:8080/`.
- DB 스키마는 `backend/src/main/resources/db/migration` (Flyway) 에 `V1__xxx.sql` 형식으로 추가한다.

## 보안 원칙

- 비밀번호·API 키는 **루트 `.env` 또는 환경변수**로만. 설정 파일에 기본값으로도 넣지 않는다.
- 외부 API 키는 **백엔드에만**. 차량/모바일 앱 번들에 넣지 않는다.
- 서명 키(`*.jks`, `keystore.properties`), 실사용자 위치·방문 데이터 덤프는 커밋 금지.
