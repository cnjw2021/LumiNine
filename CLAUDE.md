# Nine Star Ki (구성기학) 프로젝트 가이드

## 🏗 아키텍처 개요 (Architecture Overview)

- **Tech Stack (기술 스택)**:
  - Backend: Python, FastAPI, SQLAlchemy
  - Frontend: Next.js, TypeScript, Mantine UI
  - Database: MySQL 8.0, Redis (for Task Queue)
  - PDF 생성: WeasyPrint (Worker Queue 경유)
  - Infrastructure: Docker, Docker Compose, Nginx, Certbot (HTTPS)
- **Deployment Environment (배포 환경)**:
  - ConoHa VPS 위에 Docker Compose를 이용한 컨테이너 기반 배포 (운영환경용 `docker-compose.yml`, 개발환경용 `docker-compose.dev.yml`)
  - Nginx 리버스 프록시 및 Certbot을 통한 SSL 자동 갱신 지원 환경

## 🔐 인증 흐름 (Authentication Flow)

- **JWT 기반 인증**:
  1. 클라이언트가 `/api/auth/login` 엔드포인트에 자격 증명 전송 (POST)
  2. 서버가 검증 후 JWT Access Token 발급
  3. 클라이언트는 이후 API 요청 시 `Authorization: Bearer <token>` 헤더에 토큰을 포함
  4. 서버는 보호된 라우트(예: `/api/auth/me`)에서 토큰을 검증해 사용자 인가 처리

## 🔮 주요 감정 API 경로 (Fortune Telling API)

- **구성기학 기본 계산**: `/api/nine-star/calculate` (생년월일 기반 본명성, 월명성 등 계산 및 감정)
- **상성(궁합) 감정**: `/api/nine-star/compatibility` (두 사람의 별을 기반으로 상성 결과 반환)
- **월반/연반(방위) 차트**: `/api/nine-star/monthly-chart`, `/api/monthly/directions` (월별 길방위/흉방위 계산)
- **운세 및 가이던스**: `/api/star-life-guidance` (별자리별 삶의 지침 및 운세 제공)

## 📁 디렉토리별 역할 1줄 요약

- `backend/`: FastAPI 기반의 백엔드 API 서버 (Clean Architecture 적용)
- `frontend/`: Next.js(App Router) 기반의 프론트엔드 UI 및 클라이언트 애플리케이션
- `mysql/`: MySQL 데이터베이스 초기화 스크립트 및 설정 (DDL/DML)
- `nginx/`: Nginx 웹 서버 및 리버스 프록시 설정 파일
- `certbot/`: SSL/TLS 인증서 발급 및 갱신 설정
- `docs/`: 프로젝트 관련 문서 보관

## 🗄 DB 테이블과 관계 요약

- **기본 별 정보**: `stars` (1-9 백수성~구자화성 기본 데이터)
- **달력 및 절기 데이터**: `solar_starts` (입춘 데이터), `solar_terms` (절기 데이터), `daily_astrology` (일별 간지/별 데이터)
- **운세 및 감정 데이터**: `monthly_star_readings`, `daily_star_readings`, `star_attributes`, `main_star_acquired_fortune_message`, `month_star_acquired_fortune_message` - 모두 `stars` 테이블의 `star_number`를 Foreign Key로 참조
- **방위 및 상성 데이터**: `star_grid_patterns` (구성반), `monthly_directions` (월반 방위), `star_compatibility_matrix`, `compatibility_master` (상성 마스터)
- **시스템 및 인증 데이터**: `users` (사용자 정보), `permissions`, `user_permissions` (권한 관리)

## ✍️ 코딩 컨벤션

- **Backend (Python)**: PEP 8 스타일 가이드를 따르며, Clean Architecture를 지향하여 비즈니스 로직(Domain/Use Cases)과 프레임워크(Web/Infrastructure)를 분리.
- **Frontend (TypeScript)**: `eslint`와 `prettier` (`eslint-config-next`) 규칙을 준수. 가급적 App Router 패턴의 Server Component와 Client Component(`"use client"`)를 명확히 분리하여 사용. Custom hooks 및 Mantine UI 컴포넌트 활용.
- **DB**: MySQL DDL/DML은 `mysql/` 디렉토리에서 버전 관리
- **공통**: 변수명/함수명은 영어, 주석은 한국어 OK

## 🔐 환경변수 목록

`.env` 파일 등을 통해 다음 주요 환경변수가 관리됩니다:

- `DB_HOST`: 데이터베이스 호스트 (default: mysql)
- `DB_USER`: DB 사용자 (default: ninestarki)
- `DB_PASSWORD`: DB 비밀번호
- `DB_NAME`: 데이터베이스명 (default: ninestarki)
- `DB_PORT`: 데이터베이스 포트 (default: 3306)
- `DB_ROOT_PASSWORD`: MySQL root 암호
- `SECRET_KEY`: 백엔드 애플리케이션 시크릿 키 (본번환경 필수)
- `JWT_SECRET_KEY`: JWT 토큰 발급용 시크릿 키
- `FRONTEND_URL` / 기타 `.env.development.frontend`, `.env.production.frontend` 등 프론트엔드별 설정 값