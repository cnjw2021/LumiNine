# Phase 2: 매칭 엔진 코어 설계서

> **Issue**: #2 — Phase 2: 매칭 엔진 코어 개발 (Core Engine)  
> **작성일**: 2026-03-03  
> **참조 문서**: [월단위 길방위·파워스톤 매칭 설계서](monthly-direction-with-powerstone.md)  
> **적용 원칙**: SRP, SSoT, OCP, DIP, DRY, ISP  
> **기본 언어**: 日本語 (ja) — 확장: 한국어 (ko), English (en)

---

## 1. 스코프 및 목표

산출된 길흉방위의 오행 정보를 바탕으로, 3-Layer 파워스톤 추천 엔진을 개발한다.

| Layer | 이름 | 입력 | 변동 주기 |
|-------|------|------|----------|
| **L1** | 기본석 (基本石) | 본명성 → 오행 | 평생 고정 |
| **L2** | 월운석 (月運石) | 최적 길방위 → 오행 | 매월 변동 |
| **L3** | 호신석 (護身石) | 최악 흉방위 → 상극 오행 | 매월 변동 |

최종 출력은 **항상 서로 다른 3개의 파워스톤**, 중복 회피 알고리즘을 포함한다.

### i18n 목표
- **기본 언어**: 일본어 (`ja`) — 서비스의 주요 타깃 시장
- **확장 대상**: 한국어 (`ko`), 영어 (`en`)
- **원칙**: 도메인 로직은 언어 무관(language-agnostic), 텍스트 렌더링은 Presentation Layer에서 locale 파라미터로 결정

---

## 2. 아키텍처 레이어 구조

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Presentation Layer (presentation/ + routes/)                                │
│   routes/monthly_routes.py            [Controller] 기존 /monthly/monthly-board 연계 │
│   presentation/                       [Presenter] 응답 포맷팅 담당         │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │ depends on
┌────────────────────────────▼────────────────────────────────────────────────┐
│ Application Layer (use_cases/)                                              │
│   PowerStoneRecommendationUseCase  [NEW]                                    │
│   MonthlyDirectionsUseCase         [기존 — /monthly/monthly-board 에서 사용] │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │ depends on (interfaces only)
┌────────────────────────────▼────────────────────────────────────┐
│ Domain Layer (domain/)                                            │
│                                                                   │
│  services/                                                        │
│    GogyoService                       [NEW] 오행 판별·상극 유틸    │
│    PowerStoneMatchingEngine           [NEW] 3-Layer 매칭 엔진      │
│                                                                   │
│  services/interfaces/                                             │
│    IGogyoService                      [NEW]                       │
│    IPowerStoneMatchingEngine          [NEW]                       │
│                                                                   │
│  repositories/                                                     │
│    IPowerStoneRepository              [NEW] (기존 컨벤션 준수)      │
│                                                                   │
│  value_objects/                                                    │
│    Locale (Enum)                      [NEW] ja·ko·en               │
│    Gogyo (Enum)                       [NEW] 木·火·土·金·水         │
│    GogyoRelation (Enum)               [NEW] 相生·相剋·比和         │
│    PowerStone (Frozen Dataclass)      [NEW] 다국어 name 포함       │
│    StoneRecommendation (Frozen DC)    [NEW]                       │
│    PowerStoneResult (Frozen DC)       [NEW] 3-Layer 결과 VO        │
│                                                                   │
│  exceptions.py                        [MODIFY] 예외 추가           │
│                                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │ depends on (interfaces only)
┌────────────────────────────▼────────────────────────────────────┐
│ Infrastructure Layer (infrastructure/)                                      │
│   persistence/PowerStoneRepository   [NEW] JSON 기반 정적 데이터              │
│   services/MessageCatalog            [NEW] i18n 메시지 카탈로그                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 의존성 흐름 (DIP 준수)

```mermaid
graph TD
    UC[PowerStoneRecommendationUseCase] --> IGS[IGogyoService]
    UC --> IPSM[IPowerStoneMatchingEngine]
    UC --> IPSR[IPowerStoneRepository]
    
    GS[GogyoService] -.implements.-> IGS
    PSME[PowerStoneMatchingEngine] -.implements.-> IPSM
    PSR[PowerStoneRepository] -.implements.-> IPSR
    
    PSME --> IGS
    PSME --> IPSR
```

> **DIP**: 유즈케이스와 도메인 서비스는 인터페이스(I~)에만 의존한다. 구현체는 DI 컨테이너(`dependency_module.py`)에서 바인딩한다.

---

## 3. Value Objects (불변 도메인 모델)

### 3-0. `Locale` (지원 언어 Enum)

```python
# domain/value_objects/locale.py
class Locale(str, Enum):
    """지원 언어 — API 요청 시 Accept-Language 또는 ?lang= 파라미터로 결정."""
    JA = "ja"   # 日本語 (기본값)
    KO = "ko"   # 한국어
    EN = "en"   # English
```

> **설계 결정**: `Locale`은 Value Object로 도메인 레이어에 위치하되, 도메인 로직 자체에는 영향을 주지 않는다. `Locale`이 소비되는 지점은 **Presentation Layer**(라우트)와 **Infrastructure Layer**(메시지 카탈로그)이다.

### 3-1. `Gogyo` (오행 Enum) — SSoT

```python
# domain/value_objects/gogyo.py
class Gogyo(str, Enum):
    """오행(五行) — 프로젝트 전체에서 유일한 오행 정의 (SSoT)."""
    WOOD  = "木"
    FIRE  = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"
```

### 3-2. `GogyoRelation` (오행 관계 Enum)

```python
class GogyoRelation(str, Enum):
    SOJO  = "相生"   # 서로 도움 (생하는 관계)
    SOKOKU = "相剋"  # 서로 억제 (극하는 관계)
    HIWA   = "比和"  # 같은 오행
```

### 3-3. `PowerStone` (파워스톤 VO) — 다국어 이름 포함

```python
@dataclass(frozen=True)
class PowerStone:
    """단일 파워스톤 정보 (불변). 이름은 locale별로 보유."""
    id: str                          # "emerald", "garnet" 등 고유 식별자
    names: Dict[str, str]            # {"ja": "エメラルド", "ko": "에메랄드", "en": "Emerald"}
    gogyo: Gogyo                     # 대응 오행
    is_primary: bool                 # 해당 오행의 주석 여부

    def get_name(self, locale: str = "ja") -> str:
        """지정 locale의 이름 반환. fallback: locale → ja → 첫 번째 값."""
        return self.names.get(locale) or self.names.get("ja") or next(iter(self.names.values()))
```

### 3-4. `StoneRecommendation` (레이어별 추천 결과 VO)

```python
@dataclass(frozen=True)
class StoneRecommendation:
    """단일 레이어의 추천 결과. reason_key 를 통해 다국어 사유 지원."""
    stone: PowerStone
    layer: str                         # "base" | "monthly" | "protection"
    gogyo: Gogyo                       # 매칭에 사용된 오행
    reason_key: str                    # 메시지 카탈로그 키 (예: "reason.base.wood")
    reason_params: Dict[str, str] = field(default_factory=dict)  # 플레이스홀더 치환값
    direction: Optional[str] = None    # 관련 방위 (L2/L3)
    threat_mark: Optional[str] = None  # 관련 흉살 (L3)
```

> **i18n 설계 포인트**: 도메인 레이어는 **`reason_key`**(메시지 키)만 생성한다. 실제 번역 문자열로의 변환은 Presentation Layer에서 `MessageCatalog.resolve(key, locale, params)` 호출로 수행한다. 이로써 도메인 로직은 완전히 **language-agnostic** 하게 유지된다.

### 3-5. `PowerStoneResult` (최종 3-Layer 결과 VO)

```python
@dataclass(frozen=True)
class PowerStoneResult:
    """3-Layer 파워스톤 추천 최종 결과."""
    base_stone: StoneRecommendation      # L1 기본석
    monthly_stone: StoneRecommendation   # L2 월운석
    protection_stone: StoneRecommendation # L3 호신석
```

---

## 4. 도메인 서비스 상세 설계

### 4-1. `GogyoService` — 오행 판별·상극 유틸리티 (SRP)

> **책임**: 오행 관련 순수 비즈니스 로직만 담당. 외부 I/O 없음.

```python
# domain/services/gogyo_service.py
class GogyoService(IGogyoService):

    # ── 매핑 테이블 (SSoT) ──────────────────────
    STAR_TO_GOGYO: Final[Dict[int, Gogyo]] = {
        1: Gogyo.WATER, 2: Gogyo.EARTH, 3: Gogyo.WOOD,
        4: Gogyo.WOOD,  5: Gogyo.EARTH, 6: Gogyo.METAL,
        7: Gogyo.METAL, 8: Gogyo.EARTH, 9: Gogyo.FIRE,
    }

    DIRECTION_TO_GOGYO: Final[Dict[str, Gogyo]] = {
        "north": Gogyo.WATER, "northeast": Gogyo.EARTH,
        "east": Gogyo.WOOD,  "southeast": Gogyo.WOOD,
        "south": Gogyo.FIRE,  "southwest": Gogyo.EARTH,
        "west": Gogyo.METAL, "northwest": Gogyo.METAL,
    }

    # ── 상극 테이블 (SSoT) ──────────────────────
    # key 를 극하는(억제하는) 오행
    SOKOKU_TABLE: Final[Dict[Gogyo, Gogyo]] = {
        Gogyo.WATER: Gogyo.EARTH,   # 土剋水
        Gogyo.WOOD:  Gogyo.METAL,   # 金剋木
        Gogyo.FIRE:  Gogyo.WATER,   # 水剋火
        Gogyo.EARTH: Gogyo.WOOD,    # 木剋土
        Gogyo.METAL: Gogyo.FIRE,    # 火剋金
    }

    # ── 공개 메서드 ──────────────────────────────
    def star_to_gogyo(self, star_number: int) -> Gogyo: ...
    def direction_to_gogyo(self, direction: str) -> Gogyo: ...
    def get_relation(self, a: Gogyo, b: Gogyo) -> GogyoRelation: ...
    def get_counter_gogyo(self, target: Gogyo) -> Gogyo: ...
```

### 4-2. `PowerStoneMatchingEngine` — 3-Layer 매칭 엔진 (OCP)

> **책임**: 길흉방위 판정 결과와 오행 서비스를 조합하여 3개의 스톤을 결정.  
> **OCP**: 각 Layer 는 독립 private 메서드로 분리 → Layer 4(일운석) 추가 시 기존 Layer 로직 변경을 최소화(퍼사드/결과 VO 확장 위주).

```python
# domain/services/powerstone_matching_engine.py
class PowerStoneMatchingEngine(IPowerStoneMatchingEngine):

    @inject
    def __init__(
        self,
        gogyo_service: IGogyoService,
        stone_repo: IPowerStoneRepository,
    ) -> None: ...

    def recommend(
        self,
        main_star: int,
        directions: Dict[str, Any],   # MonthlyDirections 결과 (locale 무관)
    ) -> PowerStoneResult:
        """3-Layer 추천 실행 (퍼사드 메서드)."""
        used_ids: Set[str] = set()

        base   = self._layer1_base_stone(main_star, used_ids)
        monthly = self._layer2_monthly_stone(main_star, directions, used_ids)
        protect = self._layer3_protection_stone(directions, used_ids)

        return PowerStoneResult(base, monthly, protect)

    # ── Layer 1: 기본석 ───────────────────────────
    def _layer1_base_stone(self, main_star: int, used: Set[str]) -> StoneRecommendation:
        """본명성 → 오행 → 기본석 결정."""
        ...

    # ── Layer 2: 월운석 ───────────────────────────
    def _layer2_monthly_stone(
        self, main_star: int, directions: Dict, used: Set[str]
    ) -> StoneRecommendation:
        """최적 길방위 선택 → 오행 → 월운석 결정."""
        ...

    # ── Layer 3: 호신석 ───────────────────────────
    def _layer3_protection_stone(
        self, directions: Dict, used: Set[str]
    ) -> StoneRecommendation:
        """최악 흉살 방위 → 상극 오행 → 호신석 결정."""
        ...

    # ── 중복 회피 ─────────────────────────────────
    def _pick_stone(self, gogyo: Gogyo, used: Set[str]) -> PowerStone:
        """주석 우선 선택, used 에 포함되면 부석으로 대체."""
        ...
```

#### Layer 2 최적 길방위 선택 알고리즘 (설계서 §4-2)

```
입력: directions (방위별 길흉 판정 결과)
  ↓
1. is_auspicious == True 인 방위 필터링
  ↓
2. 본명성과의 상성으로 정렬
   - GOOD(상생) > HIWA(比和) > 기타
  ↓
3. 동순위 → 방위 고정 우선순위: south > east > southeast > southwest > north > west > northeast > northwest
  ↓
4. 1순위 방위의 오행 → 월운석 오행으로 확정
```

#### Layer 3 최악 흉살 선택 알고리즘 (설계서 §4-2)

```
입력: directions (방위별 흉살 marks)
  ↓
1. 흉살 위험도 순위표로 각 방위의 최대 위험도 산출
   五黄殺(1) > 暗剣殺(2) > 本命殺(3) > 月命殺(4) > ...
  ↓
2. 가장 위험한 방위의 오행 확인
  ↓
3. 상극(相剋) 테이블로 억제 오행 결정
  ↓
4. 억제 오행의 주석 → 호신석으로 확정 (중복 시 부석 대체)
```

---

## 5. 인터페이스 정의 (ISP 준수)

각 인터페이스는 **최소한의 메서드**만 노출한다.

```python
# domain/services/interfaces/gogyo_service_interface.py
class IGogyoService(ABC):
    @abstractmethod
    def star_to_gogyo(self, star_number: int) -> Gogyo: ...
    @abstractmethod
    def direction_to_gogyo(self, direction: str) -> Gogyo: ...
    @abstractmethod
    def get_relation(self, a: Gogyo, b: Gogyo) -> GogyoRelation: ...
    @abstractmethod
    def get_counter_gogyo(self, target: Gogyo) -> Gogyo: ...
```

```python
# domain/services/interfaces/powerstone_matching_engine_interface.py
class IPowerStoneMatchingEngine(ABC):
    @abstractmethod
    def recommend(self, main_star: int, directions: Dict[str, Any]) -> PowerStoneResult: ...
```

```python
# domain/repositories/powerstone_repository_interface.py  ← 기존 컨벤션 위치
class IPowerStoneRepository(ABC):
    @abstractmethod
    def get_primary_by_gogyo(self, gogyo: Gogyo) -> PowerStone: ...
    @abstractmethod
    def get_secondaries_by_gogyo(self, gogyo: Gogyo) -> List[PowerStone]: ...
    @abstractmethod
    def get_base_stone_for_star(self, star_number: int) -> PowerStone: ...
```

```python
# use_cases/interfaces/message_catalog_interface.py  ← i18n 렌더링은 표현 계층 성격
class IMessageCatalog(ABC):
    @abstractmethod
    def resolve(self, key: str, locale: str = "ja", params: Optional[Dict[str, str]] = None) -> str:
        """메시지 키 + locale → 번역된 문자열 반환."""
        ...
```

> **배치 근거**: `IPowerStoneRepository`는 도메인 데이터 접근이므로 `domain/repositories/`에 배치 (기존 `monthly_directions_repository_interface.py` 등과 동일). `IMessageCatalog`는 i18n 렌더링(외부 시스템 성격)이므로 `use_cases/interfaces/`에 배치 (기존 `pdf_generator_interface.py` 등과 동일, `infrastructure/readme.txt` 원칙 준수).

---

## 6. 예외 클래스 추가 (기존 계층 확장)

예외 `message` 기본값은 기존 코드베이스 컨벤션(한국어)을 따른다. 클라이언트에는 `code`를 키로 프론트엔드에서 locale별 i18n 처리한다.

```python
# domain/exceptions.py  [MODIFY]

class PowerStoneMatchingError(NineStarKiError):
    """파워스톤 매칭 과정에서 발생하는 오류."""
    def __init__(self, message="파워스톤 매칭 오류가 발생했습니다.", *, details=None):
        super().__init__(message, code="POWERSTONE_MATCHING_ERROR", status=500, details=details)

class NoAuspiciousDirectionError(NineStarKiError):
    """길방위가 하나도 없어 월운석을 결정할 수 없는 경우."""
    def __init__(self, message="길방위를 찾을 수 없습니다.", *, details=None):
        super().__init__(message, code="NO_AUSPICIOUS_DIRECTION", status=422, details=details)
```

> **에러 응답 정책**: 예외 `message` 기본값은 기존 `NineStarKiError` 하위 클래스와 동일하게 **한국어**로 유지한다 (CODE_REVIEW_GUIDELINES §E4 준수). 다국어 에러 메시지가 필요한 경우 클라이언트에서 `code`를 키로 i18n 번들을 통해 locale별로 표시한다.

---

## 7. DI 바인딩 (`dependency_module.py`)

```python
# [MODIFY] dependency_module.py — Phase 2 추가 바인딩
binder.bind(IGogyoService, to=GogyoService, scope=singleton)
binder.bind(IPowerStoneMatchingEngine, to=PowerStoneMatchingEngine, scope=singleton)
binder.bind(IPowerStoneRepository, to=PowerStoneRepository, scope=singleton)
binder.bind(IMessageCatalog, to=MessageCatalog, scope=singleton)
binder.bind(PowerStoneRecommendationUseCase, to=PowerStoneRecommendationUseCase, scope=singleton)
```

> ⚠️ **CODE_REVIEW_GUIDELINES §D2 준수**: **도메인 서비스/리포지토리**는 인터페이스 키로만 바인딩하고, 구상 클래스를 직접 키로 쓰지 않는다. UseCase는 현재 정책상 구상 클래스 키로 바인딩하되, 필요 시 별도 인터페이스를 도입한다.

---

## 8. 파일 구조 (신규/수정 대상)

```
backend/apps/reading/
├── domain/
│   ├── value_objects/               [NEW 디렉토리]
│   │   ├── __init__.py
│   │   ├── locale.py                ← Locale Enum (ja, ko, en)
│   │   ├── gogyo.py                 ← Gogyo, GogyoRelation Enum
│   │   └── powerstone.py           ← PowerStone, StoneRecommendation, PowerStoneResult
│   ├── services/
│   │   ├── gogyo_service.py         [NEW] 오행 판별·상극 서비스
│   │   ├── powerstone_matching_engine.py  [NEW] 3-Layer 매칭 엔진
│   │   └── interfaces/
│   │       ├── gogyo_service_interface.py           [NEW]
│   │       └── powerstone_matching_engine_interface.py [NEW]
│   ├── repositories/
│   │   └── powerstone_repository_interface.py  [NEW] 기존 컨벤션 위치
│   └── exceptions.py               [MODIFY] 2개 예외 추가
├── infrastructure/
│   ├── persistence/
│   │   └── powerstone_repository.py [NEW] JSON 기반 정적 데이터 구현체
│   └── services/
│       └── message_catalog.py       [NEW] JSON 기반 i18n 메시지 카탈로그 구현체
├── use_cases/
│   ├── interfaces/
│   │   └── message_catalog_interface.py  [NEW] i18n 렌더링 인터페이스
│   └── powerstone_recommendation_use_case.py  [NEW]
├── presentation/                    [기존]
├── routes/
│   └── monthly_routes.py            [MODIFY] power_stones 필드 + locale 파라미터
├── dependency_module.py             [MODIFY] DI 바인딩 추가
└── data/
    ├── powerstone_catalog.json      [NEW] 스톤 마스터 데이터 (다국어 name)
    └── messages/                    [NEW 디렉토리] i18n 메시지 번들
        ├── ja.json                  ← 기본 언어
        ├── ko.json
        └── en.json
```

---

## 9. 데이터 설계

### 9-1. `powerstone_catalog.json` — 스톤 마스터 데이터 (다국어)

```json
{
  "stones": [
    {
      "id": "aquamarine",
      "names": { "ja": "アクアマリン", "ko": "아쿠아마린", "en": "Aquamarine" },
      "gogyo": "水",
      "is_primary": true
    },
    {
      "id": "lapis_lazuli",
      "names": { "ja": "ラピスラズリ", "ko": "라피스라즐리", "en": "Lapis Lazuli" },
      "gogyo": "水",
      "is_primary": false
    }
  ],
  "star_base_stones": {
    "1": "aquamarine", "2": "citrine",     "3": "emerald",
    "4": "peridot",    "5": "tigers_eye",  "6": "clear_quartz",
    "7": "rose_quartz","8": "smoky_quartz","9": "garnet"
  }
}
```

> **SSoT**: 스톤-오행 매핑, 본명성-기본석 매핑, 다국어 이름 모두 이 파일이 단일 원천.

### 9-2. `messages/{locale}.json` — i18n 메시지 번들

각 locale별 메시지 파일. `reason_key`와 UI 표시 텍스트를 매핑한다.

**`messages/ja.json`** (기본 언어):
```json
{
  "layer.base": "基本石",
  "layer.monthly": "月運石",
  "layer.protection": "護身石",
  "reason.base": "{star_name}の本命石。{meaning}",
  "reason.monthly": "今月の最良吉方位・{direction}({element})のエネルギーを取り込む石",
  "reason.protection": "今月最大の凶殺・{threat}が{direction}({threat_element})に位置。{counter_element}の力で凶気を抑制",
  "gogyo.木": "木", "gogyo.火": "火", "gogyo.土": "土", "gogyo.金": "金", "gogyo.水": "水",
  "direction.north": "北", "direction.south": "南", "direction.east": "東", "direction.west": "西",
  "direction.northeast": "北東", "direction.northwest": "北西", "direction.southeast": "南東", "direction.southwest": "南西",
  "threat.five_yellow": "五黄殺", "threat.dark_sword": "暗剣殺",
  "threat.main_star": "本命殺", "threat.month_star": "月命殺",
  "threat.water_fire": "水火殺", "threat.opposite_zodiac": "破",
  "threat.bad_star": "凶方星", "threat.main_opposite": "本命的殺",
  "threat.month_opposite": "月命的殺"
}
```

**`messages/ko.json`**:
```json
{
  "layer.base": "기본석",
  "layer.monthly": "월운석",
  "layer.protection": "호신석",
  "reason.base": "{star_name}의 본명석. {meaning}",
  "reason.monthly": "이달 최적 길방위 {direction}({element})의 에너지를 받는 돌",
  "reason.protection": "이달 가장 강한 흉살 {threat}이(가) {direction}({threat_element})에 위치. {counter_element}의 힘으로 흉기를 억제",
  "gogyo.木": "목", "gogyo.火": "화", "gogyo.土": "토", "gogyo.金": "금", "gogyo.水": "수",
  "direction.north": "북", "direction.south": "남", "direction.east": "동", "direction.west": "서",
  "direction.northeast": "북동", "direction.northwest": "북서", "direction.southeast": "남동", "direction.southwest": "남서",
  "threat.five_yellow": "오황살", "threat.dark_sword": "암검살",
  "threat.main_star": "본명살", "threat.month_star": "월명살",
  "threat.water_fire": "수화살", "threat.opposite_zodiac": "파",
  "threat.bad_star": "흉방성", "threat.main_opposite": "본명적살",
  "threat.month_opposite": "월명적살"
}
```

### 9-3. i18n 처리 흐름

```
[Domain Layer]                              [Presentation Layer]
PowerStoneMatchingEngine                    Route Handler
  │                                           │
  ├─ reason_key = "reason.monthly"           │
  ├─ reason_params = {                        │
  │    "direction": "south",                  │
  │    "element": "火"                        │
  │  }                                        │
  └─ StoneRecommendation ──────────────────➤ │
                                              ├─ locale = request.args.get("lang", "ja")
                                              ├─ direction表示名 = message_catalog.resolve("direction.south", locale)
                                              ├─ message_catalog.resolve(
                                              │    key="reason.monthly",
                                              │    locale=locale,
                                              │    params={"direction": "南", "element": "火"}
                                              │  )
                                              └─ → "今月の最良吉方位・南(火)のエネルギーを取り込む石"
```

> **핵심**: 도메인은 direction을 "south" 같은 문자열 코드로만 다루고, locale별 표시명("南"/"남"/"South")으로의 변환은 `MessageCatalog`이 `direction.south` 키를 resolve하여 처리한다.

---

## 10. 테스트 전략

| 대상 | 테스트 유형 | 파일 |
|------|-----------|------|
| `GogyoService` | 단위 (순수 로직) | `test_gogyo_service.py` |
| `PowerStoneMatchingEngine` | 단위 (Stub 주입) | `test_powerstone_matching_engine.py` |
| `PowerStoneRecommendationUseCase` | 통합 (Stub 주입) | `test_powerstone_recommendation_use_case.py` |
| 중복 회피 | 단위 (엣지 케이스) | `test_powerstone_matching_engine.py` |

### 핵심 테스트 케이스

```
[GogyoService]
- star_to_gogyo: 1~9 전체 매핑 확인
- get_counter_gogyo: 5가지 상극 쌍 검증
- get_relation: 상생/상극/비화 각 1건 이상

[PowerStoneMatchingEngine]
- L1: 본명성 1~9 에 대해 각각 올바른 기본석 반환
- L2: 길방위가 없는 경우 → NoAuspiciousDirectionError 발생
- L2: 길방위 중 상성 GOOD 인 방위가 우선 선택됨
- L3: 五黄殺 > 暗剣殺 우선순위 확인
- 중복: L1=에메랄드(木), L2 후보도 木(주석=에메랄드) → 부석 대체 확인
- 중복: L1·L2·L3 에서 3개 전부 같은 오행 → 부석[0], 부석[1] 순차 대체

[MessageCatalog / i18n]
- resolve: ja/ko/en 각 locale에서 올바른 문자열 반환
- resolve: 미지원 locale → ja (기본값) fallback
- resolve: params 치환 ({direction} → "南") 동작 확인
- PowerStone.get_name: locale별 이름 반환 + fallback 체인 확인
```

---

## 11. 클린 아키텍처 원칙 점검표

| 원칙 | 적용 | 설계 근거 |
|------|------|----------|
| **SRP** | `GogyoService`(오행) ↔ `PowerStoneMatchingEngine`(매칭) ↔ `MessageCatalog`(번역) 분리 | 단일 책임 |
| **OCP** | Layer별 private 메서드 분리 → Layer 4 추가 시 기존 코드 수정 불필요. 새 locale 추가 시 JSON 파일만 추가 | 확장 개방 |
| **DIP** | 유즈케이스/도메인 서비스는 인터페이스(I~)에만 의존 | 의존성 역전 |
| **ISP** | 인터페이스별 최소 메서드만 노출 (예: `IGogyoService` 4개, `IMessageCatalog` 1개 메서드) | 인터페이스 분리 |
| **DRY** | 오행 매핑·상극 테이블은 `GogyoService` 에 SSoT 로 단일 정의 | 반복 제거 |
| **SSoT** | 스톤 데이터 → `powerstone_catalog.json`, 오행 매핑 → `GogyoService`, 번역 → `messages/{locale}.json` | 단일 진실 원천 |

---

## 12. 구현 순서 (의존성 기반)

```
Step 1: Value Objects (locale.py, gogyo.py, powerstone.py)
    ↓    ── 의존성 없음, 단독 테스트 가능
Step 2: GogyoService + IGogyoService + 단위 테스트
    ↓    ── Value Objects 에만 의존
Step 3: powerstone_catalog.json + PowerStoneRepository + IPowerStoneRepository
    ↓    ── Value Objects 에만 의존
Step 4: messages/*.json + MessageCatalog + IMessageCatalog + 단위 테스트
    ↓    ── Locale VO 에만 의존
Step 5: PowerStoneMatchingEngine + IPowerStoneMatchingEngine + 단위 테스트
    ↓    ── GogyoService, PowerStoneRepository 인터페이스에 의존
Step 6: 예외 클래스 추가 (exceptions.py)
    ↓
Step 7: PowerStoneRecommendationUseCase + 통합 테스트
    ↓
Step 8: DI 바인딩 + 라우트 연동 (dependency_module.py, monthly_routes.py)
         ── 라우트에서 ?lang= 파라미터 파싱 + MessageCatalog 호출
```
