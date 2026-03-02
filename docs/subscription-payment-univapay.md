# UnivaPay 결제 모듈 설계서 - 재사용 가능한 래퍼 아키텍처

> **作成日**: 2026-03-02  
> **目的**: UnivaPay API를 래핑하여 복수 서비스에서 재사용 가능한 결제 모듈 설계  
> **言語**: Python  
> **初期適用先**: 구성기학 점술 서비스 (파워스톤 구독 포함)

---

## 1. 설계 원칙

### 1-1. 핵심 목표

```
[재사용성]  어떤 서비스에서든 import 한 줄로 결제 기능 사용 가능
[관심사 분리] UnivaPay API 세부사항을 완전히 캡슐화
[멱등성]     동일 요청의 중복 과금 방지 (UnivaPay 冪等キー 활용)
[확장성]     카드 외 결제 수단 (콘비니, 은행이체, QR) 추가 용이
[테스트]     테스트/라이브 모드 전환이 설정 한 줄로 가능
```

### 1-2. 레이어 아키텍처

```
┌─────────────────────────────────────────────────┐
│              Service Layer (각 서비스별)           │
│   점술서비스 / Shopify앱 / LINE봇 / 기타 ...      │
├─────────────────────────────────────────────────┤
│           Payment Facade (결제 파사드)             │
│   pay() / subscribe() / refund() / cancel()      │
├─────────────────────────────────────────────────┤
│          Payment Module (결제 모듈 코어)           │
│   TokenManager / ChargeManager / SubscriptionMgr │
│   RefundManager / WebhookHandler                 │
├─────────────────────────────────────────────────┤
│           UnivaPay API Client (HTTP 래퍼)         │
│   인증 / 리트라이 / 에러핸들링 / 로깅             │
├─────────────────────────────────────────────────┤
│              UnivaPay REST API                    │
│   https://api.univapay.com                       │
└─────────────────────────────────────────────────┘
```

---

## 2. 디렉토리 구조

```
univapay_module/
├── __init__.py                  # 외부 공개 인터페이스
├── config.py                    # 설정 관리
├── client.py                    # UnivaPay HTTP 클라이언트 (최하위 래퍼)
├── models/
│   ├── __init__.py
│   ├── token.py                 # TransactionToken 데이터 모델
│   ├── charge.py                # Charge 데이터 모델
│   ├── subscription.py          # Subscription 데이터 모델
│   ├── refund.py                # Refund 데이터 모델
│   └── webhook.py               # Webhook 이벤트 모델
├── managers/
│   ├── __init__.py
│   ├── token_manager.py         # 트랜잭션 토큰 CRUD
│   ├── charge_manager.py        # 과금 CRUD + 폴링
│   ├── subscription_manager.py  # 정기과금 CRUD
│   └── refund_manager.py        # 환불 CRUD
├── facade.py                    # 상위 레벨 통합 인터페이스
├── webhook_handler.py           # 웹훅 수신 및 검증
├── exceptions.py                # 커스텀 예외 클래스
└── constants.py                 # 상수 정의
```

---

## 3. 각 컴포넌트 상세 설계

### 3-1. config.py - 설정 관리

```python
"""
환경변수 또는 직접 주입으로 UnivaPay 인증 정보를 관리.
서비스마다 다른 store를 사용할 수 있도록 multi-store 지원.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import os


class PaymentMode(Enum):
    TEST = "test"
    LIVE = "live"


@dataclass
class UnivaPayConfig:
    # 필수
    jwt: str                                    # アプリトークン
    secret: str                                 # シークレット
    
    # 선택 (기본값 제공)
    mode: PaymentMode = PaymentMode.TEST        # test / live
    api_base_url: str = "https://api.univapay.com"
    default_currency: str = "JPY"
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    
    # 웹훅
    webhook_secret: Optional[str] = None        # 웹훅 서명 검증용
    
    # 폴링 설정
    poll_interval_seconds: float = 2.0
    poll_max_attempts: int = 15
    
    @classmethod
    def from_env(cls, prefix: str = "UNIVAPAY") -> "UnivaPayConfig":
        """환경변수에서 설정을 로드. 서비스별로 prefix를 다르게 지정 가능."""
        return cls(
            jwt=os.environ[f"{prefix}_JWT"],
            secret=os.environ[f"{prefix}_SECRET"],
            mode=PaymentMode(os.environ.get(f"{prefix}_MODE", "test")),
            webhook_secret=os.environ.get(f"{prefix}_WEBHOOK_SECRET"),
        )
```

**사용 예시 (서비스별)**:
```python
# 점술 서비스
fortune_config = UnivaPayConfig.from_env(prefix="FORTUNE_UNIVAPAY")

# Shopify 앱
shopify_config = UnivaPayConfig.from_env(prefix="SHOPIFY_UNIVAPAY")
```

---

### 3-2. client.py - HTTP 클라이언트 (최하위 래퍼)

```python
"""
UnivaPay REST API와의 HTTP 통신을 담당하는 최하위 레이어.
인증, 리트라이, 에러 핸들링, 로깅을 여기서 일괄 처리.
모든 상위 Manager는 이 Client를 통해서만 API를 호출.
"""

class UnivaPayClient:
    """
    UnivaPay API HTTP 클라이언트.
    
    책임:
    - Authorization 헤더 구성: Bearer {secret}.{jwt}
    - 멱등키(Idempotency-Key) 자동 부여 (POST 요청 시)
    - HTTP 에러 → 커스텀 예외 변환
    - 리트라이 로직 (429 Rate Limit, 5xx 서버 에러)
    - 요청/응답 로깅
    """
    
    def __init__(self, config: UnivaPayConfig):
        self.config = config
        self._session = None  # httpx.AsyncClient 또는 requests.Session
    
    # --- 핵심 메서드 ---
    
    async def get(self, path: str, params: dict = None) -> dict:
        """GET 요청"""
        
    async def post(self, path: str, data: dict = None, 
                   idempotency_key: str = None) -> dict:
        """POST 요청. idempotency_key 미지정 시 UUID 자동 생성."""
        
    async def patch(self, path: str, data: dict = None) -> dict:
        """PATCH 요청 (UPDATE 용)"""
        
    async def delete(self, path: str) -> dict:
        """DELETE 요청"""
    
    # --- 내부 메서드 ---
    
    def _build_headers(self, idempotency_key: str = None) -> dict:
        """
        공통 헤더 구성.
        Authorization: Bearer {secret}.{jwt}
        Content-Type: application/json
        Idempotency-Key: {key}  (POST 시)
        """
        headers = {
            "Authorization": f"Bearer {self.config.secret}.{self.config.jwt}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers
    
    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """
        실제 HTTP 요청 실행.
        - 429: retry_delay만큼 대기 후 재시도
        - 5xx: max_retries까지 재시도
        - 4xx: 즉시 예외 발생
        """
    
    def _handle_error(self, status_code: int, response_body: dict):
        """HTTP 에러를 커스텀 예외로 변환"""
```

---

### 3-3. models/ - 데이터 모델

UnivaPay API의 응답을 Python 객체로 매핑한다.

```python
# models/token.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime


class TokenType(Enum):
    ONE_TIME = "one_time"           # 1회용
    SUBSCRIPTION = "subscription"    # 정기과금용 (리커링)
    RECURRING = "recurring"          # 재이용 가능


class PaymentType(Enum):
    CARD = "card"
    KONBINI = "konbini"             # 콘비니 결제
    BANK_TRANSFER = "bank_transfer"  # 은행이체
    ONLINE = "online"               # QR 등 온라인결제
    PAIDY = "paidy"


@dataclass
class TransactionToken:
    id: str
    store_id: str
    type: TokenType
    payment_type: PaymentType
    email: Optional[str]
    active: bool
    mode: str                        # "test" or "live"
    created_on: datetime
    metadata: dict
    
    # 카드 정보 (마스킹된 상태)
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None


# models/charge.py
class ChargeStatus(Enum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    ERROR = "error"
    AUTHORIZED = "authorized"        # 해외카드 오소리
    AWAITING = "awaiting"            # 콘비니/은행이체 입금대기


@dataclass
class Charge:
    id: str
    store_id: str
    transaction_token_id: str
    subscription_id: Optional[str]
    requested_amount: int
    requested_currency: str
    charged_amount: Optional[int]
    charged_currency: Optional[str]
    status: ChargeStatus
    error: Optional[dict]
    metadata: dict
    mode: str
    created_on: datetime


# models/subscription.py
class SubscriptionStatus(Enum):
    UNVERIFIED = "unverified"
    CURRENT = "current"              # 정상 과금 중
    SUSPENDED = "suspended"          # 일시 정지
    UNPAID = "unpaid"                # 미납
    CANCELED = "canceled"            # 해지
    COMPLETED = "completed"          # 완료 (회수 제한)


class SubscriptionPeriod(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    BIMONTHLY = "bimonthly"          # 격월
    QUARTERLY = "quarterly"          # 분기
    SEMIANNUALLY = "semiannually"    # 반기
    ANNUALLY = "annually"            # 연간


@dataclass
class Subscription:
    id: str
    store_id: str
    transaction_token_id: str
    amount: int
    currency: str
    period: SubscriptionPeriod
    status: SubscriptionStatus
    initial_amount: Optional[int]     # 초회 금액 (다른 경우)
    next_payment_on: Optional[datetime]
    metadata: dict
    mode: str
    created_on: datetime


# models/refund.py
class RefundStatus(Enum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    ERROR = "error"


class RefundReason(Enum):
    DUPLICATE = "duplicate"
    CUSTOMER_REQUEST = "customer_request"
    FRAUD = "fraud"


@dataclass
class Refund:
    id: str
    store_id: str
    charge_id: str
    amount: int
    currency: str
    status: RefundStatus
    reason: Optional[RefundReason]
    message: Optional[str]
    metadata: dict
    mode: str
    created_on: datetime
```

---

### 3-4. managers/ - 비즈니스 로직

```python
# managers/token_manager.py
class TokenManager:
    """
    트랜잭션 토큰 관리.
    
    주의: 카드 번호 등 PCI DSS 민감 정보는 
    프론트엔드(UnivaPay Widget/인라인폼)에서 직접 토큰화해야 함.
    서버사이드에서 생 카드번호를 다루면 PCI DSS 준수 의무 발생.
    """
    
    def __init__(self, client: UnivaPayClient): ...
    
    async def create_card_token(
        self,
        token_type: TokenType,
        card_data: dict,             # cardholder, card_number, exp_month, exp_year, cvv
        email: str = None,
        metadata: dict = None,
    ) -> TransactionToken:
        """
        카드 결제용 토큰 생성.
        ※ PCI DSS 관점에서, 가능한 프론트엔드 위젯을 통한 토큰 생성을 권장.
        이 메서드는 서버사이드 토큰 생성이 불가피한 경우에만 사용.
        
        POST /tokens
        """
    
    async def get(self, store_id: str, token_id: str) -> TransactionToken:
        """GET /stores/{storeId}/tokens/{id}"""
    
    async def list(self, store_id: str = None, **filters) -> list[TransactionToken]:
        """GET /stores/{storeId}/tokens"""
    
    async def delete(self, store_id: str, token_id: str) -> None:
        """DELETE /stores/{storeId}/tokens/{id}"""


# managers/charge_manager.py
class ChargeManager:
    """과금(Charge) 관리"""
    
    def __init__(self, client: UnivaPayClient): ...
    
    async def create(
        self,
        token_id: str,
        amount: int,
        currency: str = "JPY",
        capture: bool = True,        # False = オーソリのみ
        metadata: dict = None,
        idempotency_key: str = None,
    ) -> Charge:
        """
        과금 생성.
        POST /charges
        
        idempotency_key를 지정하면 동일 키로 중복 요청 시
        UnivaPay가 이전 결과를 반환 (멱등성 보장).
        """
    
    async def get(self, store_id: str, charge_id: str) -> Charge:
        """GET /stores/{storeId}/charges/{id}"""
    
    async def capture(self, store_id: str, charge_id: str, 
                      amount: int = None) -> Charge:
        """
        오소리 후 캡처 (실매출 확정).
        POST /stores/{storeId}/charges/{id}/capture
        """
    
    async def poll_until_final(
        self, store_id: str, charge_id: str
    ) -> Charge:
        """
        Charge가 pending/awaiting 상태인 동안 폴링하여
        최종 상태(successful/failed/error)가 될 때까지 대기.
        config의 poll_interval / poll_max_attempts 설정 사용.
        """
    
    async def list(self, store_id: str = None, **filters) -> list[Charge]:
        """GET /stores/{storeId}/charges"""


# managers/subscription_manager.py
class SubscriptionManager:
    """정기과금(Subscription) 관리"""
    
    def __init__(self, client: UnivaPayClient): ...
    
    async def create(
        self,
        token_id: str,
        amount: int,
        period: SubscriptionPeriod,
        currency: str = "JPY",
        initial_amount: int = None,        # 초회 금액 (무료체험 시 0)
        start_on: str = None,              # 과금 시작일 (YYYY-MM-DD)
        installment_plan: dict = None,     # 분할 설정
        metadata: dict = None,
        idempotency_key: str = None,
    ) -> Subscription:
        """
        정기과금 생성.
        POST /subscriptions
        """
    
    async def get(self, store_id: str, subscription_id: str) -> Subscription:
        """GET /stores/{storeId}/subscriptions/{id}"""
    
    async def suspend(self, store_id: str, subscription_id: str) -> Subscription:
        """
        일시정지.
        PATCH /stores/{storeId}/subscriptions/{id}
        body: {"status": "suspended"}
        """
    
    async def resume(self, store_id: str, subscription_id: str) -> Subscription:
        """
        재개.
        PATCH /stores/{storeId}/subscriptions/{id}
        body: {"status": "current"}
        """
    
    async def cancel(self, store_id: str, subscription_id: str) -> Subscription:
        """
        해지 (되돌릴 수 없음).
        PATCH /stores/{storeId}/subscriptions/{id}
        body: {"status": "canceled"}
        """
    
    async def update_amount(
        self, store_id: str, subscription_id: str, new_amount: int
    ) -> Subscription:
        """
        과금 금액 변경 (플랜 변경 시).
        PATCH /stores/{storeId}/subscriptions/{id}
        """
    
    async def list(self, store_id: str = None, **filters) -> list[Subscription]:
        """GET /stores/{storeId}/subscriptions"""


# managers/refund_manager.py
class RefundManager:
    """환불(Refund) 관리"""
    
    def __init__(self, client: UnivaPayClient): ...
    
    async def create(
        self,
        store_id: str,
        charge_id: str,
        amount: int,
        currency: str = "JPY",
        reason: RefundReason = RefundReason.CUSTOMER_REQUEST,
        message: str = None,
        metadata: dict = None,
        idempotency_key: str = None,
    ) -> Refund:
        """
        환불 생성.
        POST /stores/{storeId}/charges/{chargeId}/refunds
        
        부분 환불: amount < 원래 과금액
        전액 환불: amount == 원래 과금액
        """
    
    async def get(self, store_id: str, charge_id: str, refund_id: str) -> Refund:
        """GET /stores/{storeId}/charges/{chargeId}/refunds/{id}"""
    
    async def list(self, store_id: str, charge_id: str) -> list[Refund]:
        """GET /stores/{storeId}/charges/{chargeId}/refunds"""
```

---

### 3-5. webhook_handler.py - 웹훅 수신

```python
"""
UnivaPay로부터의 웹훅 이벤트를 수신하고 처리.
각 서비스에서 콜백 함수를 등록하여 이벤트별 처리를 커스터마이즈.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Awaitable


class WebhookEvent(Enum):
    CHARGE_FINISHED = "charge_finished"
    CHARGE_UPDATED = "charge_updated"
    SUBSCRIPTION_PAYMENT = "subscription_payment"
    SUBSCRIPTION_COMPLETED = "subscription_completed"
    SUBSCRIPTION_CANCELED = "subscription_canceled"
    SUBSCRIPTION_FAILURE = "subscription_failure"
    SUBSCRIPTION_SUSPENDED = "subscription_suspended"
    REFUND_FINISHED = "refund_finished"
    TOKEN_CREATED = "token_created"
    TOKEN_CVV_AUTH_UPDATED = "token_cvv_auth_updated"
    THREE_DS_STATUS_UPDATED = "three_ds_status_updated"


# 콜백 타입: async def handler(event_type, data) -> None
WebhookCallback = Callable[[WebhookEvent, dict], Awaitable[None]]


class WebhookHandler:
    """
    웹훅 수신 및 디스패치.
    
    사용 예:
        handler = WebhookHandler(config)
        handler.on(WebhookEvent.CHARGE_FINISHED, my_charge_handler)
        handler.on(WebhookEvent.SUBSCRIPTION_PAYMENT, my_sub_handler)
        
        # FastAPI/Flask 등의 엔드포인트에서:
        await handler.process(request_body, request_headers)
    """
    
    def __init__(self, config: UnivaPayConfig):
        self.config = config
        self._callbacks: dict[WebhookEvent, list[WebhookCallback]] = {}
    
    def on(self, event: WebhookEvent, callback: WebhookCallback):
        """이벤트별 콜백 등록"""
        self._callbacks.setdefault(event, []).append(callback)
    
    async def process(self, body: dict, headers: dict = None) -> bool:
        """
        웹훅 수신 처리.
        1. (선택) 서명 검증
        2. 이벤트 타입 추출
        3. 등록된 콜백 실행
        
        Returns: 처리 성공 여부
        """
        event_type = WebhookEvent(body.get("event"))
        event_data = body.get("data", {})
        
        callbacks = self._callbacks.get(event_type, [])
        for cb in callbacks:
            await cb(event_type, event_data)
        
        return True
```

---

### 3-6. facade.py - 상위 통합 인터페이스

**이것이 각 서비스에서 실제로 사용하는 메인 인터페이스이다.**

```python
"""
Payment Facade - 서비스 레이어에서 사용하는 단일 진입점.
복잡한 내부 구조를 숨기고, 직관적인 메서드만 노출.
"""


class PaymentFacade:
    """
    결제 기능의 단일 진입점.
    
    사용 예:
        config = UnivaPayConfig.from_env(prefix="FORTUNE")
        payment = PaymentFacade(config)
        
        # 1회 결제
        result = await payment.charge_once(token_id, 3000)
        
        # 구독 시작
        sub = await payment.start_subscription(token_id, 980, "monthly")
        
        # 환불
        refund = await payment.refund(store_id, charge_id, 3000)
    """
    
    def __init__(self, config: UnivaPayConfig):
        self.config = config
        self.client = UnivaPayClient(config)
        self.tokens = TokenManager(self.client)
        self.charges = ChargeManager(self.client)
        self.subscriptions = SubscriptionManager(self.client)
        self.refunds = RefundManager(self.client)
        self.webhooks = WebhookHandler(config)
    
    # ========== 1회 결제 ==========
    
    async def charge_once(
        self,
        token_id: str,
        amount: int,
        currency: str = None,
        metadata: dict = None,
        idempotency_key: str = None,
        wait_for_result: bool = True,
    ) -> Charge:
        """
        1회 과금 실행.
        
        wait_for_result=True 시, 결제 완료까지 폴링하여 최종 결과 반환.
        False 시, pending 상태의 Charge를 즉시 반환.
        """
        currency = currency or self.config.default_currency
        
        charge = await self.charges.create(
            token_id=token_id,
            amount=amount,
            currency=currency,
            metadata=metadata,
            idempotency_key=idempotency_key,
        )
        
        if wait_for_result and charge.status == ChargeStatus.PENDING:
            charge = await self.charges.poll_until_final(
                charge.store_id, charge.id
            )
        
        return charge
    
    # ========== 구독 (정기과금) ==========
    
    async def start_subscription(
        self,
        token_id: str,
        amount: int,
        period: str = "monthly",           # "daily"|"monthly"|"annually" 등
        currency: str = None,
        initial_amount: int = None,        # 초회 금액 (무료체험 = 0)
        start_on: str = None,              # 과금 시작일
        metadata: dict = None,
        idempotency_key: str = None,
    ) -> Subscription:
        """정기과금 시작"""
        currency = currency or self.config.default_currency
        
        return await self.subscriptions.create(
            token_id=token_id,
            amount=amount,
            period=SubscriptionPeriod(period),
            currency=currency,
            initial_amount=initial_amount,
            start_on=start_on,
            metadata=metadata,
            idempotency_key=idempotency_key,
        )
    
    async def cancel_subscription(
        self, store_id: str, subscription_id: str
    ) -> Subscription:
        """구독 해지"""
        return await self.subscriptions.cancel(store_id, subscription_id)
    
    async def pause_subscription(
        self, store_id: str, subscription_id: str
    ) -> Subscription:
        """구독 일시정지"""
        return await self.subscriptions.suspend(store_id, subscription_id)
    
    async def resume_subscription(
        self, store_id: str, subscription_id: str
    ) -> Subscription:
        """구독 재개"""
        return await self.subscriptions.resume(store_id, subscription_id)
    
    async def change_plan(
        self, store_id: str, subscription_id: str, new_amount: int
    ) -> Subscription:
        """플랜(금액) 변경"""
        return await self.subscriptions.update_amount(
            store_id, subscription_id, new_amount
        )
    
    # ========== 환불 ==========
    
    async def refund(
        self,
        store_id: str,
        charge_id: str,
        amount: int = None,                # None = 전액환불
        reason: str = "customer_request",
        message: str = None,
        metadata: dict = None,
        idempotency_key: str = None,
    ) -> Refund:
        """
        환불 실행.
        amount 미지정 시 해당 charge의 전액을 환불.
        """
        if amount is None:
            charge = await self.charges.get(store_id, charge_id)
            amount = charge.charged_amount
        
        return await self.refunds.create(
            store_id=store_id,
            charge_id=charge_id,
            amount=amount,
            reason=RefundReason(reason),
            message=message,
            metadata=metadata,
            idempotency_key=idempotency_key,
        )
    
    # ========== 웹훅 ==========
    
    def on_event(self, event: str, callback):
        """웹훅 이벤트 콜백 등록"""
        self.webhooks.on(WebhookEvent(event), callback)
    
    async def handle_webhook(self, body: dict, headers: dict = None) -> bool:
        """웹훅 수신 처리"""
        return await self.webhooks.process(body, headers)
```

---

### 3-7. exceptions.py - 커스텀 예외

```python
class UnivaPayError(Exception):
    """UnivaPay 모듈 기본 예외"""
    def __init__(self, message: str, status_code: int = None, 
                 error_code: str = None, raw_response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.raw_response = raw_response


class AuthenticationError(UnivaPayError):
    """인증 실패 (401)"""

class ForbiddenError(UnivaPayError):
    """권한 없음 (403)"""

class NotFoundError(UnivaPayError):
    """리소스 미발견 (404)"""

class ConflictError(UnivaPayError):
    """충돌 (409) - 중복 요청 등"""

class RateLimitError(UnivaPayError):
    """요청 제한 초과 (429)"""

class ChargeFailedError(UnivaPayError):
    """과금 실패"""

class RefundFailedError(UnivaPayError):
    """환불 실패"""

class SubscriptionError(UnivaPayError):
    """정기과금 관련 에러"""

class WebhookValidationError(UnivaPayError):
    """웹훅 검증 실패"""

class PollTimeoutError(UnivaPayError):
    """폴링 타임아웃"""
```

---

### 3-8. \_\_init\_\_.py - 외부 공개 인터페이스

```python
"""
UnivaPay 결제 모듈.

Usage:
    from univapay_module import PaymentFacade, UnivaPayConfig
    
    config = UnivaPayConfig.from_env(prefix="MYSERVICE")
    payment = PaymentFacade(config)
    
    # 1회 결제
    charge = await payment.charge_once(token_id, 3000)
    
    # 구독
    sub = await payment.start_subscription(token_id, 980, "monthly")
"""

from .config import UnivaPayConfig, PaymentMode
from .facade import PaymentFacade
from .models.token import TransactionToken, TokenType, PaymentType
from .models.charge import Charge, ChargeStatus
from .models.subscription import Subscription, SubscriptionStatus, SubscriptionPeriod
from .models.refund import Refund, RefundStatus, RefundReason
from .webhook_handler import WebhookHandler, WebhookEvent
from .exceptions import (
    UnivaPayError, AuthenticationError, ChargeFailedError,
    RefundFailedError, SubscriptionError, PollTimeoutError,
)

__all__ = [
    "PaymentFacade", "UnivaPayConfig", "PaymentMode",
    "TransactionToken", "TokenType", "PaymentType",
    "Charge", "ChargeStatus",
    "Subscription", "SubscriptionStatus", "SubscriptionPeriod",
    "Refund", "RefundStatus", "RefundReason",
    "WebhookHandler", "WebhookEvent",
    "UnivaPayError", "AuthenticationError", "ChargeFailedError",
    "RefundFailedError", "SubscriptionError", "PollTimeoutError",
]
```

---

## 4. 서비스별 통합 예시

### 4-1. 점술 서비스 - 파워스톤 구독

```python
"""
구성기학 점술 서비스에서의 결제 통합 예시.
"""
from univapay_module import PaymentFacade, UnivaPayConfig, WebhookEvent

# === 초기화 ===
config = UnivaPayConfig.from_env(prefix="FORTUNE")
payment = PaymentFacade(config)


# === 1회 결제: PDF 감정서 구매 ===
async def purchase_fortune_report(user_id: str, token_id: str):
    """감정서 1회 구매 (3,000엔)"""
    charge = await payment.charge_once(
        token_id=token_id,
        amount=3000,
        metadata={
            "user_id": user_id,
            "product": "fortune_report",
            "service": "kigaku_fortune",
        },
        idempotency_key=f"fortune_report_{user_id}_{date_str}",
    )
    
    if charge.status.value == "successful":
        await generate_and_send_report(user_id)
    
    return charge


# === 구독: 월간 파워스톤 + 길방위 리포트 ===

PLAN_PRICES = {
    "basic":   980,    # 월간 길방위 리포트만
    "stone":   2980,   # 리포트 + 파워스톤 추천
    "premium": 4980,   # 리포트 + 파워스톤 추천 + 실물 스톤 배송
}

async def start_stone_subscription(
    user_id: str, token_id: str, plan: str = "stone"
):
    """파워스톤 구독 시작"""
    sub = await payment.start_subscription(
        token_id=token_id,
        amount=PLAN_PRICES[plan],
        period="monthly",
        initial_amount=0,              # 초월 무료
        metadata={
            "user_id": user_id,
            "plan": plan,
            "service": "kigaku_fortune",
        },
        idempotency_key=f"sub_{user_id}_{plan}",
    )
    
    await activate_user_subscription(user_id, plan, sub.id)
    return sub


async def change_subscription_plan(
    user_id: str, store_id: str, subscription_id: str, new_plan: str
):
    """플랜 변경"""
    return await payment.change_plan(
        store_id=store_id,
        subscription_id=subscription_id,
        new_amount=PLAN_PRICES[new_plan],
    )


# === 웹훅 처리 ===

async def on_subscription_payment(event_type, data):
    """매월 정기과금 성공 시 → 그 달의 파워스톤 리포트 자동 생성"""
    user_id = data.get("metadata", {}).get("user_id")
    if user_id:
        await generate_monthly_stone_report(user_id)

async def on_subscription_failure(event_type, data):
    """정기과금 실패 시 → 사용자에게 알림"""
    user_id = data.get("metadata", {}).get("user_id")
    if user_id:
        await notify_payment_failure(user_id)

# 웹훅 콜백 등록
payment.on_event("subscription_payment", on_subscription_payment)
payment.on_event("subscription_failure", on_subscription_failure)
```

### 4-2. 다른 서비스에서의 재사용 예시

```python
"""
Shopify CS AI Bot 서비스에서의 결제 통합.
동일한 모듈을 다른 설정으로 사용.
"""
from univapay_module import PaymentFacade, UnivaPayConfig

# 다른 환경변수 prefix → 다른 UnivaPay 스토어
config = UnivaPayConfig.from_env(prefix="SHOPIFY_CSBOT")
payment = PaymentFacade(config)

async def charge_csbot_subscription(shop_id: str, token_id: str):
    """Shopify 앱 월정액 과금"""
    return await payment.start_subscription(
        token_id=token_id,
        amount=9800,
        period="monthly",
        metadata={"shop_id": shop_id, "service": "shopify_csbot"},
    )
```

---

## 5. 프론트엔드 연동: 토큰 생성 방식

### 5-1. 추천: UnivaPay Widget (인라인폼)

PCI DSS 관점에서, 카드 정보는 **프론트엔드에서 직접 토큰화**하는 것을 강력히 권장한다.

```html
<!-- UnivaPay 인라인폼 (HTML 설치 예시) -->
<script 
  src="https://widget.univapay.com/client/checkout.js"
  data-app-id="{APP_TOKEN_ID}"
  data-checkout="token"
  data-token-type="subscription"
  data-amount="2980"
  data-currency="jpy"
  data-inline="true"
></script>

<script>
  // 토큰 생성 완료 시 콜백
  UnivapayCheckout.on('token', function(token) {
    // token.id를 서버로 전송 → 서버에서 PaymentFacade 사용
    fetch('/api/subscribe', {
      method: 'POST',
      body: JSON.stringify({ token_id: token.id }),
    });
  });
</script>
```

### 5-2. 처리 플로우

```
[프론트엔드]                        [백엔드 (Python)]                [UnivaPay]
     │                                    │                              │
     │  1. 카드 정보 입력                  │                              │
     │  2. UnivaPay Widget으로             │                              │
     │     토큰 생성 ──────────────────────┼───────────────────────────→  │
     │                                    │                              │
     │  3. token.id 수신 ←────────────────┼──────────────────────────── │
     │                                    │                              │
     │  4. token_id를 서버로 전송          │                              │
     │  ────────────────────────────────→ │                              │
     │                                    │  5. PaymentFacade             │
     │                                    │     .start_subscription()     │
     │                                    │  ───────────────────────────→│
     │                                    │                              │
     │                                    │  6. Subscription 결과 ←───── │
     │                                    │                              │
     │  7. 결과 응답 ←─────────────────── │                              │
     │                                    │                              │
     │                                    │  8. 웹훅 수신 (매월) ←────── │
     │                                    │     → 파워스톤 리포트 생성    │
```

---

## 6. 3-Dセキュア (3DS) 대응

일본 내 카드결제에서 3-Dセキュア는 2025년 이후 사실상 필수이다.

### 6-1. 처리 플로우

```
1. 프론트에서 토큰 생성 시 3DS 인증 플래그 ON
2. UnivaPay가 카드사 3DS 인증 페이지로 리다이렉트
3. 소비자가 인증 완료
4. UnivaPay가 3DS 결과를 토큰에 반영
5. 서버에서 해당 토큰으로 과금 실행
```

### 6-2. Widget에서의 3DS 설정

```html
<script 
  src="https://widget.univapay.com/client/checkout.js"
  data-app-id="{APP_TOKEN_ID}"
  data-checkout="payment"
  data-amount="2980"
  data-currency="jpy"
  data-three-ds="true"
></script>
```

서버사이드에서 3DS 상태를 확인하려면:

```python
# 이슈어 토큰(3DS 정보) 조회
# GET /stores/{storeId}/tokens/{tokenId}/three_ds
```

---

## 7. 멱등성(冪等性) 보장 전략

### 7-1. UnivaPay 측 멱등키

```python
# 요청 시 Idempotency-Key 헤더를 포함하면,
# 동일 키로 재요청 시 UnivaPay가 이전 결과를 반환.

charge = await payment.charge_once(
    token_id=token_id,
    amount=3000,
    idempotency_key=f"order_{order_id}",  # 주문 ID 기반
)
```

### 7-2. 애플리케이션 측 이중 방어

```
[멱등성 보장 레이어]

1층: 프론트엔드
    - 결제 버튼 클릭 후 즉시 비활성화 (더블클릭 방지)
    - 요청 중 로딩 표시

2층: 백엔드 (PaymentFacade)
    - idempotency_key 자동 생성 (미지정 시 UUID)
    - 동일 user_id + product 조합의 중복 요청 검사

3층: UnivaPay API
    - Idempotency-Key 헤더 기반 중복 방지
    - 동일 키로 재요청 시 이전 응답 반환
```

---

## 8. 에러 핸들링 전략

```python
"""
서비스 레이어에서의 에러 핸들링 패턴.
"""
from univapay_module import (
    PaymentFacade, UnivaPayError, ChargeFailedError,
    PollTimeoutError, RateLimitError
)

async def safe_charge(user_id: str, token_id: str, amount: int):
    try:
        charge = await payment.charge_once(token_id, amount)
        return {"success": True, "charge_id": charge.id}
    
    except ChargeFailedError as e:
        # 과금 실패 (카드 한도 초과, 유효기간 만료 등)
        await notify_user_payment_failed(user_id, str(e))
        return {"success": False, "error": "payment_failed", "detail": str(e)}
    
    except PollTimeoutError:
        # 폴링 타임아웃 → 웹훅으로 최종 결과 수신 대기
        return {"success": None, "error": "processing", 
                "message": "결제 처리 중입니다. 잠시 후 확인해 주세요."}
    
    except RateLimitError:
        # API 요청 제한 → 잠시 후 재시도 안내
        return {"success": False, "error": "rate_limit",
                "message": "잠시 후 다시 시도해 주세요."}
    
    except UnivaPayError as e:
        # 기타 UnivaPay 에러
        await log_payment_error(user_id, e)
        return {"success": False, "error": "system_error"}
```

---

## 9. 테스트 전략

### 9-1. 모드 전환

```python
# 테스트 모드 (기본값)
config = UnivaPayConfig(jwt="...", secret="...", mode=PaymentMode.TEST)

# 라이브 모드
config = UnivaPayConfig(jwt="...", secret="...", mode=PaymentMode.LIVE)
```

### 9-2. 테스트 카드 번호

UnivaPay에서 제공하는 테스트 카드:

| 시나리오 | 카드번호 | 예상 결과 |
|---------|---------|----------|
| 정상 결제 | 4000020000000000 | successful |
| 결제 실패 | 4000020000000002 | failed |
| 3DS 인증 | 4000020000000010 | 3DS 인증 후 successful |

※ 실제 테스트 카드 번호는 UnivaPay 관리 콘솔의 테스트 가이드를 참조.

### 9-3. 유닛 테스트 구조

```python
# client를 모킹하여 API 호출 없이 테스트
class MockUnivaPayClient:
    async def post(self, path, data=None, idempotency_key=None):
        if "/charges" in path:
            return {"id": "test_charge_id", "status": "successful", ...}

# Facade에 MockClient 주입
facade = PaymentFacade.__new__(PaymentFacade)
facade.client = MockUnivaPayClient()
facade.charges = ChargeManager(facade.client)
```

---

## 10. 배포 및 환경변수

### 10-1. 필수 환경변수

```bash
# 점술 서비스용
FORTUNE_UNIVAPAY_JWT=your_app_token
FORTUNE_UNIVAPAY_SECRET=your_secret
FORTUNE_UNIVAPAY_MODE=test          # test or live
FORTUNE_UNIVAPAY_WEBHOOK_SECRET=your_webhook_secret

# Shopify 앱용 (별도 스토어)
SHOPIFY_UNIVAPAY_JWT=another_token
SHOPIFY_UNIVAPAY_SECRET=another_secret
SHOPIFY_UNIVAPAY_MODE=test
```

### 10-2. Docker / ConoHa VPS 배포 시

```yaml
# docker-compose.yml
services:
  fortune-app:
    environment:
      - FORTUNE_UNIVAPAY_JWT=${FORTUNE_UNIVAPAY_JWT}
      - FORTUNE_UNIVAPAY_SECRET=${FORTUNE_UNIVAPAY_SECRET}
      - FORTUNE_UNIVAPAY_MODE=live
      - FORTUNE_UNIVAPAY_WEBHOOK_SECRET=${FORTUNE_UNIVAPAY_WEBHOOK_SECRET}
```

---

## 부록: UnivaPay API 엔드포인트 매핑

| 모듈 메서드 | HTTP | UnivaPay Endpoint |
|------------|------|------------------|
| tokens.create | POST | /tokens |
| tokens.get | GET | /stores/{sId}/tokens/{id} |
| tokens.delete | DELETE | /stores/{sId}/tokens/{id} |
| charges.create | POST | /charges |
| charges.get | GET | /stores/{sId}/charges/{id} |
| charges.capture | POST | /stores/{sId}/charges/{id}/capture |
| charges.list | GET | /stores/{sId}/charges |
| subscriptions.create | POST | /subscriptions |
| subscriptions.get | GET | /stores/{sId}/subscriptions/{id} |
| subscriptions.update | PATCH | /stores/{sId}/subscriptions/{id} |
| subscriptions.list | GET | /stores/{sId}/subscriptions |
| refunds.create | POST | /stores/{sId}/charges/{cId}/refunds |
| refunds.get | GET | /stores/{sId}/charges/{cId}/refunds/{id} |
| refunds.list | GET | /stores/{sId}/charges/{cId}/refunds |
| webhooks (수신) | POST | (자체 서버 엔드포인트) |