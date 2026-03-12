# Frontend 모듈 가이드

> Last updated: 2026-03-12

## 🎯 해당 모듈의 책임 범위
- 사용자에게 제공되는 웹 인터페이스(UI/UX) 구현.
- 사용자의 정보(생년월일 등) 입력 폼 제공 및 감정 결과(백엔드 API 호출) 시각화·PDF 출력.
- 관리자 대시보드: 유저 관리(CRUD), 시스템 설정(계정 제한), 권한 관리.
- 클라이언트 측의 라우팅 처리 및 인증 상태 관리.
- **배포**: Cloudflare Pages (GitHub Actions 자동 배포, `@cloudflare/next-on-pages` 어댑터 사용).

## 📂 주요 파일별 역할
- `next.config.js`: Next.js 설정. `output: 'standalone'`은 Cloud Run/Docker 전용 (`CF_PAGES` 미설정 시). Cloudflare Pages 빌드 시(`CF_PAGES=1`) standalone 비활성화. 프로덕션 환경에서는 rewrites 비활성화 — `NEXT_PUBLIC_API_URL`로 백엔드 URL 직접 지정.
- `src/app/`: Next.js App Router 구조의 페이지 컴포넌트들.
  - `layout.tsx`: 루트 레이아웃 (Mantine Provider, Navigation, AppShell 설정)
  - `page.tsx`: 메인 페이지
  - `providers.tsx`: 전역 Provider 래퍼
  - `(auth)/`: 인증 관련 페이지 — `login` (로그인), `admin/` (관리자 대시보드 + `admin/users/` 유저 관리)
  - `(features)/`: 기능 페이지 — `appraisal` (감정 폼), `about/*` (소개 페이지 3종: ninestarki, numerology, powerstone), `password-change` (패스워드 변경)
  - `result/`: 감정 결과 페이지 (localStorage에서 데이터 로드)
- `src/components/`: 재사용 가능한 UI 컴포넌트.
  - `common/auth/PermissionGuard.tsx`: 권한 기반 조건부 렌더링 컴포넌트
  - `common/ui/Datepicker.tsx`: 공통 Datepicker 컴포넌트
  - `ui/`: shadcn 스타일 기본 UI 컴포넌트 (button, card, input, table, tabs, use-toast)
  - `features/form/`: `ReadingForm` — 메인 감정 입력 폼 + `readingFormConstants.ts` (폼 상수)
  - `features/results/`: 결과 표시 컴포넌트
    - `Result.tsx`: 메인 결과 페이지 컴포넌트
    - `ResultFortuneSection.tsx`: 운세 섹션
    - `MonthlyFortuneSection.tsx`: 월운 섹션
    - `YearlyFortuneSection.tsx`: 연운 섹션
    - `FoodRecommendationSection.tsx`: 본명성 기반 추천 음식 섹션
    - `NumerologyProfileSection.tsx` / `NumerologyStarInfo.tsx`: 수비술 프로필
    - `BasePowerstonesSection.tsx`: 기본 파워스톤 표시
  - `features/admin/`: 관리자 UI 컴포넌트
    - `UserTable.tsx`: 유저 목록 테이블
    - `UserFormModal.tsx`: 유저 생성/수정 모달
    - `SystemStatsPanel.tsx`: 시스템 통계 패널
    - `SystemLimitModal.tsx`: 시스템 제한 설정 모달
    - `AccountLimitModal.tsx`: 계정 제한 설정 모달
  - `features/visualization/`: 파워스톤 시각화
    - `PowerStoneSection.tsx`: 섹션 래퍼
    - `PowerStoneCard.tsx`: 개별 파워스톤 카드
    - `SixLayerStoneItem.tsx` / `StoneItem3.tsx`: 스톤 아이템 컴포넌트
    - `powerStoneConstants.ts`: 파워스톤 레이어 상수
  - `layout/`: 네비게이션 — `Navigation.tsx` (전체 네비게이션), `NavigationContent.tsx` (네비게이션 콘텐츠), `NavigationMenu.tsx` (메뉴 컴포넌트), `DrawerHeader.tsx` (모바일 드로어 헤더), `ScrollIndicator.tsx` (스크롤 인디케이터)
  - `styles/`: CSS 파일 — `result.css` (결과 페이지 + PDF 캡처 모드 스타일), `form.css` (폼 스타일), `paragraph.css` (문단 스타일)
- `src/contexts/auth/`: React Context 기반 인증 상태 관리 (`AuthContext`).
- `src/hooks/`: Custom React Hooks.
  - `usePdfReport.ts`: html2canvas + jsPDF 기반 PDF 생성. **Off-screen clone 패턴** 사용 — 원본 DOM을 변경하지 않고 `cloneNode(true)` → `document.body`에 붙여 A4 폭(794px) 데스크톱 레이아웃으로 캡처. iOS Safari 메모리 방어, 폰트 로딩 대기, 빈 canvas 검증 등 크로스브라우저 방어 로직 포함.
  - `usePowerStoneData.ts`: 파워스톤 데이터 가공
  - `useMonthFortuneData.ts`: 월운 데이터 가공
  - `useAdminCheck.ts`: 관리자 권한 체크
  - `useMenuPermissions.ts`: 메뉴 권한 상태 관리
  - `useNavigationMenuItems.ts`: 네비게이션 메뉴 아이템 구성
  - `useReadingForm.ts`: 감정 폼 상태 관리
  - `useReadingSubmit.ts`: 감정 제출 로직 (API 호출, 결과 저장)
  - `useSystemStats.ts`: 시스템 통계 데이터 조회 (관리자용)
  - `useUserFormState.ts`: 유저 폼 상태 관리 (관리자용)
  - `useUserManagement.ts`: 유저 관리 CRUD 훅 (관리자용)
- `src/types/`: TypeScript 타입 정의 (`stars.ts`, `results.ts`, `directionFortune.ts`, `navigation.ts`, `admin.ts`, `index.ts`).
- `src/utils/`: 공통 유틸리티.
  - `api.ts`: Axios 기반 API 클라이언트 (인터셉터, 토큰 관리)
  - `theme.ts`: Mantine 테마 설정
  - `stoneImageMap.ts`: 파워스톤 이미지 매핑
  - `adminValidation.ts`: 관리자 폼 유효성 검증
  - `apiErrorUtils.ts`: API 에러 처리 유틸리티
- `public/images/stones/`: AI 생성 파워스톤 이미지 32종 (`stoneImageMap.ts`의 `STONE_IDS`와 1:1 매핑).

## 📦 외부 의존성
- **Next.js (App Router)**: SSR 및 정적 사이트 생성을 지원하는 React 프레임워크.
- **React (TypeScript)**: UI 라이브러리.
- **Mantine UI**: 프로젝트 전체에서 사용되는 주요 UI 컴포넌트 프레임워크.
- **html2canvas + jsPDF**: 클라이언트 사이드 PDF 생성.
- **Axios**: HTTP 클라이언트 (백엔드 API 통신).
- **Day.js**: 날짜 처리 라이브러리.

## 🔐 환경변수
- `NEXT_PUBLIC_API_URL`: 백엔드 API **베이스 URL** (`/api`를 포함하지 않는 값). `src/utils/api.ts`에서 이 값에 `/api`를 자동으로 붙여 baseURL을 구성합니다.
  - 로컬 docker-compose: `NEXT_PUBLIC_API_URL=http://localhost:5001` (`.env.development.frontend`)
  - 프로덕션(Cloudflare Pages): GitHub Secrets에 `NEXT_PUBLIC_API_URL=https://831shop.site`
  - **⚠️ 주의**: `/api`를 포함하면 `/api/api/` 중복 발생. 미설정 시 docker-compose rewrite 사용.

## ⚠️ 수정 시 주의사항
1. **App Router 활용**: Server Component 기반으로 동작하는 파일인지, Client Component(`"use client"`) 기반인지 명확하게 구분. 상태(State)나 훅스(Hooks)가 필요한 경우는 반드시 Client Component로 선언하세요.
2. **API 연동 분리**: 백엔드 API와의 통신을 각 컴포넌트 안에서 직접 처리하지 말고, `src/utils/api.ts`의 API 클라이언트나 `src/hooks/` 등을 통해 캡슐화하여 사용하세요.
3. **타입 안전성 확보**: `any` 타입 사용을 지양하고 `src/types/` 하위에 명시된 타입을 활용하세요.
4. **PDF 크로스브라우저**: `usePdfReport.ts`는 off-screen clone 패턴을 사용하여 원본 DOM 무간섭으로 PDF를 생성합니다. iOS Safari 메모리 방어, 폰트 로딩 대기, 빈 canvas 검증, AppShell overflow:hidden 우회 등의 방어 로직이 적용되어 있으므로, PDF 관련 수정 시 이 패턴을 유지하세요.
5. **Cloudflare Pages 호환**: SSR이 필요한 경우 Cloudflare Workers(`@cloudflare/next-on-pages`) 어댑터 필요. API Route 추가 시 Edge Runtime 호환성 검토.
6. **API URL**: 프로덕션 환경에서 `/api/` 요청은 `NEXT_PUBLIC_API_URL`을 기반으로 처리됩니다. `next.config.js`의 rewrites는 `NODE_ENV !== 'production'`일 때만 활성화됩니다.
7. **CSS 캡처 모드**: `result.css`에 `.pdf-capture-mode` 클래스가 정의되어 있으며, off-screen clone에 적용되어 데스크톱 2열 레이아웃을 강제합니다. 결과 페이지 레이아웃 변경 시 이 클래스도 함께 업데이트하세요.
8. **관리자 컴포넌트**: 관리자 UI는 `features/admin/`에 집중되어 있으며, 관련 커스텀 훅(`useUserManagement`, `useSystemStats`, `useUserFormState`)을 통해 비즈니스 로직을 분리합니다.
