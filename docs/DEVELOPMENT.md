# 개발 환경

## 구조

```text
roadfm/
├─ apk/            빌드된 차량 앱 APK
├─ apps/
│  └─ vehicle/     차량 앱 (Kotlin · Jetpack Compose, 패키지 com.roadfm.car)
├─ backend/        Spring Boot 3.5 · Java 21 (패키지 com.roadfm.api)
├─ database/       PostgreSQL + PostGIS (docker-compose)
├─ docs/           문서
├─ prototypes/     UX 프로토타입 (HTML)
└─ tools/          관광지 데이터 수집 스크립트 (TourAPI)
```

## 차량 앱 빌드

요구사항: Android Studio, JDK 17, Pleos Connect 에뮬레이터

```powershell
cd apps/vehicle
./gradlew assembleDebug      # 개발용
./gradlew assembleRelease    # 배포용 (서명 키 필요)
```

release 빌드는 서명 정보를 `apps/vehicle/keystore.properties` 또는 환경변수(`ROADFM_KEYSTORE_FILE`, `ROADFM_KEYSTORE_PASSWORD`, `ROADFM_KEY_ALIAS`, `ROADFM_KEY_PASSWORD`)에서 읽습니다. 형식은 `apps/vehicle/keystore.properties.example`을 참고하세요.

## 백엔드와 DB

```powershell
copy .env.example .env

docker compose --env-file .env -f database/docker-compose.yml up -d

cd backend
./gradlew bootRun            # DB 없이 실행: --args="--spring.profiles.active=nodb"
```

- 에뮬레이터에서 백엔드 주소는 `http://10.0.2.2:8080/`입니다.
- DB 스키마는 `backend/src/main/resources/db/migration`(Flyway)에 `V1__xxx.sql` 형식으로 추가합니다.

## 보안

- 비밀번호와 API 키는 `.env` 또는 환경변수로만 관리합니다.
- 외부 API 키는 백엔드에만 두고 앱에 포함하지 않습니다.
- 서명 키(`*.jks`, `keystore.properties`)와 실사용자 위치 데이터는 저장소에 올리지 않습니다.
