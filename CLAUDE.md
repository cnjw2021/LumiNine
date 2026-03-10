# LumiNine (루미나인) 프로젝트 가이드

> Last updated: 2026-03-10

## 🏗 아키텍처 개요 (Architecture Overview)

- **Tech Stack (기술 스택)**:
  - Backend: Python, Flask, SQLAlchemy, Alembic (DB 마이그레이션)
  - Frontend: Next.js (App Router), TypeScript, Mantine UI
  - Database: PostgreSQL (Supabase)
  - PDF 생성: html2canvas + jsPDF (프론트엔드 클라이언트 사이드, off-screen clone 패턴)
  - Infrastructure: GitHub Actions, Google Cloud Run (Backend), Cloudflare Pages (Frontend)

- **Deployment Environment (배포 환경)**:
  - `main` 브랜치 push → GitHub Actions 자동 배포
  - Backend: GCP Cloud Run (Docker 컨테이너, `$PORT` 환경변수 바인딩)
  - Frontend: Cloudflare Pages (Next.js standalone)
  - DB: Supabase (PostgreSQL 16, `postgresql+psycopg2://` 연결)
  - DB 마이그레이션: Alembic (`flask db upgrade` → 스키마 + 시드 데이터 자동 적용)
  - 로컬 개발: Docker Compose (`docker-compose.yml`) — PostgreSQL 컨테이너 사용

- **CI/CD**:
  - `.github/workflows/ci.yml`: PR 테스트 (PostgreSQL 서비스 컨테이너 + pytest)
  - `.github/workflows/deploy-backend.yml`: Backend → GHCR → Cloud Run
  - `.github/workflows/deploy-frontend.yml`: Frontend → Cloudflare Pages

## 🔐 인증 흐름 (Authentication Flow)

- **JWT 기반 인증**:
  1. 클라이언트가 `/api/auth/login` 엔드포인트에 자격 증명 전송 (POST)
  2. 서버가 검증 후 JWT Access Token 발급
  3. 클라이언트는 이후 API 요청 시 `Authorization: Bearer <token>` 헤더에 토큰을 포함
  4. 서버는 보호된 라우트(예: `/api/auth/me`)에서 토큰을 검증해 사용자 인가 처리
- **패스워드 암호화**: `User` 모델(`apps/reading/shared/domain/entities/user.py`) 및 `auth_routes.py`에서 `bcrypt` 기반 해시/검증 사용

## 🔮 주요 API 경로

- **구성기학 기본 계산**: `/api/nine-star/calculate` (생년월일 기반 본명성, 월명성 등 계산 및 감정)
- **월반/연반(방위) 차트**: `/api/nine-star/monthly-chart`, `/api/monthly/directions` (월별 길방위/흉방위 계산)
- **파워스톤 추천**: `/api/nine-star/calculate` 응답에 6-레이어 파워스톤 추천 결과 포함
- **헬스체크**: `GET /api/health` (Cloud Run 헬스체크용, DB 연결 상태 포함)

## 📁 디렉토리별 역할 1줄 요약

- `backend/`: Flask 기반의 백엔드 API 서버 (Clean Architecture 적용)
  - `backend/apps/reading/`: 3개 서브도메인(ninestarki, numerology, powerstone) + shared
  - `backend/core/auth/`: JWT 인증, 패스워드 암호화, 권한 관리
  - `backend/migrations/`: Alembic DB 마이그레이션 (스키마 + 시드 데이터)
  - `backend/data/csv/`: 마스터 데이터 CSV 파일 (Alembic 시드 마이그레이션에서 사용)
  - `backend/docs/architecture/`: 아키텍처 가이드 및 CI/CD 수동 설정 가이드
- `frontend/`: Next.js(App Router) 기반의 프론트엔드 UI 및 클라이언트 애플리케이션
- `db/init/`: PostgreSQL 초기화 스크립트 (DDL/DML) — Docker 로컬 개발용
- `.github/workflows/`: GitHub Actions CI/CD 워크플로우
- `docs/`: 프로젝트 관련 문서 보관
- `Makefile`: 로컬 개발 명령어 모음

## 🗄 DB 테이블과 관계 요약

- **기본 별 정보**: `stars` (1-9 백수성~구자화성 기본 데이터)
- **별 속성 (추천 음식 등)**: `star_attributes` (본명성별 오행, 성격, 추천 음식 등)
- **달력 및 절기 데이터**: `solar_starts` (입춘 데이터), `solar_terms` (절기 데이터), `daily_astrology` (일별 간지/별 데이터)
- **방위 및 배치 데이터**: `star_grid_patterns` (구성반), `monthly_directions` (월반 방위)
- **파워스톤**: `powerstone_master`, `recommendation_history`
- **시스템 및 인증 데이터**: `users`, `permissions`, `user_permissions`, `system_config`
- **스키마 위치**: `db/init/000_create_tables.sql` (PostgreSQL DDL)
- **프로덕션 마이그레이션**: `backend/migrations/versions/` (Alembic — 001 스키마, 002 SQL 시드, 003 CSV 시드)

## ✍️ 코딩 컨벤션

- **Backend (Python)**: PEP 8 스타일 가이드를 따르며, Clean Architecture를 지향하여 비즈니스 로직(Domain/Use Cases)과 프레임워크(Web/Infrastructure)를 분리.
- **Frontend (TypeScript)**: `eslint`와 `prettier` (`eslint-config-next`) 규칙을 준수. App Router 패턴의 Server Component와 Client Component(`"use client"`)를 명확히 분리.
- **DB**: PostgreSQL DDL/DML은 `db/init/` 디렉터리에서 버전 관리. 프로덕션 환경은 Alembic으로 마이그레이션.
- **공통**: 변수명/함수명은 영어, 주석은 한국어 OK
- **📌 코드 리뷰 가이드라인**: [docs/CODE_REVIEW_GUIDELINES.md](docs/CODE_REVIEW_GUIDELINES.md) 를 코드 작성 전 반드시 참조

## 🔐 환경변수 목록

`.env` 파일 등을 통해 다음 주요 환경변수가 관리됩니다 (`.env.example` 참고):

- `DATABASE_URL`: PostgreSQL 연결 문자열 (`postgresql+psycopg2://user:pass@host:5432/db`)
- `DB_HOST`: 데이터베이스 호스트 (로컬: `postgres`, 프로덕션: Supabase URL)
- `DB_USER` / `DB_PASSWORD` / `DB_NAME` / `DB_PORT`: 개별 DB 연결 설정 (DATABASE_URL 폴백)
- `SECRET_KEY`: 백엔드 애플리케이션 시크릿 키
- `JWT_SECRET_KEY`: JWT 토큰 발급용 시크릿 키
- `PORT`: Cloud Run이 자동 주입하는 포트 (기본값 5001)
- `NEXT_PUBLIC_API_URL`: 프론트엔드에서 사용하는 백엔드 API URL (프로덕션)

## 📚 주요 문서

| 문서 | 설명 |
|------|------|
| [CI/CD 수동 설정 가이드](backend/docs/architecture/cicd-manual-setup-guide.md) | GitHub Secrets · Supabase · Cloud Run · Cloudflare Pages 순서별 안내 |
| [방위 길흉 판정 로직](docs/monthly-direction-marks-logic.md) | 오행 상생 + 정위대충·소아살 파이프라인 |
| [아키텍처 가이드](backend/docs/architecture/clean_architecture_guide.md) | Clean Architecture 적용 방식 |
| [코드 리뷰 가이드라인](docs/CODE_REVIEW_GUIDELINES.md) | 코드 작성 및 리뷰 시 준수 사항 |
| [CI 테스트 아키텍처](docs/ci-test-architecture.md) | GitHub Actions CI 테스트 구성 |