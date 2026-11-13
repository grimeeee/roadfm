# ROADFM (로디엠)

> 지나가는 길마다, 새로운 이야기가 흐르다.

**현대자동차그룹 차량용 앱 개발 공모전 출품작** · Pleos Connect 차량용 앱

ROADFM은 지나가는 지역의 이야기를 들려주는 **위치 기반 오디오 여행 채널**입니다.
길 안내는 현대차 내비가, 이야기는 ROADFM이 맡습니다. **주행 중에는 귀로, 주차 중에는 눈으로** 이용합니다.

- 시연 영상: _(링크 추가 예정)_
- 기획 문서: [`docs/ROADFM_master_2026-11-04.md`](docs/ROADFM_master_2026-11-04.md)
- Pleos 가이드 점검 보고서: [`docs/ROADFM_pleos_guide_review_2026-11-12.html`](docs/ROADFM_pleos_guide_review_2026-11-12.html)

---

## 구현 범위 (실제 동작 vs 시뮬레이션)

| 구분 | 내용 | 위치 |
|---|---|---|
| **실제 동작** (Pleos 에뮬레이터) | **NaviHelper SDK 연동**: 내비 목적지 조회(`getDestinationInfo`), 목적지 변경 이벤트(`onDestinationChanged`), 경유지 조회·추가·삭제(`getWaypointInfo` / `addWaypoint` / `removeWaypoint`, 최대 2개) | `apps/vehicle` |
| **UX 시뮬레이션** (HTML) | 사용자 흐름 전체: 취향 선택 → 내비 목적지 연동 → 사용자가 시작하는 재생 → 내비 안내 시 일시정지·재개 → 음성 경유지 추가 → 여정 기록·스탬프 | `prototypes/prototype2/ROADFM_prototype_final.html` |
| **개발 예정** | Media3 `MediaLibraryService` 재생, 오디오 포커스 처리, 지역 이야기 API(백엔드), 방문 기록 | `apps/vehicle`, `backend` |

> 현재 차량 앱 APK의 화면은 **NaviHelper 연동 검증용 개발 화면**이며, 서비스 UI는 HTML 프로토타입으로 시연합니다.

---

## 핵심 기능

| ID | 기능 | 설명 |
|---|---|---|
| F-01 | 내비 목적지 연동 | 현대차 내비에 입력한 목적지를 받아 경로 주변 이야기를 준비. ROADFM에 목적지를 다시 입력하지 않음 |
| F-02 | 지역 이야기 재생 | 사용자가 핸들 버튼·음성·화면으로 시작할 때만 재생. 내비 음성 안내 중에는 잠시 멈춤 |
| F-03 | 경로 주변 장소 · 경유지 | 주차 중 추천 장소 확인, 내비 경유지 추가(최대 2개) |
| F-04 | 여정 기록 | 동의한 경우에만 방문 장소 기록 |
| F-05 | 스탬프 | 테마별 방문 스탬프 (주차 중 확인) |

## Pleos 가이드 반영

- **자동 재생 금지**: 목적지를 받아도 준비만 하고, 재생은 사용자의 명시적 동작으로만 시작. "이어서 듣기"는 기본 OFF
- **주행 중 최소 UI**: 주행 중에는 제목·지역·진행·재생 컨트롤만 표시. 탐색·설정·기록은 주차(P) 상태에서만 제공
- **운전 관련 오디오 우선**: 내비 안내가 나오면 이야기를 일시정지하고, 안내가 끝나면 재개
- **텍스트 입력 최소화**: 목적지는 내비에서 받아오고, 주행 중 조작은 음성과 미디어 버튼으로

자세한 내용은 [가이드 점검 보고서](docs/ROADFM_pleos_guide_review_2026-11-12.html)에 정리했습니다.

---

## 시연 방법

### 1. UX 프로토타입 (브라우저)

`prototypes/prototype2/ROADFM_prototype_final.html`을 브라우저로 엽니다. 장면이 자동으로 재생됩니다.

| 조작 | 동작 |
|---|---|
| `Space` | 일시정지 / 재생 |
| `←` `→` | 이전 / 다음 장면 |
| 우하단 `화면:` 버튼 | Connect-S / Connect-W 레이아웃 전환 |
| `?scene=7&frame=2&still` | 특정 장면 정지 화면으로 열기 |

### 2. 차량 앱 (Pleos Connect 에뮬레이터)

**요구사항**: Android Studio, JDK 17, [Pleos Connect 에뮬레이터](https://document.pleos.ai/docs/pleos-only/getting-started)

빌드된 release APK는 [`apk/`](apk/) 폴더에 있습니다.

```powershell
adb install -r apk/roadfm-release.apk
```

직접 빌드하는 경우:

```powershell
cd apps/vehicle
./gradlew assembleRelease
# 산출물: app/build/outputs/apk/release/app-release.apk
```

release 빌드에는 서명 키가 필요합니다. `apps/vehicle/keystore.properties.example`을 `keystore.properties`로 복사해 값을 채우거나, 같은 이름의 환경변수(`ROADFM_KEYSTORE_FILE` 등)를 지정합니다. 서명 정보가 없으면 설치할 수 없는 미서명 APK가 만들어집니다. 개발 중에는 `./gradlew assembleDebug`를 사용합니다.

**확인 순서**

1. 에뮬레이터의 내비에서 목적지를 설정하고 길 안내를 시작합니다.
2. ROADFM을 실행하면 화면 왼쪽에 내비 목적지가 표시됩니다.
3. 앱을 켠 채 내비 목적지를 바꾸면 `onDestinationChanged` 로그가 남고 목적지가 갱신됩니다.
4. `예시 경유지 FIRST` / `SECOND` 버튼으로 내비에 경유지를 추가하고, `경유지 모두 제거`로 삭제합니다.

이벤트 로그는 화면 오른쪽과 logcat 태그 `RoadFmNavi`에서 확인할 수 있습니다.

---

## 구조

```text
roadfm/
├─ apps/
│  ├─ vehicle/     차량 앱 (Kotlin · Jetpack Compose) — 패키지 com.roadfm.car
│  │               NaviHelper 연동 구현됨 · 재생 기능 개발 예정
│  └─ mobile/      모바일 앱 (Vue 3 + Capacitor) — 개발 예정
├─ backend/        Spring Boot 3.5 · Java 21 — 패키지 com.roadfm.api (개발 예정)
├─ database/       PostgreSQL + PostGIS (docker-compose, init 스크립트)
├─ docs/           기획서 · Pleos 가이드 점검 · API 매핑 · Postman 컬렉션
├─ prototypes/     UX 프로토타입 (HTML)
├─ tools/          관광지·오디오 콘텐츠 수집 스크립트 (TourAPI)
└─ .env.example    비밀값 템플릿 (실제 값은 .env — 커밋 금지)
```

## 기술 스택

| 영역 | 사용 기술 |
|---|---|
| 차량 앱 | Kotlin, Jetpack Compose, **Pleos Connect NaviHelper SDK 3.0.5** (minSdk 29 / targetSdk 35) |
| 재생 (예정) | AndroidX Media3 (`MediaLibraryService`, ExoPlayer) |
| 백엔드 (예정) | Spring Boot 3.5, Java 21, PostgreSQL + PostGIS, Flyway |
| 콘텐츠 | 한국관광공사 TourAPI |

## 개발 환경 실행

```powershell
copy .env.example .env      # 값 채우기

# DB
docker compose --env-file .env -f database/docker-compose.yml up -d

# 백엔드  (DB 없이 띄우려면 --args="--spring.profiles.active=nodb")
cd backend; ./gradlew bootRun

# 차량 앱
cd apps/vehicle; ./gradlew assembleDebug
```

- 차량 앱은 Android Studio로 `apps/vehicle/`을 열어도 됩니다. 에뮬레이터에서 백엔드 주소는 `http://10.0.2.2:8080/`입니다.
- DB 스키마는 `backend/src/main/resources/db/migration`(Flyway)에 `V1__xxx.sql` 형식으로 추가합니다.

## 보안 원칙

- 비밀번호·API 키는 **루트 `.env` 또는 환경변수**로만 관리합니다. 설정 파일에 기본값으로도 넣지 않습니다.
- 외부 API 키는 **백엔드에만** 둡니다. 차량/모바일 앱 번들에 넣지 않습니다.
- 서명 키(`*.jks`, `keystore.properties`), 실사용자 위치·방문 데이터 덤프는 커밋하지 않습니다.
