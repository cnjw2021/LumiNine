# 프로젝트 디렉토리 구조 검토 보고서

## 1. 현재 구조 분석

### 디렉토리 이름: `backend/apps/ninestarki`

현재 앱은 **3개의 서로 다른 비즈니스 도메인**을 포함하고 있습니다:

| 도메인 | 설명 | 대표 파일 |
|--------|------|-----------|
| **구성기학 (Nine Star Ki)** | 방위 길흉 판별, 연·월 운세, 절기 등 | `star_calculator_service.py`, `direction_marks_domain_service.py` |
| **수비술 (Numerology)** | 라이프패스 넘버 계산 및 리딩 | `numerology_service.py`, `numerology_readings.json` |
| **파워스톤 (Powerstone)** | 위 두 도메인 결과 기반 추천 | `powerstone_matching_engine.py`, `six_layer_powerstone_use_case.py` |

하지만 디렉토리 이름이 `ninestarki`(九星気学 = 구성기학)로 되어 있어, **수비술과 파워스톤까지 포함하고 있다는 사실을 이름에서 알 수 없습니다**.

---

### 현재 내부 구조 (플랫 구조)

```
apps/ninestarki/
├── domain/
│   ├── entities/          ← 모든 도메인의 엔티티가 혼재
│   ├── repositories/      ← 13개 repo 인터페이스 (ninestar + numerology + powerstone)
│   ├── services/          ← 14개 도메인 서비스 (3개 도메인 전부 혼재)
│   │   └── interfaces/    ← 10개 서비스 인터페이스
│   └── value_objects/     ← gogyo, numerology, powerstone VO 혼재
├── infrastructure/
│   ├── persistence/       ← 14개 repo 구현체 (3개 도메인 전부 혼재)
│   ├── services/          ← 외부 어댑터
│   └── pdf/
├── routes/                ← 9개 라우트 파일
├── use_cases/             ← 15개 유스케이스 (3개 도메인 전부 혼재)
├── services/              ← 8개 서비스 (주로 구성기학)
├── data/                  ← JSON 카탈로그 (powerstone + numerology)
├── presentation/
├── templates/ & static/
└── dependency_module.py   ← 248줄, 모든 DI가 하나에
```

---

## 2. 발견된 문제점

### 🔴 문제 1: 디렉토리 이름과 실제 내용의 불일치

`ninestarki`라는 이름은 **구성기학만** 의미합니다. 수비술(Numerology)과 파워스톤(Powerstone) 기능이 추가된 현재, 이 이름은 **오해를 유발**합니다. 새로 합류하는 개발자나 AI 에이전트가 이 앱의 전체 범위를 파악하기 어렵습니다.

### 🟡 문제 2: 단일 앱에 여러 도메인이 플랫하게 혼재

현재 `domain/repositories/`에 13개, `domain/services/`에 14개, `use_cases/`에 15개 파일이 도메인 구분 없이 섞여 있습니다. 기능이 더 추가되면 파일 수가 급증하고 탐색이 어려워집니다.

### 🟡 문제 3: dependency_module.py의 비대화

248줄의 단일 DI 모듈이 3개 도메인의 모든 의존성을 관리합니다. Phase별 주석으로 구분하고 있지만 구조적 분리는 없습니다.

### 🟢 양호한 점: 클린 아키텍처 레이어 분리

`domain → use_cases → infrastructure → routes`로의 레이어 분리는 잘 되어 있고, 인터페이스 기반 DI 패턴도 적절합니다.

---

## 3. 개선안 비교

### 옵션 A: 이름만 변경 (최소 변경)

```
apps/fortunetelling/     ← 이름만 'ninestarki' → 'fortunetelling'으로 변경
├── domain/              ← 내부는 현재와 동일
├── infrastructure/
├── routes/
├── use_cases/
└── ...
```

| 장점 | 단점 |
|------|------|
| 변경 최소화, 리스크 낮음 | 파일 수 증가 시 혼란 여전 |
| 내부구조 변경 없음 | 도메인 간 경계가 여전히 불명확 |

---

### 옵션 B: 이름 변경 + 도메인별 서브패키지 도입 (권장)

```
apps/fortunetelling/                    ← divination, fortune, astrology 등도 가능
├── ninestarki/                         ← 구성기학 서브도메인
│   ├── domain/
│   │   ├── entities/                   ← nine_star.py, solar_term.py
│   │   ├── repositories/              ← nine_star, solar, directions 등
│   │   ├── services/                   ← star_calculator, direction_marks 등
│   │   └── value_objects/              ← gogyo.py
│   ├── infrastructure/persistence/     ← 구성기학 repo 구현체
│   ├── use_cases/                      ← calculate_stars, monthly_directions 등
│   ├── services/                       ← year_fortune, month_fortune 등
│   └── routes/                         ← nine_star_routes, monthly_routes 등
│
├── numerology/                         ← 수비술 서브도메인
│   ├── domain/
│   │   ├── repositories/              ← numerology_reading, numerology_powerstone repo
│   │   ├── services/                   ← numerology_service, numerology_powerstone_engine
│   │   └── value_objects/              ← numerology.py, numerology_powerstone.py
│   ├── infrastructure/persistence/     ← numerology repo 구현체
│   └── data/                           ← numerology_readings.json, numerology_powerstone_catalog.json
│
├── powerstone/                         ← 파워스톤 서브도메인 (두 도메인을 통합)
│   ├── domain/
│   │   ├── repositories/              ← powerstone_repository
│   │   ├── services/                   ← powerstone_matching_engine, gogyo_service
│   │   └── value_objects/              ← powerstone.py
│   ├── infrastructure/persistence/     ← powerstone repo 구현체
│   ├── use_cases/                      ← powerstone_recommendation, six_layer_powerstone
│   ├── routes/                         ← (monthly_routes의 powerstone 부분)
│   └── data/                           ← powerstone_catalog.json
│
├── shared/                             ← 공통 모듈
│   ├── domain/
│   │   ├── entities/                   ← user.py, permission.py
│   │   └── repositories/              ← user, permission repo
│   ├── infrastructure/                 ← 공통 repo 구현체
│   ├── use_cases/                      ← permission_use_case
│   ├── routes/                         ← admin, db_management routes
│   └── presentation/                   ← presenters
│
├── templates/ & static/                ← PDF 등 공유 자원
├── dependency_module.py                ← 서브도메인별 Module 클래스로 분리 가능
└── __init__.py
```

| 장점 | 단점 |
|------|------|
| 도메인 경계 명확 | import 경로 변경 많음 |
| 새 도메인 추가 시 구조가 자연스러움 | 리팩토링 작업량 큼 |
| 파일 탐색 직관적 | 테스트 구조도 함께 재편 필요 |
| DI 모듈 분리 가능 | — |

---

### 옵션 C: 멀티 앱 분리 (과도할 수 있음)

```
apps/
├── ninestarki/          ← 구성기학만
├── numerology/          ← 수비술만
├── powerstone/          ← 파워스톤만 (cross-domain 의존)
└── shared/              ← 공통 엔티티/인프라
```

| 장점 | 단점 |
|------|------|
| 완전한 독립성 | 과도한 분리 (현재 규모에서 불필요) |
| 개별 배포 가능 | 파워스톤이 두 앱에 의존 → 순환/복잡도 증가 |

---

## 4. 종합 권장사항

> [!IMPORTANT]
> **옵션 B (이름 변경 + 도메인별 서브패키지)**를 권장합니다.

### 이유

1. **현재 규모 (183개 파일)**: 단일 앱 내에서 서브패키지로 나누는 것이 가장 적절한 단위입니다
2. **향후 확장성**: 새로운 점술 도메인(사주, 타로 등)이 추가될 때 자연스러운 확장이 가능합니다
3. **점진적 마이그레이션**: 한 번에 모든 것을 바꿀 필요 없이, 서브패키지 단위로 순차 이동 가능합니다

### 앱 이름 후보

| 이름 | 의미 | 장단점 |
|------|------|--------|
| `fortunetelling` | 점술 | 직관적, 영어권에서 이해 쉬움 |
| `divination` | 점술/점복 | 좀 더 학술적 뉘앙스 |
| `fortune` | 운세 | 간결하지만 범위가 넓음 |
| `astrology` | 점성술 | 수비술은 점성술이 아니므로 정확하지 않음 |

> [!NOTE]
> 이 보고서는 **분석 및 권고안**입니다. 실제 리팩토링은 별도의 작업 계획이 필요하며, 대규모 import 경로 변경과 테스트 업데이트가 수반됩니다. 리팩토링을 진행하시려면 별도로 말씀해 주세요.
