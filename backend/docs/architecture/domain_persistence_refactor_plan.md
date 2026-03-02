### 도메인 × 영속성 분리 리팩토링 방침 (클린 아키텍처)

#### 배경
현재 일부 비즈니스 로직이 ORM(SQLAlchemy) 모델에 근접/혼재되어 있어, 도메인 계층이 영속성 세부 사항에 영향을 받을 여지가 있습니다. 클린 아키텍처의 원칙(DIP)에 기반하여, 도메인의 독립성과 테스트 용이성/교체 용이성을 높입니다.

#### 핵심 원칙 (Principles)
-   도메인 엔티티/도메인 서비스는 ORM으로부터 독립적이어야 합니다 (ORM import 금지).
-   영속성은 인프라 계층의 책임입니다 (SQLAlchemy 모델/세션/쿼리는 인프라에 격리).
-   도메인은 포트(IRepository 등의 추상화)에만 의존하며, 구현은 어댑터로 제공합니다.
-   변환(ORM 모델 ⇄ 도메인 엔티티)은 인프라의 리포지토리 어댑터에서 수행합니다.

#### 적용 방식 (How)
1.  도메인에 '순수한' 엔티티(dataclass 등)를 생성합니다.
2.  도메인에 리포지토리 포트(IXXXRepository)를 정의합니다.
3.  인프라에서 포트 구현체(SQLAlchemy 모델 사용)를 생성합니다. 단, 구현체 내부에서 다른 어댑터/리포지토리를 `new()`로 직접 생성하지 말고, 반드시 생성자 주입(또는 DI 프로바이더)으로 주입받습니다. (일관 규칙: `AnnualDirectionsRepository(ISolarTermsRepository)`와 같이 포트 주입)
4.  유스케이스/도메인 서비스 내의 ORM 직접 참조를 포트 호출로 교체합니다.
5.  DI로 포트→구현체를 바인딩합니다.
6.  모든 계층에서 “의존성은 생성자 주입” 규칙을 유지합니다. 정적 헬퍼라도 외부 IO/쿼리를 포함하면 포트로 래핑 후 주입합니다.
7.  모든 참조가 포트를 통해 이루어지는 것을 확인한 후, 불필요한 ORM 직접 참조를 삭제합니다.

#### 기대 효과 (Effects)
-   DIP 준수를 통해 도메인의 독립성이 향상되고, DB/ORM 교체에 대한 내구성이 높아집니다.
-   테스트 용이성 개선 (Fake/Stub 리포지토리 주입이 용이해짐).
-   책임 분리로 가독성/변경 용이성이 향상됩니다.

---

### 모델별 리팩토링 계획 (core.models → Domain Ports/Entities)

**상태 아이콘**: ⬜ 미착수 / 🟡 진행 중 / ✅ 완료

-   ✅ **SolarTerms(절기)**:
    -   ✅ 도메인: `domain/entities/solar_term.py` 추가
    -   ✅ 포트: `domain/repositories/solar_terms_repository_interface.py` 추가 (`get_yearly_terms`/`get_term_by_month`/`get_term_by_date`/`get_spring_start`)
    -   ✅ 인프라: `infrastructure/persistence/solar_terms_repository.py` 구현
    -   ✅ 도메인: `domain/entities/solar_term.py` 추가
    -   ✅ 포트: `domain/repositories/solar_terms_repository_interface.py` 추가 (`get_yearly_terms`/`get_term_by_month`/`get_term_by_date`/`get_spring_start`)
    -   ✅ 인프라: `infrastructure/persistence/solar_terms_repository.py` 구현
    -   ✅ 참조 교체: `YearStarDomainService`/`GetFortuneDataUseCase`에서 직접 참조 제거
    -   ✅ 추가 완료: `AstrologyDataReader`가 절기/기간 계산에 도메인 서비스 사용(`AuspiciousCalendarService`), 6/1 폴백 제거 후 입춘 날짜/시간 기반으로 연성 산출
    -   ✅ 추가 완료: 절기 기반 기간·배열 정책(해당 연도 2~12월 + 익년 1월)을 `AuspiciousCalendarService`로 이전하여 도메인 규칙으로 캡슐화

-   ✅ **SolarStarts(입춘 정보)**:
    -   ✅ 포트: `ISolarStartsRepository` 정의 완료 (`get_by_year`)
    -   ✅ 인프라: `infrastructure/persistence/solar_starts_repository.py` 구현 (`read_only_session` 사용)
    -   ✅ 참조 교체: `YearFortuneService`/`YearStarDomainService`/`AstrologyDataReaderAdapter`에서 포트 경유 사용 확인 (직접 ORM 참조 제거)

-   🟡 **MonthlyDirections / StarGridPattern**: (일부는 AnnualDirectionsRepository에 흡수됨)
    -   🟡 직접 참조 부분 재검토 → 포트 경유로 통일（서비스/유스케이스에서 `IStarGridPatternRepository` 사용 유지 확인 중）
        -   ✅ `YearStarDomainService`: `StarGridPattern` 직접 참조 제거 → `IStarGridPatternRepository` 경유 완료
        -   ✅ `DirectionMarksDomainService`: `StarGridPattern` 직접 참조 제거 → `IStarGridPatternRepository` 경유 완료（DI 주입）
        -   ✅ `DirectionRuleEngine`: `StarGridPattern` 직접 의존 제거 → `IStarGridPatternRepository` DI 주입으로 전환 완료

---

### 라우트 이관 현황 (UseCase 경유) — 점진 적용/테스트 그린 유지

-   ✅ `/api/nine-star/month-star-readings`
    -   UseCase: `ReadingQueryUseCase`
    -   포트: `IReadingQueryRepository`
    -   상태: 라우트 연결 완료, 골든마스터 테스트 그린

-   ✅ `/api/nine-star/daily-star-readings`
    -   UseCase: `ReadingQueryUseCase`
    -   포트: `IReadingQueryRepository`
    -   상태: 라우트 연결 완료, 골든마스터 테스트 그린

-   ✅ `/api/nine-star/daily-star-reading`
    -   UseCase: `DailyStarReadingUseCase`（生年月日→日命星/星情報/リーディング返却）
    -   포트: `INineStarRepository`, `IReadingQueryRepository`
    -   상태: 라우트 연결 완료, 유닛/골든마스터 테스트 그린

-   ✅ `/api/nine-star/stars`
    -   UseCase: `StarCatalogUseCase`
    -   포트: `INineStarRepository`
    -   상태: 라우트 연결 완료, 스모크/GM 테스트 그린

-   ✅ `/api/nine-star/star-attributes`
    -   UseCase: `StarAttributeUseCase`
    -   상태: 라우트 연결 완료, 골든마스터 테스트 그린

---

### 運用ルール（重要）

1.  エンドポイント単位で最小変更→即テスト（ゴールデンマスター/ユニット）→グリーン確認→次へ
2.  ルートは UseCase のみ依存。UseCase は Domain Port にのみ依存。Infrastructure は Port 実装のみ（DIP）
3.  互換スキーマは UseCase で固定化（フィールド追加/削除はここで吸収）
4.  DI で依存を構成し、new()/サービスロケータは禁止（@inject/コンストラクタ注入）
5.  import はファイル先頭に集約（ランタイム/中間 import を排除して依存の明示性を確保）

-   ⬜ **DailyAstrology / HourlyStarZodiac / ZodiacGroupMember**:
-   ⬜ **Compatibility\* / AcquiredFortune\* 계열(절기 외)**:
-   ⬜ **그 외 `core/models/__init__.py` 경유 참조 재검토**:

> **비고**: 일괄적이 아닌, 유스케이스 단위로 교체→회귀 테스트 확인의 점진적 접근 방식을 채택합니다.

---

### NineStar 모델에 관한 시정 조치 (예외 정리)

-   **현상**: `apps/ninestarki/domain/entities/nine_star.py`에 SQLAlchemy 의존성이 포함되어 있음 (도메인 계층과 인프라 책임이 혼재)
-   **방침**: 클린 아키텍처에 맞춰 다음 시정 조치를 수행합니다.
    1.  도메인에 '순수한' `NineStar` 엔티티를 정의합니다 (ORM 의존성 없음).
    2.  도메인에 `INineStarRepository`(기존)를 유지/정비합니다.
    3.  인프라에 ORM 모델(`core/models` 하위)을 배치/유지하고, 리포지토리 어댑터에서 변환합니다.
    4.  도메인/유스케이스는 `INineStarRepository`만 사용합니다 (SQLAlchemy에 의존하지 않음).
    5.  모든 참조 교체 후, `domain/entities/nine_star.py`의 ORM 의존성을 제거합니다 (또는 파일 구성을 정리).

#### 체크리스트 (NineStar)
-   ⬜ 도메인 순수 엔티티 생성 (ORM import 없음)
-   🟡 기존 포트 `INineStarRepository` 경유로 취득/저장 통일
    -   현황: 라우트는 `StarCatalogUseCase` 경유로 포트 사용 완료. 도메인 엔티티/저장 쪽은 추가 이관 필요.
-   🟡 인프라의 리포지토리 어댑터에서 ORM↔도메인 변환 (to\_domain/from\_domain)
    -   현황: 읽기 경로 일부는 포트/어댑터 사용. 도메인 엔티티 변환 규약 정립 및 적용 필요.
-   🟡 도메인/유스케이스에서 SQLAlchemy 직접 참조 전부 폐지
    -   현황: `YearStarDomainService`/`DirectionMarksDomainService`/`DirectionRuleEngine`에서 직접 참조 제거 완료. NineStar 관련 잔존 참조 점검 필요.
-   ⬜ `domain/entities/nine_star.py`의 SQLAlchemy 정의를 삭제 또는 인프라 측으로 회귀
    -   현황: 미착수. 도메인 순수 엔티티 도입 후 정리 예정.

---

### 보완 메모 (최근反映)

-   DI/포트化:
    -   `YearStarDomainService` → `IStarGridPatternRepository` 주입 완료
    -   `DirectionMarksDomainService` → `IStarGridPatternRepository` 주입 완료
    -   `DirectionRuleEngine` → `IStarGridPatternRepository` 주입 완료
    -   `GenerateReportUseCase` → `DirectionMarksDomainService` 주입(옵션)으로 전환, DI 모듈 갱신
    -   `AuspiciousDatesDomainService` → `DirectionRuleEngine` 생성자 주입(옵션) 반영
-   import ポリシー: 모든 import는 파일 선두에 집약 (중간 import 제거)

---

### 실시 단계 (전체)
1.  대상 유스케이스의 동작을 골든 마스터/유닛 테스트로 고정합니다.
2.  도메인 엔티티/포트 추가 → 인프라 구현 → DI 바인딩
3.  참조 교체 (직접 ORM → 포트)
4.  기존 테스트 수정/보완, 회귀 테스트 확인
5.  직접 참조가 0이 된 모델부터 순서대로 `core.models` 의존성 축소/정리 (필요하면 삭제)

---

### 메모
-   기존의 `AnnualDirectionsRepository` 등 “인프라에 있지만 도메인에 가까운 의미”를 가진 어댑터는, 계속해서 포트 경유의 집약 포인트로서 활용합니다.
-   하드코딩(예: 월=2)은 금지. 의미 있는 이름의 API(`get_spring_start` 등)를 포트로 제공합니다.
-   라우트/컨트롤러에서는 의존성 new() 및 서비스 로케이터(injector.get 등) 사용을 금지하고, 함수 인자 DI 주입(@inject)만 사용합니다. 조립은 반드시 DI 모듈에서 수행합니다.