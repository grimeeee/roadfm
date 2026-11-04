# apps/mobile — 모바일 앱 (향후, F-06)

공모전 필수 산출물이 아니다. 차량 앱 MVP 이후 착수한다.

- 스택 예정: Vue 3 + Vite + Pinia + Vue Router + Capacitor (android / ios)
- 역할: 취향 설정, 여행 기록 보기, 저장 장소 관리
- 차량 ↔ 모바일 동기화는 ROADFM 백엔드 계정 기반 (Pleos 자동 동기화를 가정하지 않음)
- 예정 구조: `src/{assets,components,views,router,stores,services}`, `capacitor.config.ts`, `vite.config.ts`
- API 키를 앱 번들에 넣지 않는다. 모든 외부 API 는 백엔드 경유.
