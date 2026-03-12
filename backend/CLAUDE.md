# Backend 모듈 가이드

> Last updated: 2026-03-12

## 🎯 해당 모듈의 책임 범위
- 구성기학(九星気学)·수비술(Numerology)·파워스톤 추천 등 비즈니스 로직 계산 및 데이터베이스 CRUD 처리.
- 사용자 인증(Authentication/Authorization), JWT 발급, 패스워드 암호화(`bcrypt`) 등 세션 및 권한 관리.
- 클라이언트(프론트엔드)에서 접근 가능한 RESTful API 엔드포인트 제공.
- Cloud Run 배포: `$PORT` 환경변수 바인딩, `GET /api/health` 헬스체크 엔드포인트.
- Alembic 기반 DB 마이그레이션: `flask db upgrade`로 스키마 + 시드 데이터 자동 적용.

## 📂 주요 파일별 역할
- `app.py`: Flask 애플리케이션의 엔트리포인트. 미들웨어 설정, Blueprint 등록, FlaskInjector DI 바인딩, 전역 에러 핸들러, `/api/health` 포함.
- `start.sh`: Cloud Run 전용 Gunicorn 기동 스크립트 (`$PORT` 환경변수 바인딩, cron/logrotate 없음).
- `config.py`: 애플리케이션 설정. `DATABASE_URL`(`postgresql+psycopg2://`) 우선, 개별 환경변수 폴백.
- `wait_for_db.py`: 로컬 개발환경 전용 PostgreSQL 연결 대기 스크립트 (psycopg2 사용).
- `core/`: 설정(`config.py`), DB 세션(`database.py`), DB 설정(`db_config.py`), 예외 처리(`exceptions.py`), 유틸리티.
  - `core/auth/`: 인증 모듈 — `auth_routes.py`(로그인·로그아웃·패스워드변경·유저정보), `admin_user_routes.py`(관리자 유저 CRUD), `admin_system_routes.py`(시스템 설정·계정제한), `token_routes.py`(JWT 토큰 라이프사이클), `debug_routes.py`(헬스체크), `auth_utils.py`(get_current_user 헬퍼·권한 데코레이터), `jwt_helpers.py`(JWT), `permission_routes.py`(권한관리).
  - `core/models/`: SQLAlchemy 모델 정의 — `stars`, `star_attributes`, `star_grid_patterns`, `monthly_directions`, `daily_astrology`, `solar_starts`, `solar_terms`, `powerstone_master`, `recommendation_history`, `hourly_star_zodiacs`, `zodiac_groups`/`zodiac_group_members`, `pattern_switch_dates`, `system_config`, `admin_account_limit`, `star_groups`, `exceptions`.
  - `core/services/`: 공통 서비스 레이어.
  - `core/utils/`: 로거(`logger.py`) 등 유틸리티.
- `apps/reading/`: 도메인 기반으로 분리된 기능 모듈. 3개 서브도메인 + 공통 모듈.
  - `apps/reading/ninestarki/`: 구성기학(九星気学) 도메인 — 방위 길흉·연월반 계산, 운세.
    - `domain/entities/`: 핵심 비즈니스 엔티티.
    - `domain/repositories/`: 레포지토리 인터페이스 (7개).
    - `domain/services/`: 도메인 서비스 — `star_calculator_service`, `monthly_board_domain_service`, `fortune_status_service`, `five_elements_fortune_service`, `additional_direction_marks_service`, `direction_rule_engine`, `year_star_domain_service` + `interfaces/` (서비스 인터페이스).
    - `domain/constants/`: 도메인 상수 (`direction_constants` 등).
    - `domain/value_objects/`: 값 객체 (`gogyo`, `locale`, `star_grid_pattern_vo`).
    - `infrastructure/persistence/`: 레포지토리 구현 및 DB 연동.
    - `infrastructure/services/`: 인프라 서비스.
    - `use_cases/`: 애플리케이션 서비스 로직 — `calculate_stars_use_case`, `monthly_directions_use_case`.
    - `routes/`: API 엔드포인트 — `nine_star_routes`(`/api/nine-star/`), `monthly_routes`(`/api/monthly/`).
    - `services/`: 패턴 전환 서비스 (`pattern_switch_service`).
    - `utils/`: 유틸리티.
  - `apps/reading/numerology/`: 수비술(Numerology) 도메인 — Life Path Number 기반 파워스톤.
  - `apps/reading/powerstone/`: 파워스톤 추천 도메인 — 6-레이어 추천 엔진 + `data/` (JSON 데이터).
  - `apps/reading/shared/`: 공통 모듈 — `domain/`(entities: user/permission, constants, exceptions, repositories, services) + `infrastructure/persistence/` + `use_cases/`(admin_user_use_case, permission_use_case).
  - `apps/reading/dependency_module.py`: Flask-Injector 기반 DI 컨테이너 설정 (모든 서브도메인 바인딩).
- `migrations/`: Alembic DB 마이그레이션 디렉토리.
  - `migrations/versions/001_initial_schema.py`: 초기 스키마 생성.
  - `migrations/versions/002_seed_data.py`: SQL 파일 기반 시드 데이터 로드.
  - `migrations/versions/003_csv_seed_data.py`: CSV 파일 기반 마스터 데이터 시드 (대량 데이터용).
- `data/csv/`: Alembic CSV 시드 마이그레이션에서 로드하는 마스터 데이터 CSV 파일 7종 (zodiac_groups, zodiac_group_members, hourly_star_zodiacs, solar_terms, solar_starts, daily_astrology, pattern_switch_dates).
- `db_manage.py`: 데이터베이스 관리 유틸리티 — `init` (Alembic 마이그레이션 적용+슈퍼유저 생성), `reset` (전체 DROP+재구축), `create-superuser` (슈퍼유저만 생성).
- `tests/`: pytest 기반 테스트 — 도메인 서비스, 유즈케이스, 라우트 단위 테스트.
- `docs/architecture/`: 아키텍처 가이드, CI/CD 수동 설정 가이드, 리팩터링 플레이북 등.

## 📦 외부 의존성
- **Flask**: 웹 프레임워크.
- **Flask-Injector**: 의존성 주입 (Clean Architecture DI 컨테이너).
- **Flask-Migrate (Alembic)**: 데이터베이스 스키마 마이그레이션.
- **SQLAlchemy (Core / ORM)**: 데이터베이스 ORM 및 쿼리 빌더.
- **SQLAlchemy-Utils**: SQLAlchemy 확장 유틸리티.
- **psycopg2-binary**: PostgreSQL 드라이버.
- **Flask-JWT-Extended**: JWT 토큰 발급 및 검증.
- **gunicorn**: WSGI 서버 (Cloud Run 프로덕션 배포용).
- **pandas / numpy**: 데이터 처리 (CSV 시드 마이그레이션 등).
- **pytz**: 시간대 처리.

## ⚠️ 수정 시 주의사항
1. **Clean Architecture 준수**: `use_cases`나 `domain` 레이어에 `Flask`나 `SQLAlchemy` 같은 특정 인프라 코드가 직접적으로 침투하지 않도록 유의하세요.
2. **서브도메인 독립성**: `ninestarki`, `numerology`, `powerstone` 각 서브도메인은 서로 직접 import하지 않고, `dependency_module.py`를 통해 연결됩니다.
3. **DB 스키마 변경**: 모델을 변경할 경우, Alembic 마이그레이션(`migrations/versions/`)을 생성하세요 (`make db-migrate MSG="설명"`).
4. **환경에 따른 설정 분리**: `config.py`는 단일 `Config` 클래스로 구성. 프로덕션은 `DATABASE_URL` 환경변수로 제어.
5. **Cloud Run 호환성**: `start.sh`에서 `PORT` 환경변수를 반드시 사용. cron, logrotate, New Relic 등 VPS 전용 로직을 추가하지 마세요.
6. **패키지 정리**: `requirements.txt`에서 WeasyPrint, Redis, RQ 등은 제거된 상태. 추가 시 Cloud Run 이미지 크기 증가에 유의.
7. **CSV 시드 데이터**: 마스터 데이터 추가/수정 시 `data/csv/` 디렉토리의 CSV 파일과 `migrations/versions/003_csv_seed_data.py`를 함께 관리하세요.
8. **DI 컨테이너**: 새 서비스나 레포지토리 추가 시 `apps/reading/dependency_module.py`에 바인딩을 반드시 등록하세요. 서비스 생성자에 `@inject` 데코레이터를 사용하세요.
