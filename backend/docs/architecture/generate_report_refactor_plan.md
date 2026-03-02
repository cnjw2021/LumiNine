# Nine Star Ki Report - Clean Architecture 리팩토링 계획

## 배경
`GenerateReportUseCase`가 오케스트레이션 역할을 하면서도 ORM/인프라 레이어 접근, 의존성 생성, 표현계 매핑까지 포함하고 있어 SRP 및 경계 분리가 약합니다. 아래 단계로 점진 리팩토링을 진행합니다.

## 원칙
- UseCase는 의사결정과 시나리오 조합만 수행 (쿼리/저장/표현은 외부 위임)
- 의존성은 생성자가 주입(인터페이스 우선), 작업 스크립트/라우트는 경계
- DTO를 경계마다 명확히 정의

### 상태 아이콘
✅ 완료 · 🟡 진행 중 · ⬜ 대기

## 단계별 계획 (각 단계마다 PDF 생성 확인 및 커밋)

- ✅ 1) UseCase의 의존성 주입(부분) 도입 → 이후 필수 DI로 승격 완료
  - `calculate_stars_use_case`, `compatibility_service` 주입 및 내부 new 제거
- ✅ 2) 리딩 보강 쿼리 분리 → 도메인 포트 `IReadingQueryRepository` + 인프라 구현 도입, UseCase는 포트만 의존
- ✅ 3) 달력/절기/간지 의존 분리 → `ISolarStartsRepository`, `ISolarCalendarProvider` 주입 및 정적 호출 제거
- ✅ 4) 컨텍스트 빌더 도입 → `ReportContextBuilder`에서 표현계 매핑 수행
- ✅ 5) DTO 정리 → 입력/출력 DTO로 경계 타입 명시 (1차 완료)
  - `PartnerDTO`, `ReportInputDTO`, `ReportContextDTO`를 TypedDict로 도입
  - `/api/pdf-jobs` 라우트에 DTO 기반 검증/정규화 적용
  - `GenerateReportUseCase` ↔ `ReportContextBuilder` 간 DTO 경계 확립
  - 프론트엔드 PDF 요청은 최소 페이로드만 전달, 백엔드에서 재계산
- ✅ 6) 예외/로깅 정교화 → 단계별 예외 타입/메시지 표준화 (완료)
  - `/api/pdf-jobs`에 표준 에러 구조(code/message/fields, request_id 포함) 적용
  - `tasks.generate_pdf_task`에 job_id 기반 단계별 로깅(start/execute/save/success, error) 추가
  - 인프라 레이어(DB 조회) 예외를 `ExternalServiceError`로 변환: `ReadingQueryRepository`, `SolarStartsRepository`
  - UseCase 핵심 검증 실패 시 `ValidationError`/`DomainRuleViolation` 발생
  - 앱 전역 `AppError` 핸들러 및 예상치 못한 예외(500) 처리 추가
  - 프론트엔드 `X-Request-ID` 자동 주입(axios 인터셉터)로 추적성 강화

## 완료 기준
- RQ 작업과 라우트는 경계 역할만 수행
- UseCase는 도메인 서비스와 쿼리/리포지토리를 오케스트레이션
- 템플릿/표현 포맷은 빌더 레이어로 이동

## 추가 보완 사항 및 리팩토링 대상 (Backlog)

- ✅ 서비스 포트 표준화(Ports導入)
  - YearFortuneService / MonthFortuneService / StarAttributeService 등 도메인 인터페이스(`IYearFortuneService`, `IMonthFortuneService`, `IStarAttributeService`) 추가
  - 인프라/응용 구현은 어댑터로 분리하고 AppModule에서 인터페이스→実装をバインド

- ✅ DTO 도입(경계 타입 명시)
  - 입력: ReportInputDTO { fullName, birthdate, gender, targetYear, partner? }
  - 출력: ReportContextDTO 명시 타입 적용 및 템플릿 변수 정합 반영 완료
  - 라우트/UseCase/Renderer 경계를 DTO 기반으로 정리 완료

- ✅ DI 일원화
  - app.py / tasks.py의 수동 조립 최소화, Flask-Injector 바인딩으로 통일
  - UseCase 자체도 provider로 관리(테스트 시 모듈 스왑 용이)

- ✅ 트랜잭션/쿼리 경계 정리
  - 읽기 전용 쿼리와 상태 변경 경계를 분리
  - 필요 시 UseCase 단위로 트랜잭션 스코프 명확화
  - ✅ `read_only_session` 도입 및 적용 (ReadingQueryRepository, SolarStartsRepository, NineStarRepository, StarLifeGuidanceRepository, PermissionRepository[읽기])
  - ✅ 쓰기 경로에 `write_session` 적용 (UserRepository.save/delete, PermissionRepository.save)

– ✅ 테스트強化
  - 진행: GenerateReportUseCase 입력 검증 테스트(ValidationError), 파트너相性フローのノンエラー確認
  - 상세 변경(테스트 파일별):
    - `tests/test_generate_report_use_case_fakes.py`
      - `StarLifeGuidanceRepoFake`를 주입하여 `StarLifeGuidanceService`의 리포지토리 의존 해소
      - `DirectionMarksDomainService.get_direction_fortune`를 모키패치하여 앱 컨텍스트 의존 제거
      - 최소 입력으로 `execute_pdf`가 바이트를 반환하는지 검증
    - `tests/test_generate_report_validation.py`
      - ValidationError 경로(필수 필드 누락)에 대한 파라미터화 테스트 추가
      - `StarLifeGuidanceRepoFake` 주입 및 방향 판단 모키패치 적용
    - `tests/test_generate_report_partner.py`
      - 파트너 재계산/相性フロー에서 오류가 발생하지 않는지 검증
      - `StarLifeGuidanceRepoFake` 주입 및 방향 판단 모키패치 적용
    - `tests/test_generate_report_happy.py`
       - 해피패스(정상入力)で `execute_pdf` がバイト列を返すことを確認
       - 方向マークはモックでアプリコンテキスト依存を排除

- ✅ 表現(Formatting) 완전 분리
  - 날짜 문자열/간지/기간 포맷 등 표현 로직을 독립 포맷터로 분리 완료
  - 적용 파일: `apps/ninestarki/utils/formatters/date_formatter.py`, `zodiac_formatter.py`, `period_formatter.py`
  - `ReportContextBuilder`는 내부 포맷 로직 제거 후 포맷터 의존성만 사용

- ✅ 상수/기본값 주입화
  - 태어난 시각 미지정 시 기본값을 설정/환경(Config) 주입으로 전환: `DEFAULT_NOON_TIME` (기본: `12:00`)
  - 적용 파일: `core/config.py`(기본값 정의), `apps/ninestarki/tasks.py`, `apps/ninestarki/use_cases/generate_report_use_case.py`, `apps/ninestarki/routes/compatibility_routes.py`
  - 결과: 기본 동작은 동일(기본 `12:00` 유지). 배포환경에서 `DEFAULT_NOON_TIME`를 `HH:MM` 형식으로 재정의 가능
  - 환경 파일: `.env.development.backend`, `.env.production.backend` 에 `DEFAULT_NOON_TIME` 추가

- ✅ 잔여 직접 ORM참조 제거 점검
  - `GetFortuneDataUseCase`에서 `MonthlyDirections`/`StarGridPattern`/`SolarTerms` 직접 참조 제거
  - 포트導入: `IAnnualDirectionsRepository` + 実装 `AnnualDirectionsRepository`
  - DI 바인딩: `AppModule.configure()`에 포트 바인딩 추가
  - UseCase는 `IAnnualDirectionsRepository`経由で月盤/節気/盤パターンを取得

- ✅ 순환 참조 제거 및 조립 루트 도입
  - app.py를 `create_app()` 팩토리로 전환하고, 조립 루트에서만 DI/블루프린트/전역 핸들러 등록
  - 라우트/태스크 모듈 최상단에서 `app`/상호 모듈 import 금지: `/api/pdf-jobs` 라우트는 문자열 경로 enqueue로 전환
  - RQ 워커 진입점에서만 `create_app()` 호출 후 컨텍스트 관리 및 태스크 로딩
    - ✅ `apps.ninestarki.worker_entrypoint` 도입, `docker-compose(.dev).yml`의 rq-worker 커맨드 갱신 완료
    - ✅ `tasks.py`는 Flask 비의존(앱 컨텍스트 관리는 워커 엔트리포인트에서만 수행)
    - ✅ PDF ジェネレーターのグローバル app 参照を削除し、現行コンテキストのみに依存

### 운영 환경의 cron/logrotate 권한 처리
- ✅ Dockerfile(production)에서 컨테이너는 root로 시작하여 cron/logrotate를 정상 구동
- ✅ `start.sh`에서 cron 시작 및 logrotate 1회 실행 후, gunicorn은 `appuser`로 권한 다운그레이드하여 실행
- ✅ `/tmp/pdf` 디렉토리 생성 및 권한 보장(워커/앱 모두 쓰기 가능)

## 예외 설계 가이드 (Pythonic, Clean Architecture)

- 베이스 예외: `AppError(code, status, message, fields?, details?)`
- 서브클래스(소수):
  - `ValidationError(400)`, `NotFoundError(404)`, `DomainRuleViolation(422)`, `UnauthorizedError(401)`, `ForbiddenError(403)`, `ExternalServiceError(502)`
- 경계별 역할:
  - 도메인/UseCase: 의미 있는 도메인 예외만 raise (외부 라이브러리 예외는 포착 후 도메인 예외로 변환)
  - 라우트/RQ 워커: 예외 → 표준 응답(JSON)/로깅으로 변환, 재시도 정책 결정
  - 원인 보존: `raise NewError(...) from e`
- 표준 응답 형태(JSON):
  - `{ "error": { "code": "...", "message": "...", "fields": [..] }, "request_id": "..." }`

### 현재 적용 범위
- `/api/pdf-jobs` 라우트: `ValidationError` 사용, 블루프린트 에러 핸들러에서 표준 응답 변환
- `tasks.generate_pdf_task`: 단계별(job_id) 로깅 및 에러 로깅 표준화

### 완료된 적용 항목
- UseCase 내부에서 도메인/인프라 예외 분류 및 변환
- 외부 서비스/DB 실패를 `ExternalServiceError`로 표준화, 4xx/5xx 매핑 일원화
- `GetFortuneDataUseCase`에도 동일한 규칙 확장
  - ✅ 입력 검증 실패 시 `ValidationError`
  - ✅ 도메인상 부재/불일치는 `DomainRuleViolation`
  - ✅ ORM/외부 호출 실패는 `ExternalServiceError`
  - ✅ 응답 DTO 도입: `AnnualDirectionsResponseDTO`, `MonthAcquiredFortuneResponseDTO`

## 패키지 호환성 업데이트

- ✅ Flask 3.1.x + Flask-JWT-Extended 4.6.0로 업그레이드 (경고 제거)
  - 현재 고정 버전: Flask 3.1.2, Flask-JWT-Extended 4.6.0, Werkzeug 3.1.3, itsdangerous 2.2.0
- ✅ 상호 의존 패키지 점검 및 기본 테스트 통과 확인
  - 체크리스트: JWT 콜백/설정, 예외/핸들러 시그니처, 토큰 API, Werkzeug/itsdangerous 제약 (검증 완료)