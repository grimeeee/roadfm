# collect_places — 시연용 관광지 데이터 수집

서울 → 강릉 3개 경로(빠른 길 / 풍경 좋은 길 / 문화가 깃든 길) 주변 관광지를
TourAPI(KorService2)·오디(Odii)에서 모아 `output/places_seoul_gangneung.json` 으로 저장한다.

## 사전 준비
공공데이터포털 활용신청(승인) 필요:
- 한국관광공사_국문 관광정보 서비스 (`KorService2`)
- 한국관광공사_관광지 오디오 가이드정보 (`Odii`) — 없으면 `--no-odii`

## 실행 (repo 루트에서)
```powershell
python -I tools/collect_places/collect_places.py --dry-run   # 호출 수만 미리 확인
python -I tools/collect_places/collect_places.py             # 인증키 입력 프롬프트
```
- 인증키는 실행 시 입력하거나 환경변수 `TOUR_API_KEY` 로. **파일에 저장하지 않는다.**
- Encoding/Decoding 키 둘 다 가능 (`%` 포함 여부로 자동 판별).
- 응답은 `.cache/` 에 저장 → 중간에 끊겨도 다시 실행하면 이어서 진행, 트래픽 절약.

## 결과 항목 (places[])
| 필드 | 설명 |
|---|---|
| `guideShort` | 짧은 안내 문장 (관광지명 + 개요 첫 문장 + 주차/휴무) |
| `summary` / `overview` | 개요 첫 문장 / 개요 전체 |
| `usetime`, `restdate`, `parking`, `fee` | 소개정보 |
| `routeIds`, `distanceFromRouteM` | 어느 경로 주변인지, 경로와의 거리 |
| `fromPrototype` | 프로토타입에 나오는 장소 여부 |
| `odiiStories` | 500m 이내 오디 이야기(대본·음원) |
| `imageLicense` | 이미지 공공누리 유형 — 사용 전 확인 |

## 조정
스크립트 상단 설정값: `STEP_KM`(조회 간격), `RADIUS_M`(반경), `ROWS_PER_POINT`, `MUST_INCLUDE`(꼭 넣을 장소).
경로 좌표는 경유 도시 기준 근사치 — 추후 외부 길찾기 API 결과로 교체.
