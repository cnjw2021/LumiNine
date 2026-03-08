# Frontend 모듈 가이드

## 🎯 해당 모듈의 책임 범위
- 사용자에게 제공되는 웹 인터페이스(UI/UX) 구현.
- 사용자의 정보(생년월일 등) 입력 폼 제공 및 감정 결과(백엔드 API 호출) 시각화·PDF 출력.
- 클라이언트 측의 라우팅 처리 및 인증 상태 관리.

## 📂 주요 파일별 역할
- `src/app/`: Next.js App Router 구조의 페이지 컴포넌트들.
  - `(auth)/`: 인증 관련 페이지 — `login`, `admin`, `password-change`
  - `(features)/`: 기능 페이지 — `appraisal` (감정 폼), `about/*` (소개 페이지 3종)
  - `result/`: 감정 결과 페이지 (localStorage에서 데이터 로드)
- `src/components/`: 재사용 가능한 UI 컴포넌트.
  - `common/ui/`: 공통 UI (Datepicker 등)
  - `features/form/`: `ReadingForm` — 메인 감정 입력 폼
  - `features/results/`: `Result`, `ResultFortuneSection` — 결과 표시
  - `features/visualization/`: `PowerStoneSection` — 파워스톤 시각화
  - `layout/`: `Navigation` — 전체 네비게이션
- `src/contexts/auth/`: React Context 기반 인증 상태 관리 (`AuthContext`).
- `src/hooks/`: Custom React Hooks.
  - `usePdfReport.ts`: html2canvas + jsPDF 기반 PDF 생성 (크로스브라우저 방어 로직 포함)
  - `usePowerStoneData.ts`: 파워스톤 데이터 가공
  - `useMonthFortuneData.ts`: 월운 데이터 가공
  - `useAdminCheck.ts`: 관리자 권한 체크
- `src/types/`: TypeScript 타입 정의 (`stars.ts`, `results.ts`, `directionFortune.ts`, `navigation.ts`).
- `src/utils/`: API 클라이언트(`api.ts`), 테마(`theme.ts`), 포맷터 등 공통 유틸리티.
- `public/images/stones/`: AI 생성 파워스톤 이미지 30종.

## 📦 외부 의존성
- **Next.js (App Router)**: SSR 및 정적 사이트 생성을 지원하는 React 프레임워크.
- **React (TypeScript)**: UI 라이브러리.
- **Mantine UI**: 프로젝트 전체에서 사용되는 주요 UI 컴포넌트 프레임워크.
- **html2canvas + jsPDF**: 클라이언트 사이드 PDF 생성.
- **Axios**: HTTP 클라이언트 (백엔드 API 통신).
- **Day.js**: 날짜 처리 라이브러리.

## ⚠️ 수정 시 주의사항
1. **App Router 활용**: Next.js 13+의 App Router를 사용하고 있으므로, Server Component 기반으로 동작하는 파일인지, Client Component(`"use client"`) 기반인지 명확하게 구분하여 작성해야 합니다. 상태(State)나 훅스(Hooks)가 필요한 경우는 반드시 Client Component로 선언하세요.
2. **API 연동 분리**: 백엔드 API와의 통신을 각 컴포넌트 안에서 직접 처리하지 말고, `src/utils/api.ts`의 API 클라이언트나 `src/hooks/` 등을 통해 캡슐화하여 사용하세요.
3. **타입 안전성 확보**: `any` 타입 사용을 지양하고 `src/types/` 하위에 명시된 타입을 활용하여 런타임 이전의 에러를 방지하세요.
4. **PDF 크로스브라우저**: `usePdfReport.ts`에 iOS Safari 메모리 방어, 폰트 로딩 대기, 빈 canvas 검증 등 방어 로직이 적용되어 있으므로, PDF 관련 수정 시 이 패턴을 유지하세요.
