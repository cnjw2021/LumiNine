# Backend 모듈 가이드

## 🎯 해당 모듈의 책임 범위
- 비즈니스 로직(九星気学 - 구성기학) 계산 및 관련 데이터베이스 CRUD 처리.
- 사용자 인증(Authentication/Authorization), JWT 발급 등 세션 및 권한 관리.
- Redis를 활용한 비동기 작업(Task Queue, ex: PDF 혹은 이미지 생성) 처리.
- 클라이언트(프론트엔드)에서 접근 가능한 RESTful API 엔드포인트 제공.

## 📂 주요 파일별 역할
- `app.py`: FastAPI 애플리케이션의 엔트리포인트. 미들웨어 설정 및 최상위 Router 연결.
- `core/`: 애플리케이션 전반에 적용되는 설정(`config.py`), 데이터베이스 세션 관리(`database.py`), 예외 처리(`exceptions.py`), 유틸리티 등을 포함.
- `apps/`: 도메인 기반으로 분리된 기능 모듈. `apps/reading/` 하위에 3개 서브도메인과 공통 모듈이 있음.
  - `apps/reading/ninestarki/`: 구성기학(九星気学) 도메인 — 방위 길흉·연월반 계산.
  - `apps/reading/numerology/`: 수비술(Numerology) 도메인 — Life Path Number 기반 파워스톤.
  - `apps/reading/powerstone/`: 파워스톤 추천 도메인 — 6-레이어 추천 엔진.
  - `apps/reading/shared/`: 공통 모듈 — user, permission, 예외(exceptions.py), 상수(constants.py).
- `db_manage.py`: 데이터베이스 초기화(init) 및 리셋(reset) 등을 수행하기 위한 유틸리티 스크립트.

## 📦 외부 의존성
- **FastAPI**: 웹 프레임워크.
- **SQLAlchemy (Core / ORM)**: 데이터베이스 ORM 및 쿼리 빌더.
- **PyMySQL**: MySQL 드라이버.
- **Redis / RQ**: 비동기 워커 처리를 위함.
- **Pydantic**: 데이터 검증 및 API 스키마 정의.

## ⚠️ 수정 시 주의사항
1. **Clean Architecture 준수**: `use_cases` 나 `domain` 레이어에 `FastAPI`나 `SQLAlchemy` 같은 특정 인프라 코드가 직접적으로 침투하지 않도록 유의하세요.
2. **DB 스키마 변경**: 모델을 변경할 경우, 데이터베이스의 마이그레이션 전략이나 초기화 SQL(`mysql/init/`)을 함께 고려하세요. (현재 ORM 변경과 별개로 순수 SQL로 테이블이 생성되는 구조입니다).
3. **환경에 따른 설정 분리**: 개발 환경에서만 동작하는 로직이 본번 환경에 포함되지 않도록 `core/config.py`의 `BaseConfig`, `DevelopmentConfig`, `ProductionConfig`의 구조를 잘 활용하세요.

## 🚀 향후 확장 계획 (Upcoming Extensions)
- **월반(月盤) 길흉방위 판별 로직 추가**: 연단위 방위 판별 로직을 확장하여 절입일 기준 월단위 길흉방위 판별 기능 개발.
- **파워스톤 매칭 시스템**: 본명성(기본석), 월운석, 호신석으로 이루어진 3-Layer 파워스톤 추천 로직 적용.
- **상세 설계서 참조**: 위 두 기능의 알고리즘 및 오행 상생상극 매칭 규칙은 [월단위 길방위 및 파워스톤 매칭 설계서](../docs/monthly-direction-with-powerstone.md) 문서를 참고하여 구현할 예정입니다.
