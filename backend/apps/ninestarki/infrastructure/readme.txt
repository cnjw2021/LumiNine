## infrastructure 디렉토리의 역할
"외부 연동이 없다면 infrastructure는 없는 구조여도 괜찮을까?" 라는 질문에 대한 답은 "네, 괜찮습니다." 입니다.

다만, infrastructure 계층은 데이터베이스 연동만을 위한 공간은 아닙니다.

만약 미래에 애플리케이션이 다음과 같은 외부 기술과 연동해야 한다면, 그 로직은 모두 infrastructure 디렉토리 안에 위치하게 됩니다.

외부 API 호출 (예: 날씨 정보 API, 소셜 로그인 API)

이메일 발송 서비스 (예: SMTP, SendGrid)

파일 스토리지 연동 (예: Amazon S3)

메시지 큐 (예: RabbitMQ)


---

## 인터페이스 위치 결정의 핵심 원칙
인터페이스의 위치를 결정하는 가장 좋은 질문은 "이 역할(Interface)이 '무엇'을 위한 것인가?" 입니다.

1. Repository 인터페이스 (예: UserRepository)
역할: User와 같은 **도메인 엔티티(Domain Entity)**의 생명주기(생성, 조회, 저장, 삭제)를 관리하는 것.

결론: domain 계층에 위치하는 것이 맞습니다.

이유: 어떻게 저장될지는(infrastructure의 관심사) 몰라도, "User는 어딘가에 저장되고 다시 불러올 수 있어야 한다"는 규칙 자체는 도메인의 핵심적인 요구사항이기 때문입니다. 즉, 도메인 계층이 자신의 엔티티를 어떻게 관리할지에 대한 '명세서(Interface)'를 직접 정의하는 것입니다.

2. 외부 시스템 인터페이스 (예: PdfGenerator, EmailSender)
역할: 특정 유즈케이스의 결과를 외부에 표현하거나(PDF 생성), 유즈케이스의 부수적인 효과를 발생시키는 것(이메일 발송).

결론: use_cases (Application) 계층에 위치하는 것이 더 적합합니다.

이유: '보고서'라는 도메인 데이터는 PDF가 될 수도, Excel 파일이 될 수도, 단순한 JSON이 될 수도 있습니다. 'PDF로 만든다'는 것은 여러 표현 방식 중 하나일 뿐, 도메인의 핵심 규칙이 아닙니다. 이것은 어플리케이션(Use Case)이 도메인 데이터를 어떻게 활용하여 사용자에게 보여줄 것인가에 대한 관심사입니다.


인터페이스 종류
- Repository Interfaces (AuspiciousDayRepository)
  - 위치: domain
    - 이유: 도메인 엔티티의 생명주기를 관리하는 것은 도메인의 핵심 관심사이기 때문입니다.

- 외부 시스템 Interfaces (PdfGenerator, PaymentGateway)
  - 위치: use_cases
    - 이유: PDF 생성, 결제 등은 특정 유즈케이스의 결과물 또는 부수효과이며, 도메인 자체의 규칙은 아니기 때문입니다.