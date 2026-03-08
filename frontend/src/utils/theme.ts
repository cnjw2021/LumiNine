/**
 * LumiNine Premium Design Tokens
 * 감정결과/인사이트 페이지의 "Premium Healing" 비주얼 랭귀지를 전체 앱에 통일
 *
 * 핵심 원칙:
 *  - gold(#d4af37)는 **서브 악센트** (섹션 라벨, 미세한 보더, 작은 아이콘)
 *  - dusty rose(#d8a7a7)는 **CTA / 주요 인터랙션** (버튼, 활성 탭)
 *  - 타이틀/본문은 **soft charcoal(#4a4a4a)** — 골드로 쓰지 않음
 */

// ─── Colors ──────────────────────────────────────────────────────────
export const COLORS = {
    /** 메인 페이지 배경 (warm off-white/beige) */
    primaryBg: '#f9f7f2',
    /** 카드/컨테이너 배경 */
    cardBg: '#ffffff',
    /** 서브 악센트 (brass / gold) — 섹션 라벨, 미세 보더, 아이콘 */
    accent: '#d4af37',
    /** CTA / 주요 버튼 (dusty rose) */
    rose: '#d8a7a7',
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
    /** 페이지 배경 그라데이션 (subtle radial) */
    pageBg: `
    radial-gradient(circle at 10% 10%, rgba(216, 167, 167, 0.03) 0%, transparent 40%),
    radial-gradient(circle at 90% 90%, rgba(155, 176, 165, 0.03) 0%, transparent 40%)
  `,
    /** CTA 버튼 — 단색 rose (Result 페이지와 동일) */
    button: { from: '#d8a7a7', to: '#d8a7a7' },
    /** 관리자 버튼 — 미묘한 rose 그라데이션 */
    adminButton: { from: '#d8a7a7', to: '#c9a0a0' },
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
    border: '1px solid rgba(212, 175, 55, 0.08)',
    boxShadow: '0 5px 20px -5px rgba(0, 0, 0, 0.03)',
} as const;

// ─── Button Styling (Result 페이지와 동일) ─────────────────────────
export const BUTTON = {
    /** CTA (primary) — pill 형태, dusty rose */
    primary: {
        backgroundColor: COLORS.rose,
        color: '#FFF',
        borderRadius: '9999px',
        border: 'none',
        fontSize: '13px',
        letterSpacing: '0.2em',
        fontFamily: FONTS.body,
        boxShadow: '0 10px 20px -5px rgba(216, 167, 167, 0.25)',
    },
    /** Secondary — ghost pill, gold border */
    secondary: {
        backgroundColor: 'transparent',
        color: COLORS.accent,
        borderRadius: '9999px',
        border: '1px solid rgba(212, 175, 55, 0.3)',
        fontSize: '13px',
        letterSpacing: '0.2em',
        fontFamily: FONTS.body,
    },
} as const;

// ─── Section Header (Result의 "YEARLY FORTUNE", "RECOMMENDED STONES" 스타일) ─
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
    /** 사이드바 border */
    borderColor: `rgba(212, 175, 55, 0.1)`,
    /** 섹션 제목 — gold 서브 악센트 */
    sectionTitle: COLORS.accent,
    /** 아이콘 default — muted gold */
    iconColor: 'rgba(212, 175, 55, 0.6)',
    /** 호버 배경 */
    hoverBg: 'rgba(212, 175, 55, 0.06)',
    /** Active 항목 — dusty rose */
    activeColor: COLORS.rose,
} as const;
