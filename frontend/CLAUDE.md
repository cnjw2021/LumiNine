# Frontend 모듈 가이드

## 🎯 해당 모듈의 책임 범위
- 사용자에게 제공되는 웹 인터페이스(UI/UX) 구현.
- 사용자의 정보(생년월일 등) 입력 폼 제공 및 구성기학 계산 결과(백엔드 API 호출) 시각화 데이터 렌더링.
- 클라이언트 측의 라우팅 처리 및 전역/지역 상태 관리.

## 📂 주요 파일별 역할
- `src/app/`: Next.js App Router 구조의 페이지 컴포넌트들 보관. `page.tsx` (개별 페이지), `layout.tsx` (공통 레이아웃).
- `src/components/`: 재사용 가능한 UI 컴포넌트 (ex: Button, Input, Modal, 九星盤 시각화 등 UI 조각들).
- `src/hooks/`: 컴포넌트 로직의 재사용을 위한 Custom React Hooks (예: API 호출 훅, 폼 관리 훅).
- `src/types/`: TypeScript 타입 정의 모음 (API 응답 스키마, 주요 모델 타입).
- `src/utils/`: 데이터 포맷팅이나 공통 헬퍼 함수들의 집합.
- `next.config.js` / `eslint.config.mjs`: Next.js 설정 및 ESLint 규칙 파일.

## 📦 외부 의존성
- **Next.js**: SSR 및 정적 사이트 생성을 지원하는 React 프레임워크.
- **React (TypeScript)**: UI 라이브러리.
- **Mantine UI**: 프로젝트에서 사용된 주요 UI 컴포넌트 프레임워크 (README 참조).
- **Tailwind CSS / PostCSS** (존재하는 경우): 스타일링 툴킷. (현재 `postcss.config.js`가 존재함).

## ⚠️ 수정 시 주의사항
1. **App Router 활용 인식**: Next.js 13+의 App Router를 사용하고 있으므로, Server Component 기반으로 동작하는 파일인지, Client Component(`"use client"`) 기반인지 명확하게 구분하여 작성해야 합니다. 상태(State)나 훅스(Hooks)가 필요한 경우는 반드시 Client Component로 선언하세요.
2. **API 연동 분리**: 백엔드 API와의 통신을 각 컴포넌트 안에서 직접 처리하지 말고, 가급적 `src/utils/`의 API 클라이언트나 `src/hooks/` 등을 통해 캡슐화하여 사용하세요.
3. **타입 안전성 확보**: `any` 타입 사용을 지양하고 가급적 `src/types/` 하위에 명시된 타입을 활용하여 런타임 이전의 에러를 방지하세요.
