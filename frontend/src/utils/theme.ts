/**
 * LumiNine Premium Design Tokens
 * 감정결과/인사이트 페이지의 "Premium Healing" 비주얼 랭귀지를 전체 앱에 통일
 */

// ─── Colors ──────────────────────────────────────────────────────────
export const COLORS = {
    /** 메인 페이지 배경 (warm off-white/beige) */
    primaryBg: '#f9f7f2',
    /** 카드/컨테이너 배경 */
    cardBg: '#ffffff',
    /** 악센트 (brass / gold) — 아이콘, 보더, 소제목 */
    accent: '#d4af37',
    /** 서브 악센트 (dusty rose) — 하이라이트, 키 넘버 */
    secondary: '#d8a7a7',
    /** 본문 텍스트 (soft charcoal) */
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
    /** 버튼 그라데이션 */
    button: { from: '#d4af37', to: '#d8a7a7' },
    /** 관리자 버튼 그라데이션 */
    adminButton: { from: '#d4af37', to: '#c5975a' },
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

// ─── Input Focus Ring ────────────────────────────────────────────────
export const INPUT_STYLES = {
    label: { color: COLORS.text },
    input: {
        '&:focus': {
            borderColor: COLORS.accent,
        },
    },
} as const;

// ─── Navigation Tokens ──────────────────────────────────────────────
export const NAV = {
    /** 사이드바 border */
    borderColor: `rgba(212, 175, 55, 0.1)`,
    /** 섹션 제목 */
    sectionTitle: COLORS.accent,
    /** 아이콘 default */
    iconColor: COLORS.accent,
    /** 호버 배경 */
    hoverBg: 'rgba(212, 175, 55, 0.08)',
    /** Active 항목 */
    activeColor: '#d8a7a7',
} as const;
