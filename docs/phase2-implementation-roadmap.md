# Phase 2: 매칭 엔진 코어 — PR별 구현 로드맵

> **Issue**: #2 — Phase 2: 매칭 엔진 코어 개발 (Core Engine)  
> **설계서**: [phase2-matching-engine-design.md](phase2-matching-engine-design.md)  
> **최종 갱신**: 2026-03-03

---

## 진행 현황 요약

| PR | 제목 | 상태 | 비고 |
|----|------|------|------|
| **PR-A** | Value Objects + GogyoService | 🔀 머지 완료 | 의존성 없음 |
| **PR-B** | 스톤 데이터 + Repository + MessageCatalog | 🔀 머지 완료 | PR-A 이후 |
| **PR-C** | PowerStoneMatchingEngine (3-Layer 엔진) | 🔀 머지 완료 | PR-A, PR-B 이후 |
| **PR-D** | UseCase + Route 연동 + DI 바인딩 | 🔄 진행 중 | PR-C 이후 |

> 상태: ⬜ 미착수 / 🔄 진행 중 / ✅ 완료 / 🔀 머지 완료

---

## PR-A: Value Objects + GogyoService

> **브랜치**: `feat/phase2-vo-gogyo` (← `main`)  
> **의존성**: 없음 (독립 착수 가능)  
> **설계서 참조**: §3 Value Objects, §4-1 GogyoService

### 구현 항목

- [ ] `domain/value_objects/__init__.py`
- [ ] `domain/value_objects/locale.py` — `Locale` Enum (ja/ko/en)
- [ ] `domain/value_objects/gogyo.py` — `Gogyo`, `GogyoRelation` Enum
- [ ] `domain/value_objects/powerstone.py` — `PowerStone`, `StoneRecommendation`, `PowerStoneResult` frozen dataclass
- [ ] `domain/services/interfaces/gogyo_service_interface.py` — `IGogyoService` ABC
- [ ] `domain/services/gogyo_service.py` — `GogyoService` 구현
  - [ ] `STAR_TO_GOGYO` 매핑 (SSoT)
  - [ ] `DIRECTION_TO_GOGYO` 매핑 (SSoT)
  - [ ] `SOKOKU_TABLE` 상극 테이블 (SSoT)
  - [ ] `star_to_gogyo()`, `direction_to_gogyo()`, `get_relation()`, `get_counter_gogyo()`
- [ ] `domain/exceptions.py` — `PowerStoneMatchingError`, `NoAuspiciousDirectionError` 추가

### 테스트

- [ ] `tests/unit/test_gogyo_service.py`
  - [ ] `star_to_gogyo`: 1~9 전체 매핑
  - [ ] `get_counter_gogyo`: 5가지 상극 쌍
  - [ ] `get_relation`: 상생/상극/비화 각 1건+
  - [ ] 범위 밖 입력 → 예외 발생 확인
- [ ] `tests/unit/test_value_objects.py`
  - [ ] `PowerStone.get_name()` locale별 반환 + fallback

---

## PR-B: 스톤 데이터 + Repository + MessageCatalog

> **브랜치**: `feat/phase2-stone-data` (← PR-A 머지 후 `main`)  
> **의존성**: PR-A (Value Objects)  
> **설계서 참조**: §5 인터페이스, §9 데이터 설계

### 구현 항목

- [ ] `data/powerstone_catalog.json` — 스톤 마스터 데이터 (전체 20종, 다국어 names)
  - [ ] 水: aquamarine(주), lapis_lazuli, blue_topaz, onyx
  - [ ] 木: emerald(주), peridot, aventurine, jade
  - [ ] 火: garnet(주), carnelian, ruby, amethyst
  - [ ] 土: citrine(주), tigers_eye, yellow_jasper, smoky_quartz
  - [ ] 金: clear_quartz(주), moonstone, rose_quartz, pearl
  - [ ] `star_base_stones` 매핑 (본명성 1~9 → stone id)
- [ ] `domain/repositories/powerstone_repository_interface.py` — `IPowerStoneRepository` ABC
- [ ] `infrastructure/persistence/powerstone_repository.py` — `PowerStoneRepository` (JSON 로드)
  - [ ] `get_primary_by_gogyo()`
  - [ ] `get_secondaries_by_gogyo()`
  - [ ] `get_base_stone_for_star()`
- [ ] `data/messages/ja.json` — 일본어 메시지 번들 (기본) + `threat.<mark_code>` 키 포함
- [ ] `data/messages/ko.json` — 한국어 메시지 번들 + `threat.<mark_code>` 키 포함
- [ ] `data/messages/en.json` — 영어 메시지 번들 + `threat.<mark_code>` 키 포함
- [ ] `use_cases/interfaces/message_catalog_interface.py` — `IMessageCatalog` ABC
- [ ] `infrastructure/services/message_catalog.py` — `MessageCatalog` (JSON 로드 + resolve)
  - [ ] `resolve(key, locale, params)` — 키 조회 + 플레이스홀더 치환
  - [ ] fallback: 미지원 locale → ja

### 테스트

- [ ] `tests/unit/test_powerstone_repository.py`
  - [ ] 전체 20종 스톤 로드 확인
  - [ ] 오행별 주석/부석 분류 정확성
  - [ ] `get_base_stone_for_star` 1~9 전체 확인
- [ ] `tests/unit/test_message_catalog.py`
  - [ ] ja/ko/en 각 locale에서 올바른 문자열 반환
  - [ ] 미지원 locale → ja fallback
  - [ ] params 플레이스홀더 치환 ({direction} → "南")

---

## PR-C: PowerStoneMatchingEngine (3-Layer 엔진)

> **브랜치**: `feat/phase2-matching-engine` (← PR-B 머지 후 `main`)  
> **의존성**: PR-A (GogyoService), PR-B (Repository + Catalog)  
> **설계서 참조**: §4-2 PowerStoneMatchingEngine

### 구현 항목

- [ ] `domain/services/interfaces/powerstone_matching_engine_interface.py` — `IPowerStoneMatchingEngine` ABC
- [ ] `domain/services/powerstone_matching_engine.py` — `PowerStoneMatchingEngine`
  - [ ] `recommend()` 퍼사드 메서드
  - [ ] `_layer1_base_stone()` — 본명성 → 오행 → 기본석
  - [ ] `_layer2_monthly_stone()` — 최적 길방위 선택 알고리즘
    - [ ] 길방위 필터링 (is_auspicious)
    - [ ] 상성 우선순위 정렬 (GOOD > HIWA)
    - [ ] 동순위 방위 고정 우선순위 (S > E > SE > ...)
  - [ ] `_layer3_protection_stone()` — 최악 흉살 선택 알고리즘
    - [ ] 흉살 위험도 순위 (五黄殺 > 暗剣殺 > ...)
    - [ ] 상극 오행 결정
  - [ ] `_pick_stone()` — 중복 회피 (주석 → 부석[0] → 부석[1])

### 테스트

- [ ] `tests/unit/test_powerstone_matching_engine.py`
  - [ ] L1: 본명성 1~9 → 올바른 기본석
  - [ ] L2: 길방위 없음 → `NoAuspiciousDirectionError`
  - [ ] L2: 상성 GOOD 방위 우선 선택
  - [ ] L3: 五黄殺 > 暗剣殺 우선순위
  - [ ] 중복: L1=에메랄드(木), L2 후보도 木 → 부석 대체
  - [ ] 중복: 3개 전부 같은 오행 → 부석[0], 부석[1] 순차 대체
  - [ ] 결과: 항상 3개의 서로 다른 stone id 반환

---

## PR-D: UseCase + Route 연동 + DI 바인딩

> **브랜치**: `feat/phase2-usecase-route` (← PR-C 머지 후 `main`)  
> **의존성**: PR-C (전체 도메인 레이어 완료)  
> **설계서 참조**: §7 DI 바인딩, §8 파일 구조

### 구현 항목

- [ ] `use_cases/powerstone_recommendation_use_case.py` — `PowerStoneRecommendationUseCase`
  - [ ] `MonthlyDirectionsUseCase` 결과 수신 → `PowerStoneMatchingEngine.recommend()` 호출
  - [ ] `IMessageCatalog.resolve()` 로 locale별 응답 텍스트 생성
- [ ] `dependency_module.py` [MODIFY]
  - [ ] `IGogyoService` → `GogyoService` 바인딩
  - [ ] `IPowerStoneMatchingEngine` → `PowerStoneMatchingEngine` 바인딩
  - [ ] `IPowerStoneRepository` → `PowerStoneRepository` 바인딩
  - [ ] `IMessageCatalog` → `MessageCatalog` 바인딩
  - [ ] `PowerStoneRecommendationUseCase` 바인딩
- [ ] `routes/monthly_routes.py` [MODIFY]
  - [ ] `?lang=` 쿼리 파라미터 파싱 (기본값: `ja`) + `Locale` Enum 검증
  - [ ] 기존 directions 응답에 `power_stones` 필드 추가 (엔드포인트: `/monthly/monthly-board`)
  - [ ] locale별 스톤 이름, reason 텍스트 렌더링

### 테스트

- [ ] `tests/unit/test_powerstone_recommendation_use_case.py`
  - [ ] 정상 흐름: directions 결과 → 3개 스톤 추천
  - [ ] locale=ja / ko / en 별 응답 텍스트 확인
  - [ ] 에러 전파: NoAuspiciousDirectionError 상위 전달
- [ ] 기존 테스트 전량 통과 확인 (regression)

---

## 의존성 그래프

```
PR-A (VO + GogyoService)
  │
  ▼
PR-B (Data + Repository + MessageCatalog)
  │
  ▼
PR-C (MatchingEngine)
  │
  ▼
PR-D (UseCase + Route + DI)
```

> PR-A → PR-D 까지 **순차 머지** 방식. 각 PR 머지 후 `main`에서 다음 브랜치를 생성한다.
