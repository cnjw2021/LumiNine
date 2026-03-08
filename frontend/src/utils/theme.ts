/**
 * LumiNine Premium Design Tokens
 * 감정결과/인사이트 페이지의 "Premium Healing" 비주얼 랭귀지를 전체 앱에 통일
 *
 * 핵심 원칙:
 *  - gold(#d4af37)는 **미세 보더, 구분선** 에만 사용
 *  - dusty rose(#d4b0b0)는 **CTA / 주요 인터랙션** (버튼, 활성 탭)
 *  - sage green(#5a8a6e)은 **네비/아이콘** 악센트 (길흉방위 그리드 톤)
 *  - 타이틀/본문은 **soft charcoal(#4a4a4a)**
 *  - 섹션 라벨은 **dimmed charcoal(#9a9a9a)**
 */

// ─── Colors ──────────────────────────────────────────────────────────
export const COLORS = {
    /** 메인 페이지 배경 (warm off-white/beige) */
    primaryBg: '#f9f7f2',
    /** 카드/컨테이너 배경 */
    cardBg: '#ffffff',
    /** 서브 악센트 (brass / gold) — 미세 보더, 구분선 */
    accent: '#d4af37',
    /** CTA / 주요 버튼 (밝은 dusty rose) */
    rose: '#d4b0b0',
    /** 세이지 그린 (방위 그리드 톤) — 네비 아이콘 */
    sage: '#5a8a6e',
    /** 본문 텍스트 (soft charcoal) — 타이틀도 이 색상 사용 */
    text: '#4a4a4a',
    /** 라벨/캡션 텍스트 */
    textDimmed: '#7a7a7a',
    /** 에러 */
    error: '#c0392b',
    /** 성공 */
    success: '#27ae60',
} as const;

// ─── Gradients ───────────────────────────────────────────────────────
export const GRADIENTS = {
    /** 페이지 배경 그라데이션 — sage green tint 포함 */
    pageBg: `
    radial-gradient(circle at 10% 10%, rgba(90, 138, 110, 0.04) 0%, transparent 40%),
    radial-gradient(circle at 90% 90%, rgba(212, 176, 176, 0.03) 0%, transparent 40%)
  `,
    /** CTA 버튼 — 밝은 rose */
    button: { from: '#d4b0b0', to: '#d4b0b0' },
    /** 관리자 버튼 */
    adminButton: { from: '#d4b0b0', to: '#c9a6a6' },
} as const;

// ─── Typography ──────────────────────────────────────────────────────
export const FONTS = {
    /** 타이틀 (전통적, 우아) */
    title: '"Shippori Mincho", "Noto Serif JP", serif',
    /** 본문 */
    body: '"Noto Serif JP", serif',
    /** 캡션/라벨 (모던 산세리프) */
    caption: '"Montserrat", sans-serif',
} as const;

// ─── Card Styling ────────────────────────────────────────────────────
export const CARD = {
    borderRadius: '16px',
    border: '1px solid rgba(90, 138, 110, 0.06)',
    boxShadow: '0 5px 20px -5px rgba(0, 0, 0, 0.03)',
} as const;

// ─── Button Styling (Result 페이지 기반) ─────────────────────────
export const BUTTON = {
    /** CTA (primary) — pill 형태, 밝은 dusty rose */
    primary: {
        backgroundColor: '#d4b0b0',
        color: '#FFF',
        borderRadius: '9999px',
        border: 'none',
        fontSize: '15px',
        fontWeight: 600,
        lineHeight: 1.5,
        padding: '12px 24px',
        letterSpacing: '0.2em',
        fontFamily: FONTS.body,
        boxShadow: '0 10px 20px -5px rgba(212, 176, 176, 0.2)',
    },
    /** Secondary — ghost pill, sage border */
    secondary: {
        backgroundColor: 'transparent',
        color: COLORS.sage,
        borderRadius: '9999px',
        border: '1px solid rgba(90, 138, 110, 0.25)',
        fontSize: '13px',
        letterSpacing: '0.2em',
        fontFamily: FONTS.body,
    },
} as const;

// ─── Section Header (Result의 "YEARLY FORTUNE" 스타일) ──────────────
export const SECTION_HEADER = {
    color: COLORS.accent,
    fontSize: '11px',
    letterSpacing: '0.3em',
    fontWeight: 500,
    textTransform: 'uppercase' as const,
    fontFamily: FONTS.caption,
} as const;

// ─── Navigation Tokens ──────────────────────────────────────────────
export const NAV = {
    /** 사이드바 border — sage tint */
    borderColor: 'rgba(90, 138, 110, 0.08)',
    /** 섹션 제목 — dimmed charcoal (금색 X) */
    sectionTitle: '#9a9a9a',
    /** 아이콘 default — sage green */
    iconColor: 'rgba(90, 138, 110, 0.5)',
    /** 호버 배경 — subtle sage */
    hoverBg: 'rgba(90, 138, 110, 0.06)',
    /** Active 항목 — dusty rose */
    activeColor: '#d4b0b0',
    /** 네비게이션 배경 — warm beige + sage tint */
    bgColor: 'rgba(245, 247, 243, 0.95)',
} as const;
