# Backend 모듈 가이드

> Last updated: 2026-03-10

## 🎯 해당 모듈의 책임 범위
- 구성기학(九星気学)·수비술(Numerology)·파워스톤 추천 등 비즈니스 로직 계산 및 데이터베이스 CRUD 처리.
- 사용자 인증(Authentication/Authorization), JWT 발급, 패스워드 암호화(`werkzeug.security`) 등 세션 및 권한 관리.
- 클라이언트(프론트엔드)에서 접근 가능한 RESTful API 엔드포인트 제공.
- Cloud Run 배포: `$PORT` 환경변수 바인딩, `GET /api/health` 헬스체크 엔드포인트.
- Alembic 기반 DB 마이그레이션: `flask db upgrade`로 스키마 + 시드 데이터 자동 적용.

## 📂 주요 파일별 역할
- `app.py`: Flask 애플리케이션의 엔트리포인트. 미들웨어 설정 및 최상위 Blueprint/Router 연결. `/api/health` 포함.
- `start.sh`: Cloud Run 전용 Gunicorn 기동 스크립트 (`$PORT` 환경변수 바인딩, cron/logrotate 없음).
- `config.py`: 애플리케이션 설정. `DATABASE_URL`(`postgresql+psycopg2://`) 우선, 개별 환경변수 폴백.
- `wait_for_db.py`: 로컬 개발환경 전용 PostgreSQL 연결 대기 스크립트 (psycopg2 사용).
- `core/`: 설정(`config.py`), DB 세션(`database.py`), DB 설정(`db_config.py`), 예외 처리(`exceptions.py`), 유틸리티.
  - `core/auth/`: 인증 모듈 — `auth_routes.py`(로그인·관리API), `auth_utils.py`(패스워드 해시), `jwt_helpers.py`(JWT), `permission_routes.py`(권한관리).
  - `core/models/`: SQLAlchemy 모델 정의.
  - `core/services/`: 공통 서비스 레이어.
- `apps/reading/`: 도메인 기반으로 분리된 기능 모듈. 3개 서브도메인 + 공통 모듈.
  - `apps/reading/ninestarki/`: 구성기학(九星気学) 도메인 — 방위 길흉·연월반 계산, 운세.
    - `domain/`: 핵심 비즈니스 객체 및 레포지토리 인터페이스.
    - `infrastructure/`: 레포지토리 구현 및 DB 연동.
    - `use_cases/`: 애플리케이션 서비스 로직 (비즈니스 흐름 제어).
    - `routes/`: API 엔드포인트 (Flask Blueprint).
  - `apps/reading/numerology/`: 수비술(Numerology) 도메인 — Life Path Number 기반 파워스톤.
  - `apps/reading/powerstone/`: 파워스톤 추천 도메인 — 6-레이어 추천 엔진.
  - `apps/reading/shared/`: 공통 모듈 — user, permission, 예외, 상수.
  - `apps/reading/dependency_module.py`: Flask-Injector 기반 DI 컨테이너 설정.
- `migrations/`: Alembic DB 마이그레이션 디렉토리.
  - `migrations/versions/001_initial_schema.py`: 초기 스키마 생성.
  - `migrations/versions/002_seed_data.py`: SQL 파일 기반 시드 데이터 로드.
  - `migrations/versions/003_csv_seed_data.py`: CSV 파일 기반 마스터 데이터 시드 (대량 데이터용).
- `data/csv/`: Alembic CSV 시드 마이그레이션에서 참조하는 마스터 데이터 CSV 파일 (daily_astrology, solar_terms 등 9종).
- `db_manage.py`: 데이터베이스 초기화(init) 및 리셋(reset) 유틸리티 스크립트 (로컬 개발/Docker용).
- `docs/architecture/cicd-manual-setup-guide.md`: CI/CD 수동 설정 가이드 (Secrets 등록부터 VPS 정리까지).

## 📦 외부 의존성
- **Flask**: 웹 프레임워크.
- **Flask-Injector**: 의존성 주입 (Clean Architecture DI 컨테이너).
- **Flask-Migrate (Alembic)**: 데이터베이스 스키마 마이그레이션.
- **SQLAlchemy (Core / ORM)**: 데이터베이스 ORM 및 쿼리 빌더.
- **psycopg2-binary**: PostgreSQL 드라이버 (구 PyMySQL/mysql-connector 대체).
- **Flask-JWT-Extended**: JWT 토큰 발급 및 검증.
- **gunicorn**: WSGI 서버 (Cloud Run 프로덕션 배포용).

## ⚠️ 수정 시 주의사항
1. **Clean Architecture 준수**: `use_cases`나 `domain` 레이어에 `Flask`나 `SQLAlchemy` 같은 특정 인프라 코드가 직접적으로 침투하지 않도록 유의하세요.
2. **서브도메인 독립성**: `ninestarki`, `numerology`, `powerstone` 각 서브도메인은 서로 직접 import하지 않고, `dependency_module.py`를 통해 연결됩니다.
3. **DB 스키마 변경**: 모델을 변경할 경우, `db/init/000_create_tables.sql` (PostgreSQL DDL)과 Alembic 마이그레이션(`migrations/versions/`)을 함께 수정하세요. (`mysql/init/`는 레거시이므로 참고용으로만 사용)
4. **환경에 따른 설정 분리**: `config.py`는 단일 `Config` 클래스로 구성. 프로덕션은 `DATABASE_URL` 환경변수로 제어.
5. **Cloud Run 호환성**: `start.sh`에서 `PORT` 환경변수를 반드시 사용. cron, logrotate, New Relic 등 VPS 전용 로직을 추가하지 마세요.
6. **패키지 정리**: `requirements.txt`에서 WeasyPrint, Redis, RQ 등은 제거된 상태. 추가 시 Cloud Run 이미지 크기 증가에 유의.
7. **CSV 시드 데이터**: 마스터 데이터 추가/수정 시 `data/csv/` 디렉토리의 CSV 파일과 `migrations/versions/003_csv_seed_data.py`를 함께 관리하세요.
