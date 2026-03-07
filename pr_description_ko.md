# PR #82: 백엔드 및 프런트엔드 불필요 코드 및 데이터 정리 (Phase 4 & 6)

## 개요
이 PR은 LumiNine 애플리케이션의 최적화를 위해 더 이상 사용되지 않는 백엔드의 관리자 API, CSV 데이터 파일 및 관련 로직을 제거하고, 이에 대응하는 프런트엔드의 불필요한 코드(API 호출, 타입 정의 등)를 정리한 결과물입니다.

## 주요 변경 사항

### 1. 백엔드 정리 (Phase 4)
- **파일 삭제**:
  - `core/admin/routes.py`: 사용되지 않는 관리자 전용 라우트 삭제
  - `data/csv/star_life_guidance.csv`, `main_star_acquired_fortune_message.csv`: 레거시 데이터 파일 삭제
  - `core/models/main_star_acquired_fortune_message.py`: 삭제된 데이터에 대응하는 모델 삭제
  - `apps/ninestarki/__init__.py`: 레거시 앱 엔트리 포인트 삭제
- **코드 리팩토링**:
  - `backend/app.py`: 인덱스(`/`) 응답에서 삭제된 관리자 엔드포인트 제거
  - `backend/db_manage.py`: `_EXPECTED_TABLES`에서 삭제된 테이블 제외
  - `backend/scripts/csv_file_loader.py`: 삭제된 CSV 파일 로딩 로직 제거
  - `mysql/init/000_create_tables.sql`: 불필요한 테이블 생성 구문 제거

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
