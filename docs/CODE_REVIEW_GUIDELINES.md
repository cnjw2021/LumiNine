# 코드 리뷰 교훈 & 코딩 가이드라인
> PR #9 에서 Copilot 리뷰를 통해 지적받은 77건의 코멘트를 분석·분류하여, 동일한 실수를 반복하지 않기 위한 **실전 체크리스트**입니다.
> 새로운 코드 작성 또는 리뷰 전에 반드시 훑어보세요.
>
> **§ 1~6**: 과거 리뷰에서 반복된 실수 기반 체크리스트
> **§ 7**: 올바른 코드를 위한 일반 점검 리스트
> **§ 8**: 클린 아키텍처 원칙 재점검 리스트

---

## 1. 예외 처리 (Exception Handling)

### ✅ DO — 올바른 패턴
```python
# 도메인 고유 예외 클래스를 정의하고, code/status/details 를 명시한다.
raise NineStarKiError(
    "절기 데이터를 찾을 수 없습니다.",
    status=422,
    code="SETSU_MONTH_NOT_FOUND",
    details="DB의 solar_terms 테이블에 해당 날짜 이전/당일 절기가 존재하는지 확인해 주세요.",
)
```

### ❌ DON'T — 반복된 실수
```python
# 1) 내장 예외를 그대로 사용 → 글로벌 에러 핸들러에서 잡히지 않음
raise ValueError("Invalid target_month")

# 2) 도메인 예외지만 status 생략 → 기본값 500 으로 응답
raise NineStarKiError("Invalid month_index")

# 3) 에러 메시지에 내부 변수명 노출 → 클라이언트 혼동
raise NineStarKiError(f"Invalid target_month: {v}")
#                      ^^^^^^^^^^^^ 외부 API 파라미터명은 month_index
```

### 📋 체크리스트
| # | 항목 | 근거 라운드 |
|---|------|-----------|
| E1 | `ValueError`, `KeyError` 등 내장 예외 대신 **도메인 전용 예외** 사용 | R3, R16 |
| E2 | 예외 생성 시 **`status`(HTTP), `code`(고유 식별자), `details`(디버깅 힌트)** 3개를 반드시 명시 | R4, R17 |
| E3 | 에러 메시지의 파라미터명은 **외부 API 인터페이스 기준**으로 표기 | R20 |
| E4 | 에러 메시지 언어를 **프로젝트 주 언어(한국어)로 통일** — 일본어/영어 혼재 금지 | R15 |
| E5 | 입력값 검증 실패 → **HTTP 422**, 데이터 미존재 → **HTTP 422**, 서버 내부 오류 → **HTTP 500** | R17 |

---

## 2. DI & 아키텍처 (Dependency Injection)

### ✅ DO
```python
# 인터페이스를 명시적으로 상속하고, DI 바인딩은 인터페이스 키로 단일화
class MonthlyBoardDomainService(IMonthlyBoardDomainService):
    ...

# dependency_module.py
binder.bind(IMonthlyBoardDomainService, to=MonthlyBoardDomainService, scope=singleton)
```

### ❌ DON'T
```python
# 1) 인터페이스 상속 누락 → 타입 안정성 상실, DI 바인딩과 불일치
class MonthlyBoardDomainService:  # ← IMonthlyBoardDomainService 누락!
    ...

# 2) 구상 클래스 + 인터페이스 이중 바인딩 → 서로 다른 싱글톤 인스턴스 생성 위험
binder.bind(MonthlyBoardDomainService, to=MonthlyBoardDomainService, scope=singleton)
binder.bind(IMonthlyBoardDomainService, to=MonthlyBoardDomainService, scope=singleton)
```

### 📋 체크리스트
| # | 항목 | 근거 라운드 |
|---|------|-----------|
| D1 | 구현 클래스는 반드시 해당 **인터페이스(I~)를 명시적으로 상속** 선언 | R14 |
| D2 | DI 바인딩은 **인터페이스 키로만 단일 등록** — 구상 클래스 직접 바인딩 금지 | R18 |
| D3 | 하드코딩 로직(예: `month == 1`) 대신 **리포지토리 메서드**(예: `get_spring_start()`) 활용 | R13 |

---

## 3. API 설계 & 파라미터 관리

### ✅ DO
```python
# 레거시 파라미터는 무조건 거절 (동시 전송 되어도)
if request.args.get('month') is not None:
    return jsonify({'error': "'month' 대신 'month_index'를 사용해주세요."}), 400
```

### ❌ DON'T
```python
# month_index 가 있으면 month 를 조용히 무시 → 클라이언트가 레거시 습관을 유지
if request.args.get('month') is not None and month_index is None:
    return ..., 400
```

### 📋 체크리스트
| # | 항목 | 근거 라운드 |
|---|------|-----------|
| A1 | 폐기(deprecated) 파라미터는 **무조건 400 거절** — 새 파라미터와 동시 전달 시에도 통과 금지 | R20 |
| A2 | 내부 변수명(`target_month`)과 외부 파라미터명(`month_index`)을 **엄격히 구분** | R20 |
| A3 | API 응답의 에러 메시지에는 **외부 파라미터명**만 포함 — 내부 구현 노출 금지 | R20 |

---

## 4. 테스트 품질 (Test Quality)

### ✅ DO
```python
# Mock/Stub 데이터가 도메인 불변조건(invariant)을 준수하도록 매핑
terms.append(_StubSolarTerm(
    year, month, solar_date, zodiac=zt,
    star_number=((month - 1) % 9) + 1,  # 1~9 범위 보장
))
```

### ❌ DON'T
```python
# month(2~12)를 star_number 에 그대로 대입 → 10~12월에서 도메인 불변조건(1~9) 위반
terms.append(_StubSolarTerm(year, month, solar_date, zodiac=zt, star_number=month))
```

### 📋 체크리스트
| # | 항목 | 근거 라운드 |
|---|------|-----------|
| T1 | Stub/Mock 데이터는 **도메인 불변조건**(범위, 형식, 관계)을 반드시 충족 | R15 |
| T2 | 도메인 서비스에 새 메서드/의존성 추가 시, 관련 **Stub에도 즉시 반영** | R6 |
| T3 | "현재 테스트가 우연히 통과"할 수 있는 데이터 설정 여부를 **적극적으로 검증** | R15 |

---

## 5. 코드 위생 (Code Hygiene)

### 📋 체크리스트
| # | 항목 | 근거 라운드 |
|---|------|-----------|
| H1 | 정의만 되고 호출되지 않는 **함수/변수(Dead Code)를 즉시 제거** | R18, R19 |
| H2 | `import` 문 작성 시 실제 사용하는 심볼만 포함 (예: `execFileSync` 누락 방지) | R12 |
| H3 | CLI 플래그의 `required`/`optional` 속성을 **실제 사용 시나리오와 일치**시킴 | R13 |
| H4 | 문자열 보간(`${}`)으로 GraphQL 쿼리를 조립하지 않음 — **`-f` 변수**로 파라미터화 | R11 |

---

## 6. 보안 (Security)

### ✅ DO
```javascript
// GraphQL 변수를 -f 로 안전하게 전달
execFileSync('gh', ['api', 'graphql', '-f', `query=${query}`, '-f', `threadId=${id}`]);
```

### ❌ DON'T
```javascript
// 문자열 보간으로 GraphQL 인젝션 취약점 발생
execSync(`gh api graphql -f query='mutation { ... threadId: "${id}" }'`);
```

### 📋 체크리스트
| # | 항목 | 근거 라운드 |
|---|------|-----------|
| S1 | 외부 입력이 포함된 쿼리는 반드시 **파라미터 바인딩** 방식으로 전달 | R11 |
| S2 | `execSync` 대신 **`execFileSync`** 사용으로 쉘 인젝션 방지 | R11 |

---

## 📌 코드 작성 전 최종 셀프 체크

새 코드를 작성하거나 PR 을 올리기 전에 아래 질문을 스스로에게 던져 보세요:

1. **예외를 throw 하는 곳이 있는가?**
   → `status`, `code`, `details` 가 모두 명시되었는가? 내장 예외를 쓰고 있지는 않은가?
2. **새 클래스를 만들었는가?**
   → 인터페이스를 정의/상속했는가? DI 바인딩을 추가했는가? 중복 바인딩은 없는가?
3. **API 엔드포인트를 변경했는가?**
   → 폐기 파라미터 방어 로직이 있는가? 에러 메시지에 내부 변수명이 새어나가지 않는가?
4. **테스트를 작성/수정했는가?**
   → Stub 데이터가 도메인 불변조건을 만족하는가? 새 메서드에 대한 Stub이 빠져있지 않은가?
5. **외부 명령을 실행하는가?**
   → `execFileSync`를 사용하는가? 파라미터가 안전하게 바인딩되고 있는가?
6. **사용하지 않는 코드가 남아있지 않은가?**
   → 미사용 함수, 변수, import 를 정리했는가?

---

## 7. 코드 작성 시 올바른 코드를 위한 점검 리스트

> 리뷰 지적을 최소화하고 올바른 코드를 작성하기 위해, 코드를 커밋하기 전에 반드시 확인해야 할 항목입니다.

### 7-1. 명명 & 가독성

| # | 항목 |
|---|------|
| N1 | 변수·함수·클래스명이 **역할을 즉시 파악**할 수 있도록 명명되었는가? (약어, 한 글자 변수 금지) |
| N2 | 매직 넘버/매직 문자열이 아닌 **상수(Constant)** 로 정의되었는가? |
| N3 | 함수가 **하나의 책임**만 수행하는가? (단일 책임 원칙, SRP) |
| N4 | 중첩 깊이가 3단계 이하인가? — 깊으면 **Guard Clause 또는 메서드 추출**로 리팩터링 |
| N5 | 주석이 "무엇(What)"이 아닌 **"왜(Why)"** 를 설명하고 있는가? |

### 7-2. 입력 검증 & 방어적 코딩

| # | 항목 |
|---|------|
| V1 | 외부 입력(API 파라미터, 파일, 환경변수)에 대해 **타입·범위·필수 여부**를 검증하는가? |
| V2 | `None`/`null`이 올 수 있는 값에 대해 **Null 안전성**을 확보했는가? |
| V3 | 컬렉션(리스트, 딕셔너리)이 **빈 값일 경우**를 처리했는가? |
| V4 | 경계값(0, 음수, 최대값, 빈 문자열)에 대한 **엣지 케이스**를 고려했는가? |
| V5 | 날짜/시간 처리 시 **타임존과 절기(setsu) 경계 조건**을 정확히 처리하는가? |

### 7-3. 에러 처리 & 로깅

| # | 항목 |
|---|------|
| L1 | 예외 발생 시 **근본 원인(root cause)을 추적**할 수 있는 충분한 정보가 로그에 포함되는가? |
| L2 | 예외를 삼키지(swallow) 않는가? — `except: pass` 또는 빈 `catch` 블록 금지 |
| L3 | 외부 서비스(DB, API) 호출 실패 시 적절한 **fallback 또는 재시도** 전략이 있는가? |
| L4 | 로그 레벨이 적절한가? (`DEBUG` → 개발 추적, `INFO` → 정상 흐름, `WARNING` → 주의, `ERROR` → 장애) |
| L5 | 로그에 **민감 정보**(비밀번호, 토큰, 개인정보)가 노출되지 않는가? |

### 7-4. 타입 안전성 & 일관성

| # | 항목 |
|---|------|
| Y1 | Python → **타입 힌트**(`def func(x: int) -> str:`)가 명시되었는가? |
| Y2 | TypeScript → `any` 타입 사용을 **최소화**했는가? 적절한 인터페이스/타입이 정의되었는가? |
| Y3 | API 요청/응답 DTO의 필드 타입이 **프론트엔드와 백엔드 간 일관**되는가? |
| Y4 | Enum 또는 Literal 타입으로 표현 가능한 값에 **하드코딩 문자열**을 사용하지 않았는가? |

### 7-5. 성능 & 리소스 관리

| # | 항목 |
|---|------|
| P1 | 루프 내에서 **불필요한 DB 쿼리나 I/O**를 반복하지 않는가? (N+1 문제) |
| P2 | 대량 데이터 처리 시 **적절한 페이징 또는 배치 처리**를 적용했는가? |
| P3 | DB 세션, 파일 핸들 등 리소스가 **정상·예외 경로 모두에서 반드시 해제**되는가? |
| P4 | 캐시 가능한 데이터(별 속성, 절기 정보 등)가 **반복 조회 없이 재사용**되는가? |

---

## 8. 클린 아키텍처 원칙 재점검 리스트

> 본 프로젝트의 계층 구조(`domain` → `use_cases` → `infrastructure` → `routes`)를 기반으로, 클린 아키텍처 원칙을 준수하고 있는지 스스로 점검하기 위한 리스트입니다.

### 8-1. 의존성 규칙 (Dependency Rule)

| # | 항목 |
|---|------|
| CA1 | **안쪽 계층이 바깥 계층을 import하지 않는가?** `domain/` → ✅ 순수 Python만 사용, ❌ Flask/SQLAlchemy/외부 라이브러리 import 금지 |
| CA2 | `domain/services/`에서 `infrastructure/` 또는 `routes/`의 모듈을 직접 참조하지 않는가? |
| CA3 | `use_cases/`에서 `routes/`를 import하지 않는가? |
| CA4 | 데이터베이스 세부사항(SQL, ORM 모델)이 **`infrastructure/` 계층에만 존재**하는가? |

### 8-2. 인터페이스 분리 & 의존성 역전

| # | 항목 |
|---|------|
| CA5 | 새 리포지토리 추가 시 `domain/repositories/`에 **인터페이스(ABC)**를 먼저 정의했는가? |
| CA6 | 새 도메인 서비스 추가 시 `domain/services/interfaces/`에 **인터페이스(ABC)**를 먼저 정의했는가? |
| CA7 | 구현 클래스의 **`__init__` 시그니처에 구체 클래스가 아닌 인터페이스 타입**이 선언되었는가? |
| CA8 | 인터페이스의 메서드 시그니처와 구현 클래스의 메서드 시그니처가 **완전히 일치**하는가? (반환 타입 포함) |

### 8-3. DI 컨테이너 관리 (`dependency_module.py`)

| # | 항목 |
|---|------|
| CA9 | 새 서비스/리포지토리를 **`dependency_module.py`에 바인딩 등록**했는가? |
| CA10 | 바인딩 키가 **인터페이스(I~)**인가? — 구체 클래스로 바인딩하면 교체 불가 |
| CA11 | 동일 인터페이스에 대한 **중복 바인딩**이 없는가? (싱글톤 인스턴스 분리 위험) |
| CA12 | 순환 의존(Circular Dependency)이 발생하지 않는가? — A→B→A 의존 체인 금지 |

### 8-4. Use Case 설계

| # | 항목 |
|---|------|
| CA13 | 하나의 Use Case가 **하나의 비즈니스 유스케이스만** 담당하는가? (God Use Case 금지) |
| CA14 | Use Case가 HTTP 요청/응답 객체(Request, Response)에 **직접 의존하지 않는가?** |
| CA15 | Use Case의 입출력이 **도메인 모델 또는 DTO**로 명확히 정의되어 있는가? |
| CA16 | Use Case 내에서 **프레젠테이션 로직**(JSON 직렬화, HTML 렌더링)을 수행하지 않는가? |

### 8-5. 계층별 역할 준수

| # | 항목 | 해당 계층 |
|---|------|----------|
| CA17 | 비즈니스 규칙(별 계산, 상성 판단, 방위 판정)이 **`domain/services/`에만** 위치하는가? | Domain |
| CA18 | DB 접근, 외부 API 호출이 **`infrastructure/`에만** 위치하는가? | Infrastructure |
| CA19 | HTTP 요청 파싱, 응답 포맷팅이 **`routes/` 또는 `presentation/`에만** 위치하는가? | Presentation |
| CA20 | 오케스트레이션(여러 서비스를 조합하여 하나의 기능을 완성)이 **`use_cases/`에만** 위치하는가? | Use Case |

### 8-6. 테스트 용이성 (Testability)

| # | 항목 |
|---|------|
| CA21 | 도메인 서비스가 **외부 의존 없이 단위 테스트**할 수 있는가? (순수 함수 또는 인터페이스 Stub으로 격리 가능) |
| CA22 | Use Case 테스트에서 리포지토리/서비스를 **Mock/Stub으로 교체**할 수 있는가? |
| CA23 | 테스트가 **DB, 네트워크 등 외부 인프라 없이 실행**할 수 있는가? |

---

## 📋 전체 체크리스트 요약 (Quick Reference)

> 커밋 전 빠르게 훑어보는 최소 점검 항목입니다.

```
□ 예외 → 도메인 예외 + status/code/details 명시 (E1~E5)
□ 네이밍 → 역할 명확, 매직 넘버 제거, 단일 책임 (N1~N5)
□ 입력 검증 → 타입/범위/null/엣지 케이스 방어 (V1~V5)
□ 보안 → 파라미터 바인딩, execFileSync, 민감 정보 미노출 (S1~S2, L5)
□ 의존성 규칙 → 안쪽→바깥 import 금지 (CA1~CA4)
□ 인터페이스 → ABC 정의 → 구현 상속 → DI 등록 (CA5~CA12)
□ Use Case → 단일 책임, HTTP 무관, DTO 입출력 (CA13~CA16)
□ 계층 역할 → 비즈니스=domain, DB=infra, HTTP=routes (CA17~CA20)
□ 테스트 → Stub 도메인 준수, 외부 의존 없이 실행 (CA21~CA23, T1~T3)
□ 코드 위생 → Dead Code 제거, 미사용 import 정리 (H1~H4)
```
