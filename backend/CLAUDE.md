# Backend 모듈 가이드

## 🎯 해당 모듈의 책임 범위
- 구성기학(九星気学)·수비술(Numerology)·파워스톤 추천 등 비즈니스 로직 계산 및 데이터베이스 CRUD 처리.
- 사용자 인증(Authentication/Authorization), JWT 발급 등 세션 및 권한 관리.
- 클라이언트(프론트엔드)에서 접근 가능한 RESTful API 엔드포인트 제공.

## 📂 주요 파일별 역할
- `app.py`: Flask 애플리케이션의 엔트리포인트. 미들웨어 설정 및 최상위 Blueprint/Router 연결.
- `core/`: 애플리케이션 전반에 적용되는 설정(`config.py`), 데이터베이스 세션 관리(`database.py`, `db_config.py`), 예외 처리(`exceptions.py`), 유틸리티 등을 포함.
- `apps/reading/`: 도메인 기반으로 분리된 기능 모듈. 3개 서브도메인 + 공통 모듈.
  - `apps/reading/ninestarki/`: 구성기학(九星気学) 도메인 — 방위 길흉·연월반 계산, 운세.
    - `domain/`: 핵심 비즈니스 객체 및 레포지토리 인터페이스.
    - `infrastructure/`: 레포지토리 구현 및 DB 연동.
    - `use_cases/`: 애플리케이션 서비스 로직 (비즈니스 흐름 제어).
    - `routes/`: API 엔드포인트 (Flask Blueprint).
    - `utils/`: 날짜·간지·시간 포맷터 등 헬퍼 함수.
    - `templates/`: HTML 템플릿 (PDF용).
  - `apps/reading/numerology/`: 수비술(Numerology) 도메인 — Life Path Number 기반 파워스톤.
    - `domain/`, `infrastructure/`, `data/`
  - `apps/reading/powerstone/`: 파워스톤 추천 도메인 — 6-레이어 추천 엔진.
    - `domain/`, `infrastructure/`, `use_cases/`, `data/`
  - `apps/reading/shared/`: 공통 모듈 — user, permission, 예외(exceptions.py), 상수(constants.py).
    - `domain/`, `infrastructure/`, `use_cases/`
  - `apps/reading/dependency_module.py`: Flask-Injector 기반 DI 컨테이너 설정 (서브도메인별 섹션으로 구성).
- `db_manage.py`: 데이터베이스 초기화(init) 및 리셋(reset) 등을 수행하기 위한 유틸리티 스크립트.

## 📦 외부 의존성
- **Flask**: 웹 프레임워크.
- **Flask-Injector**: 의존성 주입 (Clean Architecture DI 컨테이너).
- **SQLAlchemy (Core / ORM)**: 데이터베이스 ORM 및 쿼리 빌더.
- **PyMySQL**: MySQL 드라이버.
- **Flask-JWT-Extended**: JWT 토큰 발급 및 검증.
- **Pydantic**: 데이터 검증 및 API 스키마 정의.

## ⚠️ 수정 시 주의사항
1. **Clean Architecture 준수**: `use_cases`나 `domain` 레이어에 `Flask`나 `SQLAlchemy` 같은 특정 인프라 코드가 직접적으로 침투하지 않도록 유의하세요.
2. **서브도메인 독립성**: `ninestarki`, `numerology`, `powerstone` 각 서브도메인은 서로 직접 import하지 않고, `dependency_module.py`를 통해 연결됩니다.
3. **DB 스키마 변경**: 모델을 변경할 경우, 데이터베이스의 마이그레이션 전략이나 초기화 SQL(`mysql/init/`)을 함께 고려하세요. (현재 ORM 변경과 별개로 순수 SQL로 테이블이 생성되는 구조입니다).
4. **환경에 따른 설정 분리**: 개발 환경에서만 동작하는 로직이 프로덕션 환경에 포함되지 않도록 `core/config.py`의 `BaseConfig`, `DevelopmentConfig`, `ProductionConfig`의 구조를 잘 활용하세요.
