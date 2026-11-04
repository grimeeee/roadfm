# database/init

PostGIS 컨테이너 최초 기동 시 실행되는 스크립트(`*.sql`, `*.sh`) 위치.

- **스키마는 여기 두지 않는다.** 스키마 변경은 `backend/src/main/resources/db/migration` 의 Flyway 마이그레이션으로만 관리한다.
- 여기에는 확장 설치, 개발용 시드 데이터 등만 둔다.
- 실제 사용자 위치·방문 기록 같은 개인정보 덤프는 절대 커밋하지 않는다.
