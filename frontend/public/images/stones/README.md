# 파워스톤 이미지 카탈로그 (30종)

AI 생성 보석 이미지. `stoneImageMap.ts` 유틸이 `stone_id` → 이미지 경로로 매핑한다.

## 분류

### 구성기학(NSK) 전용 — 8종

오행(五行) 기반 카탈로그(`powerstone_catalog.json`)에만 등록.
기본석(L6), 월운석(L7), 호신석(L8) 계산에 사용.

| stone_id | 한국명 | 용도 |
|----------|--------|------|
| `aquamarine` | 아쿠아마린 | star 1 기본석 |
| `aventurine` | 어벤츄린 | 오행 보완석 |
| `blue_topaz` | 블루 토파즈 | 오행 보완석 |
| `clear_quartz` | 수정(클리어 쿼츠) | star 5 기본석 |
| `jade` | 옥(제이드) | 오행 보완석 |
| `smoky_quartz` | 스모키 쿼츠 | star 8 기본석 |
| `tigers_eye` | 타이거 아이 | star 2/5 기본석 |
| `yellow_jasper` | 옐로우 재스퍼 | 오행 보완석 |

### 수비술(NUM) 전용 — 10종

행성(Planet) 기반 카탈로그(`numerology_powerstone_catalog.json`)에만 등록.
전체운(L1), 건강운(L2), 재물운(L3), 연애운(L4), 연운석(L5) 계산에 사용.

| stone_id | 한국명 | 주요 행성 |
|----------|--------|----------|
| `blue_sapphire` | 블루 사파이어 | 토성(Saturn) |
| `cats_eye` | 캐츠아이 | 케투(Ketu) |
| `diamond` | 다이아몬드 | 금성(Venus) |
| `green_aventurine` | 그린 어벤츄린 | 수성(Mercury) |
| `hessonite` | 헤소나이트 | 라후(Rahu) |
| `red_coral` | 레드 코랄 | 화성(Mars) |
| `sunstone` | 선스톤 | 태양(Sun) |
| `tiger_eye` | 타이거 아이 | 목성(Jupiter) |
| `turquoise` | 터키석 | 목성(Jupiter) |
| `yellow_sapphire` | 옐로우 사파이어 | 목성(Jupiter) |

> **참고:** `tiger_eye`(수비술)와 `tigers_eye`(구성기학)는 별도 stone_id로 관리됨.

### 공용 — 12종

양쪽 카탈로그 모두에 등록. 구성기학 오행석이면서 수비술 행성석이기도 한 스톤.

| stone_id | 한국명 |
|----------|--------|
| `amethyst` | 자수정 |
| `carnelian` | 카넬리안 |
| `citrine` | 시트린 |
| `emerald` | 에메랄드 |
| `garnet` | 가넷 |
| `lapis_lazuli` | 라피스 라줄리 |
| `moonstone` | 문스톤 |
| `onyx` | 오닉스 |
| `pearl` | 진주 |
| `peridot` | 페리도트 |
| `rose_quartz` | 로즈 쿼츠 |
| `ruby` | 루비 |

## 수비술 마스터넘버 매핑

Life Path Number가 마스터넘버(11, 22, 33)인 경우, 프로파일 수치는 그대로 보존하되
**스톤 매핑은 base number를 공유**한다 (`_to_stone_number()`):

| 마스터넘버 | base number | 공유 행성 |
|-----------|-------------|----------|
| 11 | 2 | 달(Moon) |
| 22 | 4 | 라후(Rahu) |
| 33 | 6 | 금성(Venus) |

향후 마스터넘버 전용 스톤 매핑이 필요하면 `numerology_powerstone_catalog.json`에
`"11"`, `"22"`, `"33"` 키를 추가하고 엔진의 `_to_stone_number()` 로직을 수정해야 한다.

## 커버리지

API가 반환할 수 있는 모든 `stone_id` 30종에 대해 이미지 **100% 커버**.
`stoneImageMap.ts`에서 unknown stone_id는 `clear_quartz.png`로 fallback.
