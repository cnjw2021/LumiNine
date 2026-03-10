# CI/CD 파이프라인 수동 설정 가이드

> **관련 이슈**: [#92 GitHub Actions CI/CD 파이프라인 구축](https://github.com/cnjw2021/LumiNine/issues/92)
> **관련 PR**: [#96 feat: GitHub Actions CI/CD 파이프라인 구축](https://github.com/cnjw2021/LumiNine/pull/96)

코드 변경(PR #96)만으로는 완성되지 않는 **외부 서비스 설정 작업**을 순서대로 안내합니다.

---

## 전체 작업 순서

```
1. GitHub Secrets 등록  ← 가장 먼저, 모든 배포의 전제 조건
2. Supabase 프로젝트 생성 + 마스터 데이터 이관
3. Google Cloud Run 서비스 생성 + 환경변수 설정
4. Cloudflare Pages 프로젝트 생성 + 도메인 연결
5. ConoHa VPS 정리
```

---

## 1단계: GitHub Secrets 등록

**위치**: GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret

### 1-1. Cloudflare 관련

| Secret 이름 | 값 가져오는 방법 |
|-------------|-----------------|
| `CLOUDFLARE_API_TOKEN` | [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens) → **Create Token** → "Edit Cloudflare Pages" 템플릿 선택 |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Dashboard 우측 사이드바 → **Account ID** 복사 |
| `CF_PAGES_PROJECT_NAME` | Cloudflare Pages 프로젝트명 (예: `luminine-frontend`) |
| `NEXT_PUBLIC_API_URL` | Cloud Run 배포 완료 후 발급되는 기본 URL (예: `https://luminine-backend-xxxx-an.a.run.app`). `api.ts`에서 자동으로 `/api` 접미사를 추가합니다. |

### 1-2. Google Cloud 관련

```bash
# GCP 서비스 계정 생성
gcloud iam service-accounts create luminine-deployer \
  --display-name="LumiNine CI/CD Deployer"

SA_EMAIL="luminine-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com"

# 필요 권한 부여
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/run.admin"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/iam.serviceAccountUser"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/storage.admin"

# JSON 키 생성 → base64 인코딩
gcloud iam service-accounts keys create key.json --iam-account="${SA_EMAIL}"
base64 -i key.json | pbcopy   # macOS: 클립보드에 복사됨
```

| Secret 이름 | 값 |
|-------------|-----|
| `GCP_SA_KEY` | 위 `base64` 결과 전체를 붙여넣기 |
| `GCP_PROJECT_ID` | GCP Console 상단 프로젝트 셀렉터에서 확인 |
| `GCP_REGION` | 사용할 Cloud Run 리전 (예: `asia-northeast1`) |
| `GCP_SERVICE_NAME` | Cloud Run 서비스명 (예: `luminine-backend`) |

### 1-3. Supabase / 앱 시크릿

```bash
# SECRET_KEY, JWT_SECRET_KEY 생성 (각각 독립적으로)
python3 -c "import secrets; print(secrets.token_hex(32))"
```

| Secret 이름 | 값 |
|-------------|-----|
| `DATABASE_URL` | Supabase에서 복사한 URI (아래 2단계 완료 후) |
| `SECRET_KEY` | 위 명령어로 생성한 32바이트 hex 문자열 |
| `JWT_SECRET_KEY` | 위 명령어로 별도 생성 |
| `SUPERUSER_EMAIL` | 관리자 계정 이메일 |
| `SUPERUSER_PASSWORD` | 관리자 계정 비밀번호 (강력한 비밀번호 사용) |

---

## 2단계: Supabase 설정 + 마스터 데이터 이관

### 2-1. Supabase 프로젝트 생성

1. [supabase.com](https://supabase.com/) 로그인 후 **New Project** 클릭
2. 프로젝트명: `luminine` / 리전: **Northeast Asia (Tokyo)** 권장 / 비밀번호 설정
3. 생성 완료 후 **Project Settings → Database → Connection string → URI** 복사

### 2-2. DATABASE_URL 형식 변환

Supabase에서 복사한 URI는 `postgres://...` 형식이므로 psycopg2 호환 형식으로 변환:

```
# 원본 (Supabase 제공)
postgres://postgres.xxxx:password@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

# 변환 후 (GitHub Secret에 등록)
postgresql+psycopg2://postgres.xxxx:password@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

> `postgres://` → `postgresql+psycopg2://` 로만 바꾸면 됩니다.

### 2-3. 스키마 초기화 + 마스터 데이터 이관

Supabase Dashboard → **SQL Editor** 에서 아래 파일을 **번호 순서대로** 실행:

```
db/init/000_create_tables.sql        ← 테이블 생성 (반드시 먼저 실행)
db/init/001_setup_privileges.sql     ← 권한 설정
db/init/100_stars.sql                ← 구성 마스터 데이터
db/init/200_star_attributes.sql      ← 추천 음식 등 속성 데이터
db/init/210_star_grid_patterns.sql   ← 구성판 패턴
db/init/300_monthly_directions.sql   ← 월반 방위 데이터
db/init/310_star_number_group.sql    ← 성 그룹
db/init/320_pattern_switch_dates.sql ← 패턴 전환 절기 날짜
db/init/510_powerstone_seed.sql      ← 파워스톤 마스터 데이터
db/init/900_system_data.sql          ← 시스템 설정
db/init/999_system_user.sql          ← 슈퍼유저 권한 (create_superuser() 실행 후)
```

> 💡 모든 파일은 PostgreSQL 호환 구문으로 작성되어 있습니다.

---

## 3단계: Google Cloud Run 서비스 생성

### 3-1. Cloud Run API 활성화

```bash
gcloud services enable run.googleapis.com --project=YOUR_PROJECT_ID
```

### 3-2. Placeholder 서비스 생성

GitHub Actions가 배포할 Cloud Run 서비스를 먼저 만들어 둡니다:

```bash
gcloud run deploy luminine-backend \
  --image gcr.io/cloudrun/placeholder \
  --platform managed \
  --region asia-northeast1 \
  --project YOUR_PROJECT_ID \
  --allow-unauthenticated
```

### 3-3. 환경변수 설정 (Cloud Run Console)

> ⚠️ **반드시 자동 배포 전에 설정하세요.** 환경변수가 없으면 컨테이너가 시작 직후 crash합니다.

Cloud Run Console → 서비스 → 편집 → 컨테이너 → 환경 변수:

| 환경 변수 | 값 |
|-----------|-----|
| `DATABASE_URL` | Supabase 연결 문자열 (`postgresql+psycopg2://...`) |
| `SECRET_KEY` | GitHub Secret과 동일 값 |
| `JWT_SECRET_KEY` | GitHub Secret과 동일 값 |
| `SUPERUSER_EMAIL` | 관리자 이메일 |
| `SUPERUSER_PASSWORD` | 관리자 비밀번호 |
| `FLASK_ENV` | `production` |
| `PORT` | `5001` (Cloud Run에서 자동 주입, 명시 불필요) |

### 3-4. 자동 배포 트리거

3-2, 3-3이 완료된 상태에서 `main` 브랜치에 push/merge하면 `.github/workflows/deploy-backend.yml`이 자동으로 Cloud Run 배포를 수행합니다.

### 3-5. 헬스체크 확인

배포 완료 후 아래로 정상 응답(`{"status": "ok", "db": "connected"}`) 확인:
```bash
curl https://YOUR_CLOUD_RUN_URL/api/health
```

### 3-6. CORS 설정 업데이트

`backend/app.py`의 CORS origins에 Cloudflare Pages 도메인을 추가:
```python
"origins": [
    "http://localhost:3000",
    "https://your-pages-project.pages.dev",   # Cloudflare Pages 기본 도메인
    "https://your-custom-domain.com",          # 커스텀 도메인
]
```

---

## 4단계: Cloudflare Pages 설정 + 도메인 연결

### 4-1. Pages 프로젝트 생성 (빈 프로젝트)

> ⚠️ **Connect to Git을 선택하지 마세요!** Git 연결은 Cloudflare 자체 CI/CD를 구성하며, 이미 존재하는 GitHub Actions 워크플로우(`deploy-frontend.yml`)와 충돌합니다.

1. [Cloudflare Dashboard](https://dash.cloudflare.com/) → **Workers & Pages** → **Create application** → **Pages** 탭
2. **Upload assets** (또는 "Drag and drop your files") → **Get started** 클릭
3. 프로젝트 이름 입력 (예: `luminine-frontend`) → **Create project**
4. 빈 프로젝트가 생성됩니다 — **실제 배포는 GitHub Actions가 자동으로 수행**합니다

> 💡 프로젝트 이름은 GitHub Secret `CF_PAGES_PROJECT_NAME`에 등록한 값과 반드시 일치해야 합니다.

### 4-2. 커스텀 도메인 연결

1. Cloudflare Pages → 프로젝트 → **Custom domains** → **Set up a custom domain**
2. 도메인 입력 → DNS 레코드 자동 추가 확인 → **Activate domain**
3. SSL은 Cloudflare에서 자동 관리됩니다

### 4-3. GitHub Secret 업데이트

Cloudflare Pages 배포 확인 후 `NEXT_PUBLIC_API_URL` Secret에 Cloud Run URL이 정확히 입력되어 있는지 확인.

---

## 5단계: ConoHa VPS 정리

모든 배포가 정상 동작한다면:

1. **DNS 레코드 이전 확인** — 도메인이 Cloudflare로 완전히 이전되었는지 확인
2. **VPS 컨테이너 중지** — 서버에 접속하여 Docker 컨테이너 종료
3. **서버 스냅샷 생성** — ConoHa 콘솔에서 스냅샷 저장 (데이터 유실 방지)
4. **VPS 정지/삭제** — 스냅샷 확인 후 서버 정지

> ⚠️ `docker-compose.prod.yml`, `deploy.sh` 등 구 VPS 배포 파일은 Issue #97에서 삭제되었습니다.


