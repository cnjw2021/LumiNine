# LumiNine (루미나인)

> 구성기학 × 수비술 — 두 가지 동양·서양 운명학을 융합한 맞춤형 파워스톤 큐레이션 서비스

## 프로젝트 개요

생년월일을 입력하면 **구성기학(九星気学)**과 **수비술(Numerology)** 두 축의 분석을 동시에 수행하여, 나에게 가장 필요한 에너지를 채워주는 **최대 8가지 레이어의 파워스톤**을 개인 맞춤형으로 큐레이션합니다.

### 8-Layer 파워스톤 시스템

| 레이어 | 이름 | 기반 | 변동 주기 |
|--------|------|------|----------|
| L1 | 전체운석 | 수비술 (Life Path Number) | 고정 |
| L2 | 건강운석 | 수비술 (Life Path × Sun) | 고정 |
| L3 | 재물운석 | 수비술 (Life Path × Jupiter) | 고정 |
| L4 | 연애운석 | 수비술 (Life Path × Venus) | 고정 |
| L5 | 연운석 | 수비술 (Personal Year Number) | 매년 |
| L6 | 기본석 | 구성기학 (본명성 오행) | 고정 |
| L7 | 월운석 | 구성기학 (월반성 × 길방위) | 매월 |
| L8 | 호신석 | 구성기학 (월반성 × 흉방위) | 매월 |

## 핵심 가치

- **동서양 융합**: 구성기학(동양)과 수비술(서양)을 하나의 시스템으로 통합
- **프리미엄 큐레이션**: 천연석 고유의 오행·행성 에너지를 정밀하게 매칭
- **현대적 오컬트**: 전통 명리학을 현대적이고 우아한 라이프스타일로 재해석
- **포토리얼 보석 이미지**: AI 생성 고품질 보석 이미지 30종 탑재 ([상세 카탈로그](frontend/public/images/stones/README.md))

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Next.js, TypeScript, Mantine UI |
| Backend | Flask, Python, SQLAlchemy |
| Database | MySQL |
| Infra | Docker Compose, Nginx, Let's Encrypt |

## 프로젝트 구조

```
LumiNine/
├── frontend/           # Next.js 프론트엔드
│   ├── src/components/ # UI 컴포넌트
│   │   ├── features/form/          # 입력 폼
│   │   ├── features/results/       # 감정 결과 페이지
│   │   └── features/visualization/ # 방위판·스톤카드
│   └── public/images/stones/       # 파워스톤 이미지 (30종)
├── backend/            # Flask 백엔드
│   └── apps/ninestarki/
│       ├── domain/services/    # 도메인 서비스 (구성기학·수비술 엔진)
│       ├── data/               # 스톤 카탈로그 JSON
│       └── use_cases/          # 유스케이스
├── mysql/init/         # DB 초기화 스크립트
├── nginx/              # Nginx 설정
├── docs/               # 프로젝트 문서
└── docker-compose.yml  # 컨테이너 오케스트레이션
```

## 로컬 개발

```bash
# 환경 설정
cp .env.example .env

# Docker로 전체 실행
docker compose up -d

# 프론트엔드 개발 서버
cd frontend && npm install && npm run dev

# 백엔드 개발 서버
cd backend && pip install -r requirements.txt && flask run
```

## 로드맵

GitHub Projects 및 Issues를 통해 가치 단위(Value Stream)로 관리됩니다.

### 진행 중 / 예정

- [#67](https://github.com/cnjw2021/LumiNine/issues/67) — 수비술 마스터넘버(11/22/33) 전용 파워스톤 매핑 추가
