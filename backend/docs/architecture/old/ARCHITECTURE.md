# NineStarKi Backend Architecture

## 개요

NineStarKi 백엔드는 **도메인 중심 설계(Domain-Driven Design, DDD)** 원칙에 기반하여 설계되었습니다. 이 아키텍처는 비즈니스 로직의 명확한 분리, 유지보수성 향상, 그리고 확장성을 목표로 합니다.

## 디렉토리 구조

```
backend/apps/ninestarki/
├── domain/                      # 도메인 계층 (핵심 비즈니스 로직)
│   ├── entities/               # 도메인 엔티티
│   │   └── auspicious_date.py  # 길일 도메인 엔티티
│   └── services/               # 도메인 서비스
│       └── auspicious_dates_domain_service.py  # 길일 계산 도메인 로직
├── application/                 # 애플리케이션 계층 (유스케이스 및 비즈니스 규칙)
│   ├── services/               # 애플리케이션 서비스
│   │   └── auspicious_dates_application_service.py  # 길일 데이터 포맷팅 및 조합
│   └── interfaces/             # 서비스 인터페이스
│       └── auspicious_dates_interface.py  # 길일 서비스 계약
├── infrastructure/              # 인프라 계층 (외부 의존성 및 기술적 구현)
│   └── services/               # 외부 서비스 래퍼
│       └── auspicious_dates_service.py  # 길일 서비스 구현체
├── routes/                      # API 라우트 (프레젠테이션 계층)
│   └── auspicious_dates_routes.py  # 길일 통합 API 엔드포인트
├── services/                    # 기존 서비스들 (점진적 마이그레이션 대상)
│   ├── moving_dates_service.py
│   ├── recommended_water_drawing_dates.py
│   └── pdf_generator.py
│   # ⚠️ 주의: 이 파일들은 새로운 구조로 점진적 마이그레이션 예정
│   # - moving_dates_service.py → domain/services/
│   # - recommended_water_drawing_dates.py → domain/services/
│   # - pdf_generator.py → infrastructure/services/
├── utils/                       # 유틸리티 함수들
├── constants/                   # 상수 정의
├── static/                      # 정적 파일들
└── templates/                   # HTML 템플릿들
```

## 계층별 책임

### 1. Domain Layer (도메인 계층)

**목적**: 핵심 비즈니스 로직과 규칙을 담당

**구성요소**:
- **Entities**: 비즈니스 개념을 표현하는 객체 (예: `AuspiciousDate`)
- **Domain Services**: 도메인 규칙을 구현하는 서비스 (예: `AuspiciousDatesDomainService`)

**특징**:
- 외부 의존성이 없음
- 순수한 비즈니스 로직만 포함
- 테스트하기 쉬움

### 2. Application Layer (애플리케이션 계층)

**목적**: 유스케이스 구현 및 도메인 서비스 조합

**구성요소**:
- **Application Services**: 비즈니스 프로세스 조정 (예: `AuspiciousDatesApplicationService`)
- **Interfaces**: 서비스 계약 정의 (예: `IAuspiciousDatesService`)

**특징**:
- 도메인 계층과 인프라 계층 사이의 중재자
- 트랜잭션 경계 관리
- 도메인 서비스를 조합하여 복잡한 비즈니스 프로세스 구현

### 3. Infrastructure Layer (인프라 계층)

**목적**: 외부 시스템과의 상호작용 및 기술적 구현

**구성요소**:
- **Services**: 외부 서비스 래퍼 (예: `AuspiciousDatesService`)
- **Repositories**: 데이터 접근 구현 (향후 추가 예정)
- **External Services**: 외부 API 클라이언트

**특징**:
- 데이터베이스, 외부 API, 파일 시스템 등과의 상호작용
- 도메인 계층에 정의된 인터페이스 구현

### 4. Presentation Layer (프레젠테이션 계층)

**목적**: 사용자 요청 처리 및 응답 생성

**구성요소**:
- **Routes**: API 엔드포인트 정의
- **Controllers**: 요청/응답 처리 로직

## 의존성 방향

```
Presentation Layer (Routes)
           ↓
Infrastructure Layer (Services)
           ↓
Application Layer (Services, Interfaces)
           ↓
Domain Layer (Entities, Services)
```

**원칙**: 의존성은 항상 안쪽(도메인)을 향합니다.

## 주요 설계 원칙

### 1. 단일 책임 원칙 (Single Responsibility Principle)
- 각 클래스와 모듈은 하나의 명확한 책임만 가짐

### 2. 의존성 역전 원칙 (Dependency Inversion Principle)
- 고수준 모듈이 저수준 모듈에 의존하지 않음
- 추상화를 통해 의존성 방향 제어

### 3. 인터페이스 분리 원칙 (Interface Segregation Principle)
- 클라이언트는 사용하지 않는 인터페이스에 의존하지 않음

### 4. 개방-폐쇄 원칙 (Open-Closed Principle)
- 확장에는 열려있고, 수정에는 닫혀있음

## 길일 서비스 아키텍처

### 서비스 구성
```
AuspiciousDatesService (Infrastructure)
    ↓
AuspiciousDatesApplicationService (Application)
    ↓
AuspiciousDatesDomainService (Domain)
    ↓
DirectionFortuneService (External)
```

### 데이터 흐름
1. **API 요청** → `auspicious_dates_routes.py`
2. **서비스 호출** → `AuspiciousDatesService`
3. **애플리케이션 로직** → `AuspiciousDatesApplicationService`
4. **도메인 로직** → `AuspiciousDatesDomainService`
5. **외부 서비스** → `DirectionFortuneService`
6. **결과 반환** → API 응답

## 장점

### 1. 유지보수성
- 각 계층의 책임이 명확하게 분리됨
- 변경 시 영향 범위를 최소화

### 2. 테스트 용이성
- 각 계층을 독립적으로 테스트 가능
- Mock 객체 사용으로 단위 테스트 용이

### 3. 확장성
- 새로운 도메인 추가 시 `domain/` 하위에 추가
- 새로운 유스케이스 추가 시 `application/services/` 하위에 추가

### 4. 재사용성
- 도메인 로직을 여러 애플리케이션에서 재사용
- 다른 프로젝트에서도 활용 가능

## 향후 계획

### 1. 점진적 마이그레이션
- 기존 서비스들을 새로운 구조로 단계적 이동
- 레거시 코드 제거

### 2. 추가 도메인
- 사용자 관리 도메인
- 결제 도메인
- 알림 도메인

### 3. 인프라 개선
- 데이터베이스 리포지토리 패턴 적용
- 캐싱 전략 구현
- 로깅 및 모니터링 강화

## 결론

이 아키텍처는 **도메인 중심 설계**의 핵심 원칙을 따르며, 비즈니스 로직의 명확한 분리와 유지보수성 향상을 목표로 합니다. 각 계층의 책임이 명확하게 정의되어 있어, 개발팀이 코드를 이해하고 수정하기 쉬운 구조를 제공합니다.
