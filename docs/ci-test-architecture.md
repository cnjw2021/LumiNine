# CI 테스트 아키텍처

> **최종 업데이트:** 2026-03-01  
> **대상 브랜치:** `fix/integration-test-seeding`

## 개요

본 프로젝트의 CI 파이프라인은 테스트를 **단위 테스트 (Unit Test)** 와 **통합 테스트 (Integration / E2E Test)** 로 분리하여, 각각 다른 트리거로 실행합니다.

| 테스트 종류 | 트리거 | 워크플로우 | Makefile 타겟 | DB 필요 |
|-----------|---------|-------------|-------------------|---------|
| 단위 테스트 | Push / PR → `main` (자동) | `ci.yml` | `make test-unit` | ❌ |
| 통합 테스트 | `workflow_dispatch` (수동) | `integration-test.yml` | `make test-integration` | ✅ |
| 전체 테스트 | 로컬 실행 | — | `make test` | ✅ |

---

## 테스트 분류

### 단위 테스트 (23건) — DB 불필요
```
tests/unit/test_daily_star_reading_use_case.py
tests/unit/test_reading_query_use_case.py
tests/unit/test_star_catalog_use_case.py
tests/test_generate_report_happy.py
tests/test_generate_report_partner.py
tests/test_generate_report_use_case_fakes.py
tests/test_generate_report_validation.py
tests/test_solar_starts_repository_param.py
tests/test_solar_terms_boundaries.py
```

### 통합 테스트 (35건) — 백엔드 API + DB 필수
```
tests/golden_master/test_annual_directions.py
tests/golden_master/test_auspicious_days_report.py
tests/golden_master/test_daily_star_reading.py
tests/golden_master/test_direction_fortune.py
tests/golden_master/test_month_acquired_fortune.py
tests/golden_master/test_month_star_readings.py
tests/golden_master/test_star_attributes.py
tests/golden_master/test_star_life_guidance.py
tests/golden_master/test_year_acquired_fortune.py
tests/golden_master/test_year_star.py
tests/test_direction_fortune_birthdate_2026.py
```

---

## 조사 및 수정 과정

### Phase 1: 기본 CI 셋업

**문제:** GitHub Actions에서 `make test` 실행 시 전체 테스트 실패.

**조사 결과:**
- `PermissionError: [Errno 13] Permission denied: '/app/logs'` — Docker 컨테이너 내부 사용자 권한 문제
- `backend-test` 컨테이너가 `appuser`로 실행되어 로그 디렉토리에 쓰기 불가

**수정:**
- `docker-compose.dev.yml`의 `backend-test`에 `user: root` 추가
- CI 워크플로우에서 `mkdir -p backend/logs backend/.pytest_cache && chmod -R 777` 실행

---

### Phase 2: 백엔드 컨테이너 헬스체크 실패

**문제:** `dependency failed to start: container backend-container is unhealthy`

**조사 결과:**
1. **Linux 파일 권한 충돌:** `db_manage.py init`이 `root`로 `/app/logs/app.log`를 생성 → 이후 `gunicorn`이 `appuser`로 기동 → Permission Denied로 worker 전멸
2. **GitHub Actions의 느린 환경:** 2코어 runner에서 헬스체크 타임아웃

**수정:**
- `start.sh`에 `chown -R appuser:appgroup /app/logs` 추가 (`gunicorn` fork 전)
- 헬스체크 `start_period: 30s`, `retries: 15`로 증가

---

### Phase 3: 데이터베이스 연결 오류 (Access Denied)

**문제:** `Access denied for user 'ninestarki'@'172.18.0.4' (using password: YES)`

**조사 결과 (근본 원인 특정까지의 과정):**

1. **환경변수 전파 경로 분석:**
   ```
   ci.yml env → .env (root) → docker-compose.yml → mysql 컨테이너
                             → backend/.env.development.backend → backend 컨테이너
   ```

2. **`touch` vs `>`의 차이:**
   - `touch backend/.env.production.backend` → **파일 내용이 유지됨** (타임스탬프만 갱신)
   - `> backend/.env.production.backend` → **파일 내용이 비워짐**

3. **`DATABASE_URL` 우선순위 문제:**
   - `backend/.env.production.backend`가 **Git에 커밋**되어 있었음
   - 내용: `DATABASE_URL=mysql+pymysql://ninestarki:ninestarki_password@mysql:3306/ninestarki`
   - `core/db_config.py`는 `DATABASE_URL`을 `DB_USER`보다 **우선** 사용 (line 89)
   - CI에서 `DB_USER=superuser`를 설정해도, `DATABASE_URL`이 우선하므로 항상 `ninestarki`로 접속

**수정:**
```yaml
# ci.yml - 프로덕션 환경 파일을 truncate (touch가 아닌 >)
> backend/.env.production.backend

# 개발용 .env에 DATABASE_URL을 포함한 전체 변수 생성
echo "DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASSWORD}@mysql:3306/${DB_NAME}?charset=utf8mb4" >> backend/.env.development.backend
```

---

### Phase 4: 단위 테스트 / 통합 테스트 분리

**문제:** DB가 빈 상태에서는 통합 테스트가 반드시 실패 (`No yearly_info for 2025` 등)

**판단:** CI의 자동 테스트는 단위 테스트만으로 한정하고, 통합 테스트는 `workflow_dispatch`로 수동 실행

**수정:**
- `ci.yml`: `make test` → `make test-unit`으로 변경
- `integration-test.yml`: 신규 생성 (`workflow_dispatch` 트리거)
- `Makefile`: `test-unit`, `test-integration`, `db-seed` 타겟 추가

---

### Phase 5: 통합 테스트용 데이터 시딩

**문제:** `make test-integration`을 실행해도 DB가 비어 있어 전체 테스트 실패

**조사 결과 (3개의 버그를 단계적으로 발견):**

| # | 에러 메시지 | 원인 | 수정 |
|---|------------|------|------|
| 1 | `Access denied for user 'ninestarki'` | `backend-test`에 `env_file`이 없어 기본값 `ninestarki` 자격 증명 사용 | `docker-compose.dev.yml`에 `env_file: ./backend/.env.development.backend` 추가 |
| 2 | `Table 'ninestarki.zodiac_groups' doesn't exist` | `db_manage.py reset`이 테이블 생성 후 `commit()` 안 함 → 별도 커넥션의 CSV 로더에서 테이블이 보이지 않음 | `conn.commit()`을 테이블 생성 직후에 추가 |
| 3 | `SQL 파일 'mysql/init/xxx.sql'을 찾을 수 없습니다` | `backend-test` 컨테이너 내 CWD는 `/app` (= `./backend`), 하지만 SQL 파일은 `./mysql/init/` (리포지토리 루트)에 위치 | 볼륨 마운트 `./mysql/init:/app/mysql/init` 추가 |

**최종 `docker-compose.dev.yml`의 `backend-test` 수정 내용:**
```yaml
backend-test:
  user: root
  volumes:
    - ./backend:/app
    - ./mysql/init:/app/mysql/init      # SQL 시드 스크립트
    - ./backend/data:/var/lib/mysql-files  # CSV 파일 (LOAD DATA INFILE용)
  env_file:
    - ./backend/.env.development.backend
  environment:
    - PYTHONPATH=/app
```

---

## 데이터 시딩 파이프라인

통합 테스트 실행 시, 아래 순서로 데이터가 투입됩니다:

```mermaid
graph TD
    A[MySQL 컨테이너 기동] -->|docker-entrypoint-initdb.d| B[000_create_tables.sql<br/>테이블 생성]
    B --> C[001_create_users.sql<br/>권한 설정]
    C --> D[100_stars.sql ~ 900_system_data.sql<br/>SQL INSERT 데이터]
    D --> E[make db-seed]
    E -->|db_manage.py reset| F[테이블 DROP & 재생성]
    F -->|conn.commit| G[SQL 파일로 INSERT]
    G --> H[load_all_csv_data<br/>CSV LOAD DATA INFILE]
    H --> I[create_superuser<br/>슈퍼유저 생성]
    I --> J[통합 테스트 실행<br/>make test-integration]
```

### CSV로 로드되는 데이터
| CSV 파일 | 테이블 |
|---------|--------|
| `solar_terms_data.csv` | `solar_terms` |
| `solar_starts_data.csv` | `solar_starts` |
| `daily_astrology_data.csv` | `daily_astrology` |
| `star_life_guidance.csv` | `star_life_guidance` |
| `pattern_switch_dates.csv` | `pattern_switch_dates` |
| `zodiac_groups.csv` | `zodiac_groups` |
| `zodiac_group_members.csv` | `zodiac_group_members` |
| `hourly_star_zodiacs.csv` | `hourly_star_zodiacs` |
| `compatibility_master_*.csv` (9건) | `compatibility_master` |
| 기타 | `star_compatibility_matrix`, `compatibility_readings_master` 등 |

---

## 사용법

### 로컬 실행

```bash
# 전체 테스트 실행
make test

# 단위 테스트만
make test-unit

# 통합 테스트만 (사전에 make up ENV=dev 로 DB 기동 필요)
make test-integration

# DB 데이터 완전 리셋 & 재투입
make db-seed
```

### GitHub Actions 실행

| 작업 | 방법 |
|------|------|
| 단위 테스트 | `main`에 Push / PR 시 자동 실행 |
| 통합 테스트 | GitHub → Actions → "Integration Tests (Manual)" → "Run workflow" → 브랜치 선택 → Run |
| 특정 테스트 | `test_path`에 `tests/golden_master/test_year_star.py` 등을 입력 |

---

## 관련 파일

| 파일 | 역할 |
|------|------|
| `.github/workflows/ci.yml` | 자동 CI (단위 테스트만) |
| `.github/workflows/integration-test.yml` | 수동 통합 테스트 |
| `Makefile` | `test`, `test-unit`, `test-integration`, `db-seed` 타겟 |
| `docker-compose.dev.yml` | `backend-test` 서비스 정의 |
| `backend/db_manage.py` | `init` (슈퍼유저만) / `reset` (전체 데이터 재투입) |
| `backend/scripts/csv_file_loader.py` | CSV 데이터 로더 |
| `mysql/init/*.sql` | MySQL 초기화 스크립트 |
| `backend/core/db_config.py` | DB 접속 정보 관리 (`DATABASE_URL` 우선) |
