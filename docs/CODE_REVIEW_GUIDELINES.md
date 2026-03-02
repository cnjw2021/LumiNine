# 코드 리뷰 교훈 & 코딩 가이드라인
> PR #9 에서 Copilot 리뷰를 통해 지적받은 77건의 코멘트를 분석·분류하여, 동일한 실수를 반복하지 않기 위한 **실전 체크리스트**입니다.
> 새로운 코드 작성 또는 리뷰 전에 반드시 훑어보세요.

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
