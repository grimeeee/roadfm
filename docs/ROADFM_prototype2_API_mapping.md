# prototype2 ↔ 백엔드 API 대조표 (2026-11-11 · 2026-11-12 개정)

- 대상 프로토타입: `prototypes/prototype2/ROADFM_deepgreen.html`
- 대상 API: `ROADFM_master_2026-11-04.md` 7장
- 전제: 프로토타입은 데이터가 HTML에 하드코딩된 UX 시뮬레이션(네트워크 호출 없음). 백엔드는 아직 Controller 미구현. → **실호출 테스트가 아니라 설계 대조**다.
- **2026-11-12 개정:** 기획서 A 방향(오디오 여행 채널, "주행 중엔 귀로, 주차 중엔 눈으로") 반영. 자동 재생 제거(`autoAudio` → `continuousQueue`), 오디오 조회를 `/audio/stories` 리소스로 변경, 재생 서비스용 API·"나중에 보기" 추가. 근거: [`ROADFM_pleos_guide_review_2026-11-12.html`](ROADFM_pleos_guide_review_2026-11-12.html)

## 1. 화면 → API

ROADFM 앱 화면은 모두 **주차(P) 중**에만 쓴다. 주행 중 조작은 차량 미디어 화면·핸들 버튼·Gleo 음성이 재생 서비스(Media3 `MediaLibraryService`)를 통해 처리한다(2장).

| 페이지 | 화면 동작 | 대응 API | 판정 | 비고 |
|---|---|---|---|---|
| 여정 탐색 | 내비 목적지 표시("현대차 내비 · 강릉 · NaviHelper로 받아옴") | — (NaviHelper) | ⚠️ 화면 변경 | **ROADFM은 길 안내·목적지 검색을 하지 않는다.** 기존 목적지 텍스트 검색·마이크 입력 UI 제거(2026-11-12). 시연에서는 "내비 목적지 설정" 칩으로 NaviHelper 수신을 시뮬레이션 |
| 여정 탐색 | ~~목적지 텍스트 검색 / 마이크로 목적지 말하기~~ | ~~`GET /places/search?q=`~~ | 🚫 보류 | 목적지는 현대차 내비에서 받으므로 불필요. 기획서 7장에서도 보류 처리 |
| 여정 탐색 | "어떤 길의 이야기를 들을까요?" 경로 3개(빠른/풍경/문화) + **예상** 소요시간 | `POST /routes/search` | ✅ | 길 안내용이 아니라 **이야기·장소 추천용 예상 경로**(실제 내비 경로와 다를 수 있음). 출발지는 프로토타입에서 "현재 위치(서울)" 고정 → 실제는 NaviHelper 현재 위치 |
| 여정 탐색 | 추천 장소 "내비 경유지로" | — (NaviHelper) | ⚠️ | 서버 API 아님. 현대차 내비에 경유지 추가를 **요청**만 하고 안내는 내비가 함. 주차 중에만 |
| 여정 탐색 | 여행 테마 선택(자연/미식/문화) | `PUT /users/me/preferences` | ✅ | 설정 페이지 테마와 같은 상태 공유 |
| 여정 탐색 | 경로×테마별 추천 장소 3개 | `POST /routes/recommendations` | ✅ | 응답에 장소명·한줄설명·체류시간 필요 |
| 여정 탐색 | 출발하기 | — (NaviHelper) | ⚠️ 화면 수정 | **재생을 시작하지 않는다.** 기존 "출발하기 → 오디오 자동 재생"은 자동 재생 금지 규정 위반 소지 → 출발과 "이야기 듣기"를 분리 |
| 여정 탐색 / 홈 | "이야기 듣기" → 이 길의 이야기 목록 재생 | `GET /audio/stories?routeId=&regionId=&theme=` | ❌→변경 | 기존 `GET /audio?placeId=` 대체. 프로토타입 트랙은 장소가 아닌 **지역/주제 스토리**(예: "강릉 커피가 특별한 이유")라 경로·지역·주제 기준 조회로 변경. 각 항목에 고정 `storyId` 필요 |
| 이야기 | 재생 / 일시정지 / 다음 이야기 | — (재생 서비스) | ⚠️ | 서버 API 아님. Media3 세션 명령. 주행 중에는 이 화면 대신 차량 미디어 화면 사용 |
| ~~음성 가이드~~ | ~~다음 안내 / 다음 경유지 / 남은 시간~~ | — | 🚫 제거 | 길 안내 정보는 현대차 내비 영역이라 ROADFM 화면에서 제거(2026-11-12) |
| ~~음성 가이드~~ | ~~경로 지도 · waveform~~ | — | 🚫 제거 | 주행 중 화면 기준 위반 소지(지도는 Maps/Navigation 카테고리 예시, 움직이는 그래픽 최소화) → 제거(2026-11-12) |
| 이야기 | "이 길의 이야기" 목록 · "나중에 보기" 목록 | `GET /audio/stories`, `GET /saved-places` | ❌→신규 | 2장·3장 참고 |
| 여정 기록 | 방문한 장소 목록·개수 | `GET /visits` | ✅ | |
| 여정 기록 | 스탬프 탭(스탬프북, n/4 진행률, 완료일) | `GET /stamp-books` | ❌→신규 추가 | 스탬프북·소속 장소 테이블 필요(DB 마이그레이션) |
| 설정 | 관심 테마 | `PUT /users/me/preferences` | ✅ | |
| 설정 | 방문 자동 기록 / **이어서 듣기** 토글 | `PUT /users/me/preferences` 확장 | ❌→제안 | 본문에 `autoRecord`, `continuousQueue` 추가 제안(**기본값 false**). 기존 `autoAudio`("오디오 자동 재생", 기본 ON)는 폐기. 로컬 저장만으로 충분하면 API 불필요 |

## 2. 재생 서비스 → API (화면 없이 호출)

차량 미디어 화면·핸들 버튼·Gleo 음성 요청을 Media3 `MediaLibraryService` 콜백이 받아 호출한다. Pleos Music/Audio 가이드 필수 요건(미디어 ID 기반 재생, 검색 기반 재생, 브라우즈) 대응.

| 재생 서비스 동작 | 대응 API | 판정 | 비고 |
|---|---|---|---|
| 브라우즈 루트 / 폴더 목록 (`onGetLibraryRoot`, `onGetChildren`) | `GET /audio/stories?routeId=&regionId=&theme=` | ❌→변경 | 폴더: 이 길의 이야기 / 지역별 / 주제별 / 최근 들은 이야기. 단일 혼합 리스트 금지 |
| 미디어 ID로 재생 (`onGetItem`, `onAddMediaItems`) | `GET /audio/stories/{storyId}` | ❌→신규 추가 | `mediaId = "story:{storyId}"`. 응답에 음원 URL·제목·지역명·길이·아트워크 필요 |
| 검색으로 재생 (`onSearch`, `onGetSearchResult`) — "강릉 이야기 틀어줘" | `GET /audio/stories/search?q=` | ❌→신규 추가 | 핸들 키·Gleo 음성 검색 공용. 지역명·장소명·주제 키워드 검색 |
| 이어서 듣기 — 다음 지역 이야기 큐 추가 | `GET /audio/stories?regionId=` | ❌→변경 | `PLAYING` 상태이고 `continuousQueue=true`일 때만 호출. 중복 재생 제외 |
| 최근 들은 이야기 | — (로컬) | ⚠️ 결정 필요 | 로컬 저장으로 시작, 모바일 연동 시 서버 이전 검토 |

## 3. API → 화면 (화면에 없는 API)

| API | 상태 | 판단 |
|---|---|---|
| `GET /places/{placeId}` | 장소 상세 화면 없음 | 추천 장소 탭 시 상세 시트 추가 or 2차 범위로 이동. "나중에 보기" 장소 상세에도 사용 |
| `POST/GET/DELETE /saved-places` | **(신규 제안)** 화면 없음 | 주행 중 오디오로 들은 추천을 "나중에 보기"에 담고 주차 중 확인. 홈에 "나중에 보기" 목록 추가 필요. 주행 중 음성 저장은 Pleos 확인 후 |
| `POST /visits` | 화면 트리거 없음 | 정상 — 백그라운드 체류 추정(6-6)에서 호출. 재생 서비스와 분리된 컴포넌트 |
| `PATCH /visits/{id}`, `DELETE /visits/{id}` | 수정·삭제 UI 없음 | 기획서는 "사용자가 확인/수정/삭제 가능"이라 명시 → UI 추가하거나 기획서 문구 조정 |
| `POST /audio/jobs` | 관리자용 | 정상 |

## 4. 후속 작업

- [ ] 신규·변경 API 요청/응답 JSON 예시 작성: `/stamp-books`, `/audio/stories`(목록·단건·검색), `/saved-places` (`/places/search`는 보류)
- [x] ~~목적지 검색 UI 유지 여부~~ → 제거. 목적지는 현대차 내비에서 NaviHelper로 수신(2026-11-12)
- [x] ~~`/audio` 조회 기준(장소 vs 지역/경로) 결정~~ → 경로·지역·주제 기준 `/audio/stories` + 고정 `storyId`로 결정(2026-11-12)
- [ ] `audio_content`에 고정 `story_id`, `saved_place` 테이블 Flyway 마이그레이션 설계
- [x] prototype2 수정: 출발과 재생 분리, "이어서 듣기"(기본 OFF), 오디오 화면 지도·waveform 제거, "나중에 보기", 주행 화면 시뮬레이션, 내비 목적지 수신 표시(2026-11-12)
- [ ] 방문 기록 수정/삭제 UI 유무 결정 → 기획서와 일치시키기
- [ ] PDF/DOCX(이전 버전)에 새 화면 캡처 + 갱신된 API 표 반영
- [ ] 백엔드 목업 Controller 작성 후 실호출 테스트(Swagger/curl)
