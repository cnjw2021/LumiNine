### 모델 리팩토링 플레이북 (core/models → Domain Ports/Entities)

#### 목적
- ORM 모델에서 비즈니스/조회 로직을 제거하고, 도메인/인프라 경계(Ports/Adapters)를 명확히 한다.
- 라우트/유스케이스/도메인 서비스는 포트만 의존하도록 통일한다.

#### 적용 범위
- 대상 디렉터리: `backend/core/models/` 내 모든 모델
  - 우선순위: MonthlyDirections → StarGridPattern → DailyAstrology/HourlyStarZodiac/ZodiacGroup* → Attributes/Readings → Compatibility*

#### 표준 절차(각 모델 공통)
1) 현재 책임 식별
   - 모델 내 classmethod/쿼리/판정/기간계산/헬퍼를 나열한다.
   - “데이터 정의(컬럼/관계)” 외 책임은 분리 후보로 표시한다.

2) 포트 정의(Domain)
   - `apps/ninestarki/domain/repositories/<model>_repository_interface.py` 를 생성한다.
   - 읽기/쓰기 요구사항을 메서드로 선언 (예: `get_by_id`, `find_by_*`, `list`, `save`, `delete`).
   - 외부 IO/쿼리/집계가 필요한 동작은 포트 메서드로 표준화한다.

3) 인프라 구현(Adapters)
   - `apps/ninestarki/infrastructure/persistence/<model>_repository.py` 구현.
   - SQLAlchemy 쿼리는 어댑터 내부로만 배치. 세션은 `read_only_session`/`write_session` 사용.
   - ORM ↔ 도메인 엔티티 변환을 어댑터에서 수행.

4) 도메인 서비스/유스케이스 정리
   - 모델의 classmethod/비즈니스 판정/기간연산을 도메인 서비스로 이동.
   - 도메인 서비스는 포트/엔티티만 의존 (ORM import 금지). DI로 포트 주입.
   - 유스케이스는 조립과 입력검증/DTO 조립만 담당.

5) 라우트/컨트롤러 정리
   - new()/서비스 로케이터 금지, `@inject` 또는 DI 컨테이너로 의존성 주입.
   - 포트/유스케이스를 호출하고 결과만 반환.

6) 테스트 전략
   - 단위: pytest + `pytest-mock` autospec으로 포트 모킹, 경계/시나리오 `@pytest.mark.parametrize` 적용.
   - 통합: 테스트 DB + 시드(CSV)로 인프라 어댑터 검증.
   - Golden Master는 API/유스케이스 레벨에서 유지.

7) 마이그레이션/스키마
   - 인덱스/제약은 DDL 파일에서 관리. 모델에 중복 선언 금지.
   - 필요 시 별도 마이그레이션 SQL로 추가.

#### 체크리스트(각 모델 적용 시)
- [ ] 모델에서 classmethod/쿼리/판정 로직 제거
- [ ] 도메인 포트 정의(IRepository)
- [ ] 인프라 어댑터 구현 + 세션 경계 적용
- [ ] 도메인 서비스로 규칙 이동 (ORM import 금지)
- [ ] 유스케이스/라우트 DI 주입로 교체
- [ ] 단위/파라미터라이즈 테스트 추가, 통합 테스트(선택)
- [ ] 문서/아이콘(✅/🟡/⬜) 업데이트

#### 주의 사항
- 하드코딩/폴백 금지. 데이터 소스는 포트에서 주입받아 판단.
- 순환 의존 방지: 무거운 import는 팩토리/어댑터로 늦춘다.
- 시그니처는 “필요 데이터만” 주입받도록 단순화.


