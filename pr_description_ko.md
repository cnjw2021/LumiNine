# PR #82: 백엔드 및 프런트엔드 불필요 코드 및 데이터 정리 (Phase 4 & 6)

## 개요
이 PR은 LumiNine 애플리케이션의 최적화를 위해 더 이상 사용되지 않는 백엔드의 관리자 API, CSV 데이터 파일 및 관련 로직을 제거하고, 이에 대응하는 프런트엔드의 불필요한 코드(API 호출, 타입 정의 등)를 정리한 결과물입니다.

## 주요 변경 사항

### 1. 백엔드 정리 및 스키마 최적화 (Phase 4, 8 & 9)
- **추가 스크립트 삭제 (Phase 9)**:
  - `backend/scripts/fortune_direction_year.py`: 연반 기준 방위 계산을 수행하던 레거시 독립형 스크립트 삭제. 현재는 `StarGridPattern` 모델 및 도메인 서비스를 통해 통합 관리되고 있습니다.
- **추가 테이블 및 모델 삭제 (Phase 8)**:
  - `moving_auspicious_dates`, `compatibility_symbol_pattern_master`, `compatibility_symbol_master`, `compatibility_readings_master` 테이블 및 관련 모델(`backend/core/models/`) 삭제.
  - `backend/scripts/generate_compatibility_readings.py` (데이터 생성 스크립트) 삭제.
- **기존 정리 내용**:
  - `core/admin/routes.py`: 사용되지 않는 관리자 전용 라우트 삭제.
  - `data/csv/` 내의 레거시 CSV 데이터 파일 삭제.
  - `db_manage.py`, `csv_file_loader.py`, `000_create_tables.sql` 등에서 위 테이블 및 파일에 대한 모든 참조 제거.

### 2. 프런트엔드 정리 (Phase 6)
- **데드 코드 제거**:
  - `frontend/src/lib/api/nineStarKiApi.ts` 삭제: 더 이상 존재하지 않는 백엔드 API(`/admin/star-fortune-batch`, `/nine-star/combination-fortune` 등)를 참조하던 파일 전체 제거
- **정합성 확인**:
  - `NineStarKiForm.tsx` 및 결과 관련 훅(`useMonthFortuneData`, `usePdfReport`)이 현재 활성화된 백엔드 엔드포인트를 올바르게 사용하는지 확인
  - `star_life_guidance`, `main_star_acquired_fortune_message`, `preview-report` 등에 대한 잔존 참조가 없음을 전체 스캔을 통해 확인
  - 관리자 대시보드가 현재 유효한 '사용자 관리' 기능에만 집중하도록 유지

## 검증 결과
- **백엔드**: `make test-unit` 실행 결과, 총 338개의 유닛 테스트가 모두 성공적으로 통과되었습니다.
- **프런트엔드**: 빌드 및 주요 페이지(결과 페이지, 관리자 페이지)의 API 연동 정합성을 확인했습니다.
