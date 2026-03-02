# 백엔드 클린 아키텍처 가이드

본 문서는 백엔드 개발 시 엄격히 따라야 할 아키텍처 표준을 규정합니다. 모든 백엔드 개발은 본 가이드에 명시된, 도메인 주도 설계 기반의 계층 분리, DI, DTO/Validator, 예외, 리포지토리 경계 원칙을 반드시 준수해야 합니다.

## 아키텍처 의존성 규칙 다이어그램
+-----------------------------------------------------------------+
|                                                                 |
|   Presentation / Adapters (Flask Routes, Consumers)             |
|                                                                 |
|       +---------------------------------------------------+     |
|       |                                                   |     |
|       |   Application (Use Cases, DTOs)                   |     |
|       |                                                   |     |
|       |       +-------------------------------------+     |     |
|       |       |                                     |     |     |
|       |       |   Domain (Entities, VOs, Ports)     |     |     |
|       |       |                                     |     |     |
|       |       +-------------------------------------+     |     |
|       |                         |                         |     |
|       +-------------------------|-------------------------+     |
|                               (DIP)                             |
|       +-------------------------|-------------------------+     |
|       |                                                   |     |
|       |   Infrastructure (Repositories Impl, ORM)         |     |
|       |                                                   |     |
|       +---------------------------------------------------+     |
|                                                                 |
+-----------------------------------------------------------------+

      ------> 의존성 방향 (안쪽으로만 향해야 함) ------>


## 1) 계층과 책임
- Domain: 엔티티/밸류/도메인 서비스/포트(인터페이스)
- Application: 유스케이스, DTO/Validator, 컨텍스트 빌더
- Infrastructure: Repository/Provider(포트 구현), DB/외부 I/O, 매핑
- Presentation / Adapters: 외부 세계와의 상호작용 경계
  - Presentation(사용자 인터페이스): HTTP Controllers(웹 라우트), View/Template, CLI
  - Adapters(외부 시스템 연동): Message Queue Consumers, Schedulers/Crons, 외부 API 클라이언트, 파일/스토리지 어댑터, PDF Renderer 등

## 2) 핵심 원칙
- SRP: 클래스/모듈은 하나의 변경 이유만 가진다.
- DIP: 유스케이스는 포트에 의존, 구현은 인프라 어댑터로 분리.
- DTO/Validator: 경계 타입 명확화 및 검증 중앙화.
- 표준 예외: AppError 하위(`ValidationError`,`DomainRuleViolation`,`ExternalServiceError` 등) 사용.

## 3) 포트/리포지토리 경계
- 읽기 전용 쿼리 포트: 화면/리포트 최적화 DTO 반환(엔티티 강제 금지)
- 쓰기 포트: 엔티티/집계 단위의 저장/조회
- 매핑은 인프라에서만 수행(ORM Row ↔ 엔티티/DTO)

## 4) 유스케이스 오케스트레이션
- 입력 DTO 검증 → 포트 호출 → 도메인 서비스/엔티티 메서드 → 출력 DTO
- 도메인 규칙/판단/상태전이는 유스케이스 밖(엔티티/도메인 서비스)에 위치

## 5) 도메인 설계 상세
- 엔티티: 상태+행위. 내부에서 규칙 보장(판단/전이 메서드 포함)
- 밸류 오브젝트: 불변/형식검증. 기본형 남용 금지
- 도메인 서비스: I/O 없는 순수 계산/판단 로직
- DTO↔엔티티 변환: Application Factory에서 수행
- UoW: 인프라에서 세션 범위 제공, 유스케이스 단위 트랜잭션
- ACL: 외부/레거시 모델은 인프라에서 흡수, 도메인은 순수 타입 유지

## 6) 가드레일 체크리스트
- Presentation(HTTP Controllers): DTO 역직렬화 + 유스케이스 호출 + 예외→응답 변환만
- UseCases: 흐름 제어/포트 호출/도메인 호출만
- Domain: 계산/판단/전이 로직 포함, 외부 I/O 없음
- Infra: 쿼리 최적화/조인/매핑/UoW

## 7) 샘플 코드
- 엔티티/VO/도메인 서비스/포트/매퍼/유스케이스의 예시는 상세 가이드 참조

## 8) 백엔드 클린 아키텍처 설계 원칙/구조
- 핵심 원칙
  - **SRP(단일 책임)**: 클래스/모듈은 하나의 이유로만 변경
  - **DIP(의존 역전)**: 유스케이스는 인터페이스(포트)에 의존, 구현은 인프라 어댑터에 위치
  - **경계 분리**: Domain(엔티티/도메인 서비스/포트) ↔ Application(UseCase/DTO/Validator) ↔ Infrastructure(Repository/Provider/ORM/외부 I/O) ↔ Interface(Flask Routes/PDF Renderer)
  - **DTO/Validator**: 경계 입력/출력 타입 명확화, 통합 검증
  - **표준 예외**: `AppError` 하위(`ValidationError`, `DomainRuleViolation`, `ExternalServiceError` 등)로 통일, 라우트/워커에서 JSON/로그 표준화

- 디렉터리 예시
  - `domain/`
    - `entities/` 도메인 엔티티(불변 규칙)
    - `services/` 순수 도메인 서비스(외부 I/O 없음)
    - `repositories/` 포트 인터페이스(예: `IReadingQueryRepository`, `ISolarStartsRepository`)
  - `use_cases/`
    - 유스케이스(정책/흐름 오케스트레이션)
    - `dto/` 입력/컨텍스트/응답 DTO, `validators.py`
    - `context/` 표현 매핑(예: `ReportContextBuilder`)
  - `infrastructure/`
    - `persistence/` 포트 구현(ORM 접근, 예외 변환)
    - `services/` 외부 서비스 어댑터(예: SolarCalendarProvider)
    - `pdf/` HTML 렌더러/리소스 로더
  - `routes/` Flask 블루프린트(경계), 유스케이스 호출 + 표준 예외 응답

- DI/조립 루트
  - `app.py`의 `create_app()`에서 Injector(AppModule) 바인딩, 블루프린트 등록, 전역 에러 핸들러 설정
  - RQ 워커/라우트는 앱 인스턴스를 직접 import하지 말고, DI 또는 문자열 경로 사용

- 테스트 가이드
  - 포트 인터페이스 Fake/Stub으로 유스케이스 단위 테스트(정상/검증 실패/외부 실패 경로)

- 운영 표준
  - `X-Request-ID` 헤더로 추적성 확보(프론트 인터셉터)
  - 액세스/에러 로그 분리, 워커 job_id 기반 단계 로그

--------
(상세 가이드)

## 섹션 1) 도메인 설계 상세 가이드
- 목표: 라우트/유스케이스에 비즈니스 로직이 섞이지 않도록 하고, 도메인 층(엔티티/밸류/도메인 서비스)에 판단 로직을 집중시킨다.

### 섹션 1.1) 엔티티(Entity)는 단순 VO가 아니다
- 엔티티는 식별자와 라이프사이클을 가지며, 도메인 규칙을 “내부에서” 보장한다.
- 엔티티는 “상태 보유 + 행위 제공”이 기본. 계산/판단/상태전이 로직을 메서드로 가진다.

```python
# 예시: 사용자 계정 도메인 (설명용, ORM 비의존)
from dataclasses import dataclass
from typing import Optional, Set

@dataclass(frozen=True)
class UserId:
    value: int

@dataclass(frozen=True)
class Email:
    value: str
    # 생성 시 형식 검증 등 수행 가능

class UserAccount:
    """
    사용자 계정 엔티티.
    
    주의: 이 클래스의 인스턴스는 반드시 정적 팩토리 메서드인
    `register()` 또는 `create_by_admin()`을 통해서만 생성해야 함.
    __init__을 직접 호출하지 마시오.
    """
    def __init__(self, user_id: UserId, email: Email, is_admin: bool, is_superuser: bool, ...):
        self._id = user_id
        self._email = email
        self._is_admin = is_admin
        self._is_superuser = is_superuser
        # ...

    @staticmethod
    def register(email: Email, permissions: Set[str]) -> 'UserAccount':
        """시나리오 1: 일반 사용자가 스스로 회원 가입할 때 사용"""
        # 이 경로로는 절대 관리자를 만들 수 없도록 비즈니스 규칙을 강제
        return UserAccount(
            user_id=UserId(0),
            email=email,
            is_admin=False, # ✨ 규칙 강제
            is_superuser=False,
            permissions=permissions,
            # ...
        )

    @staticmethod
    def create_by_admin(email: Email, is_admin: bool, permissions: Set[str]) -> 'UserAccount':
        """시나리오 2: 관리자가 다른 사용자를 생성할 때 사용"""
        # 이 경로로는 is_admin 값을 명시적으로 받아 생성할 수 있음
        return UserAccount(
            user_id=UserId(0),
            email=email,
            is_admin=is_admin, # ✨ 외부로부터 값을 받음
            is_superuser=False, # 슈퍼유저는 관리자도 만들 수 없다고 가정
            permissions=permissions,
            # ...
        )

    @staticmethod
    def reconstitute(user_id: UserId, email: Email, is_admin: bool, ...) -> 'UserAccount':
        """DB 데이터로부터 기존 엔티티를 재구성할 때만 사용합니다."""
        # 이 메서드는 '생성' 시의 비즈니스 규칙을 검사할 필요가 없습니다.
        # DB에 이미 저장된 상태를 그대로 복원하는 것이 목적이기 때문입니다.
        return UserAccount(user_id, email, is_admin, ...)

    # 판단 로직(업무 규칙)
    def is_subscription_active(self, today_iso: str) -> bool:
        if self._is_superuser:
            return True
        if not (self._subscription_start and self._subscription_end):
            return False
        return self._subscription_start <= today_iso <= self._subscription_end

    def has_permission(self, code: str) -> bool:
        if self._is_superuser:
            return True
        if self._is_admin and code in {"user_view", "user_create", "user_edit", "user_delete", "data_management"}:
            return True
        return code in self._permissions

    # 상태 전이(불변 조건 보장)
    def grant_permission(self, code: str) -> None:
        if self._is_superuser:
            return
        self._permissions.add(code)
```

### 섹션 1.2) 밸류 오브젝트(Value Object)와 규칙
- 밸류는 동등성으로만 구분되고 불변으로 다룬다. 형식/범위 검증을 생성 시 수행한다.
- 날짜/시간/이메일/성별 등의 기본형을 직접 쓰지 말고 VO로 감싼다. 도메인 규칙 누수를 줄인다.

### 섹션 1.3) 도메인 서비스(Domain Service)
- 한 엔티티로 표현하기 어려운 규칙(여러 엔티티 협력, 외부 의존 없는 순수 계산)을 캡슐화.
- 예: 별자리 매칭 규칙, 방향 판단, 相性 스코어 계산 등. I/O는 없고, 순수 함수적이어야 한다.

```python
# 예시: 상성 점수 도메인 서비스(순수 계산)
class CompatibilityDomainService:
    @staticmethod
    def calculate_score(main_star: int, partner_star: int) -> int:
        base = 50
        delta = abs(main_star - partner_star)
        return max(0, base - 5 * delta)
```

### 섹션 1.4) 리포지토리(Port)와 도메인 사이의 경계
- 포트 인터페이스는 “도메인 언어”로 정의한다. ORM/SQL 스키마의 세부는 숨긴다.
- 읽기와 쓰기를 분리한다: 쿼리 전용(ReadModel/DTO) vs 명령/집계(엔티티 저장).

```python
# 읽기 전용 쿼리 포트(도메인 언어 기반 DTO 반환)
from typing import Protocol, Optional, TypedDict

class MonthlyReadingDTO(TypedDict):
    star_number: int
    title: str
    keywords: str
    description: str

class IReadingQueryRepository(Protocol):
    def get_monthly_star_reading(self, star_number: int) -> Optional[MonthlyReadingDTO]: ...
    def get_daily_star_reading(self, star_number: int) -> Optional[MonthlyReadingDTO]: ...

# 쓰기/집계 포트(엔티티 저장)
class IUserRepository(Protocol):
    def find_by_email(self, email: Email) -> Optional[UserAccount]: ...
    def save(self, user: UserAccount) -> UserAccount: ...
```

#### 매핑 전략
- Infrastructure 계층에서만 ORM 모델 ↔ 엔티티/DTO 매핑을 수행한다.
- 읽기: 성능/표현계 요구가 크면 ReadModel/DTO를 직접 반환(엔티티 강제 금지).
- 쓰기: 엔티티/집계 단위로 저장. 입력 DTO → Factory → 엔티티 생성.

```python
# 인프라: ORM Row → 도메인 엔티티 매퍼(예시)
class UserMapper:
    @staticmethod
    def to_entity(row) -> UserAccount:
        # __init__ 대신 재구성 메서드를 호출합니다.
        return UserAccount.reconstitute(
            user_id=UserId(row.id),
            email=Email(row.email),
            # ...
        )
```

### 섹션 2) 유스케이스는 오케스트레이션만
- 입력 DTO를 검증 → 포트 호출(쿼리/저장) → 도메인 서비스/엔티티 메서드 호출 → 출력 DTO 조합.
- 규칙/판단은 유스케이스에 두지 않는다. 유스케이스는 “흐름 제어”만 맡는다.

```python
# 예시: 로그인 유스케이스(오케스트레이션만)
class LoginUseCase:
    def __init__(self, user_repo: IUserRepository):
        self._users = user_repo

    def execute(self, email_str: str, password: str) -> dict:
        user = self._users.find_by_email(Email(email_str))
        if not user:
            raise ValidationError("USER_NOT_FOUND")
        # 도메인 규칙: 구독/권한 판단은 엔티티 메서드 사용
        return {"user_id": user._id.value, "is_admin": user._is_admin}
```

### 섹션 3) Command/Query 분리(CQRS 경량 적용)
- Query: 화면 표시/보고서 목적. ReadModel/DTO를 쿼리 포트로 직접 반환(템플릿 최적화).
- Command: 상태 변화/검증. 엔티티/집계 단위로 처리, 저장은 쓰기 리포지토리 포트로.

### 섹션 4) 입력 DTO ↔ 엔티티 변환
- DTO는 경계용 타입이며, 도메인 내부로 가져가지 않는다.
- 변환은 “애플리케이션 계층의 Factory”에서 수행. 검증 실패는 `ValidationError`, 규칙 위반은 `DomainRuleViolation`.

```python
# use_cases/create_user.py
class CreateUserByAdminUseCase:
    def execute(self, command: CreateUserCommand): # command는 DTO
        # DTO의 원시 값을 Value Object로 변환
        email_vo = Email(command.email) 
        
        # 엔티티의 팩토리 메서드를 직접 호출
        new_user = UserAccount.create_by_admin(
            email=email_vo,
            is_admin=command.is_admin,
            permissions=set(command.permissions)
        )
        # ...
```

### 섹션 5) 트랜잭션/단위작업(Unit of Work) 경계
- 단일 유스케이스 내에서 여러 리포지토리 호출이 필요하면, 인프라 계층에서 UoW(세션 범위)를 제공.
- 유스케이스 시작~끝이 하나의 트랜잭션 경계가 되도록 조율.

# infrastructure/uow.py (UoW 구현 예시)
```python
class UnitOfWork:
    def __enter__(self):
        self.session = db.session() # 세션 시작
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback() # 예외 시 롤백
        else:
            self.session.commit() # 성공 시 커밋
        self.session.close()

# use_cases/some_use_case.py (사용 예시)
class SomeUseCase:
    def execute(self, command: SomeCommand):
        with UnitOfWork(): # 유스케이스 실행을 트랜잭션으로 감싼다
            # ... repository.save(entity) ...
            # ... other_repository.update(other_entity) ...
```

### 섹션 6) 도메인 예외와 결과 타입
- 도메인 계층은 표준 예외(`DomainRuleViolation` 등)를 던지고, 경계(라우트/워커)에서 JSON 응답으로 변환.
- 복잡한 판단 결과는 명시적 Result VO로 반환(예: `CompatibilityResult(score:int, label:str)`).

### 섹션 7) 반부패 계층(ACL) 원칙
- 외부 API/레거시 모델은 인프라/ACL에서 흡수, 도메인에는 순수 타입만 전달.
- ORM 모델을 엔티티/유스케이스/라우트로 직접 전달 금지.

### 섹션 8) 라우트/유스케이스에 로직이 섞이지 않도록 하는 체크리스트
- 라우트는 DTO 역직렬화 + 유스케이스 호출 + 예외→응답 변환만
- 유스케이스는 흐름 제어/포트 호출/도메인 호출만
- 계산/판단/상태전이는 엔티티/도메인 서비스로 이동
- 쿼리 최적화/조인은 인프라(리포지토리)에서 해결

### 섹션 9) DTO 네이밍 컨벤션 구체화
- 유스케이스와의 관계를 명확히 하는 DTO 네이밍 규칙을 추가하면 가독성이 크게 향상됩니다.
- 입력: [UseCaseName]Command 또는 [UseCaseName]InputDTO
- 출력: [UseCaseName]Result 또는 [UseCaseName]OutputDTO
- 예시: RegisterUserCommand, RegisterUserResult

## 섹션 10) 테스트 아키텍처 및 전략
- 목표: 각 계층의 책임을 명확히 검증하고, 외부 의존성으로 인한 테스트의 불안정성을 제거하며, 비즈니스 로직 변경에 견고한 테스트 스위트를 구축한다.

10.1) 테스트 피라미드 원칙
- 우리는 "테스트 피라미드" 전략을 따른다. 이는 빠르고 격리된 단위 테스트를 가장 많이 작성하고, 느리고 통합된 E2E 테스트는 최소한으로 작성하는 것을 의미한다.
- 단위 테스트 (Unit Tests): 가장 빠르고, 가장 많아야 한다. 외부 I/O(DB, API) 없이 메모리 내에서 실행된다.

10.2) 계층별 테스트 전략
- Domain Layer (단위 테스트)
  - 대상: 엔티티, 밸류 오브젝트, 도메인 서비스
  - 전략: Mock(모의 객체)을 절대 사용하지 않는다. 이 계층은 순수한 비즈니스 규칙과 계산 로직만을 담고 있으므로, 외부 의존성 없이 직접 인스턴스화하여 검증한다.
  - 검증 내용:
    - 엔티티의 비즈니스 메서드(is_subscription_active, grant_permission 등)가 정확히 동작하는가?
    - 상태 전이 로직이 불변성을 해치지 않는가?
    - 밸류 오브젝트가 생성 시 검증 규칙을 올바르게 강제하는가?

- Application Layer (단위 테스트)
  - 대상: 유스케이스(Use Cases)
  - 전략: 유스케이스가 의존하는 모든 포트(Repository Interface)를 가짜(Fake) 또는 Mock으로 대체한다. 이를 통해 유스케이스의 오케스트레이션 로직만을 완벽히 격리하여 테스트한다.
  - 검증 내용:
    - 성공 경로: 정상적인 입력이 주어졌을 때, 올바른 순서로 포트를 호출하고 예상된 결과를 반환하는가?
  - 실패 경로:
    - 입력 DTO 검증(Validation)이 실패했을 때 ValidationError를 발생시키는가?
    - 포트에서 예외(예: UserNotFound)가 발생했을 때, 이를 올바르게 처리하거나 전파하는가?
    - 엔티티의 도메인 규칙(예: 권한 부족)을 위반했을 때 DomainRuleViolation 예외를 발생시키는가?

- Infrastructure Layer (통합 테스트)
  - 대상: 리포지토리 구현체, 외부 서비스 어댑터
  - 전략: 실제 데이터베이스(테스트용 DB 또는 인메모리 DB)나 실제 외부 API(테스트용 엔드포인트)와 연동하여 테스트한다.
  - 검증 내용:
    - 리포지토리의 ORM 쿼리가 올바른 SQL을 생성하는가?
    - DB 데이터와 도메인 엔티티 간의 매핑(reconstitute)이 양방향으로 정확히 동작하는가?
    - UoW(Unit of Work)가 트랜잭션을 올바르게 관리하는가? (Commit/Rollback)
    - 외부 API 클라이언트가 요청과 응답을 정확히 직렬화/역직렬화하는가?