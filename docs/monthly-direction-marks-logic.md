# 월성반 방위 길흉 마크 판정 로직

> 월성반(月星盤)에 배치된 구성(九星)에 대해, 본명성(main_star)을 기준으로 각 방위의 **길(吉)·흉(凶)·중립** 을 판정하는 파이프라인의 설계 및 구현 사양.

## 아키텍처 (OCP 파이프라인)

판정은 **3단계 서비스 체인**으로 구성된다. 각 서비스는 독립적이어서 추가·삭제 시 기존 코드의 변경이 필요 없다 (OCP: 개방/폐쇄 원칙).

```
StarGridPattern.get_fortune_status()     ← 모델 레이어: 6흉살만 판정
    ↓
FiveElementsFortuneService.enrich()      ← 도메인 서비스: 오행 상생으로 길방 판정
    ↓
AdditionalDirectionMarksService.enrich() ← 도메인 서비스: 위치 기반 룰로 보정
    ↓
fortune_level 확정 → 프론트엔드 전달
```

---

## Stage 1: 6흉살 판정 (`StarGridPattern.get_fortune_status()`)

방위가 흉(凶)인지를 **6종의 흉살 마크**로 판정한다. 1개라도 해당되면 `inauspicious`.

| 마크 | 판정 로직 | 코드 mark 값 |
|------|----------|-------------|
| **오황살 (五黄殺)** | 방위성 = 5 | `five_yellow` |
| **암검살 (暗剣殺)** | 방위성 = 중궁성의 반대성 (합계 10) | `dark_sword` |
| **본명살 (本命殺)** | 방위성 = 본명성 | `main_star` |
| **월명살 (月命殺)** | 방위성 = 월명성 | `month_star` |
| **파 (破)** | 방위 = 월지(月支)의 반대 방향 | `opposite_zodiac` |
| **수화살 (水火殺)** | 本命星과 方位星이 水↔火 상극 관계 | `water_fire` |

### 추가 흉살 (반대 위치)

| 마크 | 판정 로직 | 코드 mark 값 |
|------|----------|-------------|
| **본명적살 (本命的殺)** | 본명살의 반대 방위 | `main_star_opposite` |
| **월명적살 (月命的殺)** | 월명살의 반대 방위 | `month_star_opposite` |

> **소스파일**: [`backend/core/models/star_grid_pattern.py`](../backend/core/models/star_grid_pattern.py)

---

## Stage 2: 오행 상생 fortune_level 판정 (`FiveElementsFortuneService`)

흉살에 해당하지 않는 방위에 대해, **본명성과 방위성의 오행 관계**로 길방 레벨을 결정한다.

### 구성 → 오행 매핑

| 성 | 명칭 | 오행 |
|----|------|------|
| 1 | 일백수성 (一白水星) | 수(水) |
| 2 | 이흑토성 (二黒土星) | 토(土) |
| 3 | 삼벽목성 (三碧木星) | 목(木) |
| 4 | 사록목성 (四緑木星) | 목(木) |
| 5 | 오황토성 (五黄土星) | 토(土) |
| 6 | 육백금성 (六白金星) | 금(金) |
| 7 | 칠적금성 (七赤金星) | 금(金) |
| 8 | 팔백토성 (八白土星) | 토(土) |
| 9 | 구자화성 (九紫火星) | 화(火) |

### 상생 관계 (순환)

```
목(木) → 화(火) → 토(土) → 금(金) → 수(水) → 목(木)
(목생화)   (화생토)   (토생금)   (금생수)   (수생목)
```

### fortune_level 결정 규칙

| Level | 조건 | 예시 (본명성=7적금성) |
|-------|------|---------------------|
| **best_auspicious** (최대길방) | 방위성의 오행 → 본명성의 오행을 생함 | 토→금: 2,8(토)이 7(금)을 생함 |
| **auspicious** (길방) | 본명성의 오행 → 방위성의 오행을 생함 | 금→수: 7(금)이 1(수)을 생함 |
| **auspicious** (길방) | 동일 오행 (비화) | 7(금) = 6(금) |
| **neutral** (중립) | 상극 등, 상생이 아닌 관계 | 목↔금(상극): 3,4 vs 7 |

> **소스파일**: [`backend/apps/ninestarki/domain/services/five_elements_fortune_service.py`](../backend/apps/ninestarki/domain/services/five_elements_fortune_service.py)

---

## Stage 3: 추가 방위 마크 (`AdditionalDirectionMarksService`)

오행으로 길방이라 판정된 방위에 대해, **위치 기반 룰**로 다운그레이드한다.

### 3-1. 정위대충 (定位対冲)

각 별에는 고정된 「정위(홈 방위)」가 있다. 별이 홈 방위의 **반대편**에 배치되면 정위대충이 발생하여, 길방 → **중립**으로 다운그레이드된다.

| 성 | 정위 (홈) | 정위대충 발생 방위 |
|----|----------|-------------------|
| 1 | 북 (North) | 남 (South) |
| 2 | 남서 (Southwest) | 북동 (Northeast) |
| 3 | 동 (East) | 서 (West) |
| 4 | 동남 (Southeast) | 북서 (Northwest) |
| 6 | 북서 (Northwest) | 동남 (Southeast) |
| 7 | 서 (West) | 동 (East) |
| 8 | 북동 (Northeast) | 남서 (Southwest) |
| 9 | 남 (South) | 북 (North) |

> 5(오황토성)는 중궁 고정이므로 정위대충 해당 없음.

### 3-2. 소아살 (小児殺)

월지(十二支)에 따라 결정되는 흉방위. 해당 방위가 길방인 경우, **중립**으로 다운그레이드한다.

| 월지 | 소아살 방위 |
|------|-----------|
| 인(寅) | 남 (South) |
| 묘(卯) | 북서 (Northwest) |
| 진(辰) | 서 (West) |
| 사(巳) | 동남 (Southeast) |
| 오(午) | 북 (North) |
| 미(未) | 남서 (Southwest) |
| 신(申) | 동 (East) |
| 유(酉) | 북동 (Northeast) |
| 술(戌) | 남 (South) |
| 해(亥) | 북서 (Northwest) |
| 자(子) | 서 (West) |
| 축(丑) | 동남 (Southeast) |

### 3-3. 천도 (天道)

월지에 따라 결정되는 특수 길방위. 현재는 **참고 정보로만** 표시되며, fortune_level 변경은 하지 않는다.

| 월지 | 천도 방위 |
|------|---------|
| 인(寅) | 북서 (Northwest) |
| 묘(卯) | 남서 (Southwest) |
| 진(辰) | 북 (North) |
| 사(巳) | 남서 (Southwest) |
| 오(午) | 북서 (Northwest) |
| 미(未) | 북 (North) |
| 신(申) | 남서 (Southwest) |
| 유(酉) | 북서 (Northwest) |
| 술(戌) | 북 (North) |
| 해(亥) | 남서 (Southwest) |
| 자(子) | 북서 (Northwest) |
| 축(丑) | 북 (North) |

> **소스파일**: [`backend/apps/ninestarki/domain/services/additional_direction_marks_service.py`](../backend/apps/ninestarki/domain/services/additional_direction_marks_service.py)

---

## 프론트엔드 표시

`fortune_level`에 따라 4단계 시각 표현을 수행한다.

| fortune_level | 아이콘 | 색상 | 배경색 |
|--------------|-------|------|--------|
| `best_auspicious` | ✿ | 금색 (#b8860b) | rgba(212, 175, 55, 0.12) |
| `auspicious` | ✿ | 녹색 (#3d7a56) | rgba(90, 138, 110, 0.10) |
| `neutral` | · | 회색 (#a0a0a0) | transparent |
| `inauspicious` | ✕ | 빨간 (#b04a46) | rgba(192, 82, 77, 0.08) |

> **소스파일**: [`frontend/src/components/features/results/MonthlyFortuneSection.tsx`](../frontend/src/components/features/results/MonthlyFortuneSection.tsx)

---

## 검증 예시 (2026년 3월, 본명성=7, 월명성=9)

월반 중궁성: 7 / 월지: 묘(卯)

```
SE(6) · 중립        ← 정위대충 (6의 정위=NW, 반대=SE)
S (2) ◎ 최대길방    ← 토→금 상생
SW(4) · 중립        ← 목↔금 상극 + 천도(참고)
E (5) × 흉          ← 오황살 + 월명적살
  [7 중궁]
W (9) × 흉          ← 암검살 + 월명살 + 파
NE(1) ○ 길방        ← 금→수 상생
N (3) · 중립        ← 목↔금 상극
NW(8) · 중립        ← 소아살 (묘월→NW)
```

---

## 확장 방법 (OCP)

새로운 룰을 추가하는 경우:

1. `backend/apps/ninestarki/domain/services/`에 새 서비스 파일 생성
2. `enrich(directions, ...)` 메서드 구현 (in-place로 dict 업데이트)
3. `MonthlyDirectionsUseCase`의 `execute()`에서 체인에 추가
4. `dependency_module.py`에 DI 등록

**기존 파일 수정 불필요** — UseCase 1줄 추가와 DI 등록만 하면 된다.
