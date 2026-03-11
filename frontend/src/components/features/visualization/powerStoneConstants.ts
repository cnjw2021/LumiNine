/**
 * PowerStoneCard 定数・メタデータ定義
 *
 * SSoT: 五行テーマ, レイヤーメタ, ローカライズマップを一元管理
 */

// ── 五行(五行) 色상 맵 ──────────────────────────────────
export const GOGYO_THEME: Record<string, { bg: string; border: string; badge: string; label: string }> = {
    '水': { bg: 'linear-gradient(135deg, rgba(30,136,229,0.10) 0%, rgba(30,136,229,0.04) 100%)', border: 'rgba(30,136,229,0.35)', badge: 'blue', label: '水 (Water)' },
    '木': { bg: 'linear-gradient(135deg, rgba(67,160,71,0.10)  0%, rgba(67,160,71,0.04)  100%)', border: 'rgba(67,160,71,0.35)', badge: 'green', label: '木 (Wood)' },
    '火': { bg: 'linear-gradient(135deg, rgba(229,57,53,0.10)  0%, rgba(229,57,53,0.04)  100%)', border: 'rgba(229,57,53,0.35)', badge: 'red', label: '火 (Fire)' },
    '土': { bg: 'linear-gradient(135deg, rgba(249,168,37,0.10) 0%, rgba(249,168,37,0.04) 100%)', border: 'rgba(249,168,37,0.35)', badge: 'gray', label: '土 (Earth)' },
    '金': { bg: 'linear-gradient(135deg, rgba(120,144,156,0.10) 0%, rgba(120,144,156,0.04) 100%)', border: 'rgba(120,144,156,0.35)', badge: 'yellow', label: '金 (Metal)' },
};

// ── 3-Layer メタ ─────────────────────────────────────────
export const LAYER_META_3: Record<string, { icon: string; label: string; sublabel: string }> = {
    base: { icon: '💎', label: '基本石', sublabel: '本命石 — 一生の守護石' },
    monthly: { icon: '🌙', label: '月運石', sublabel: '今月の吉方位エネルギー' },
    protection: { icon: '🛡️', label: '護身石', sublabel: '今月の凶方位を抑制' },
};

// ── 7-Layer メタ ─────────────────────────────────────────
export const LAYER_META_7: Record<string, { icon: string; label: string; sublabel: string; color: string }> = {
    overall: { icon: '💎', label: '全体運', sublabel: '人生の総合的な守護石', color: '#7c3aed' },
    health: { icon: '❤️', label: '健康運', sublabel: '心身の健康をサポート', color: '#dc2626' },
    wealth: { icon: '💰', label: '財運', sublabel: '豊かさと繁栄を引き寄せる', color: '#d97706' },
    love: { icon: '💕', label: '恋愛運', sublabel: '愛と人間関係の調和', color: '#ec4899' },
    yearly: { icon: '✨', label: '年運石', sublabel: '今年のエネルギー補充石', color: '#f59e0b' },
    monthly: { icon: '🌙', label: '月運石', sublabel: '今月の吉方位エネルギー', color: '#0891b2' },
    protection: { icon: '🛡️', label: '護身石', sublabel: '今月の凶方位を抑制', color: '#4b5563' },
};

export const DEFAULT_THEME = { bg: 'rgba(240,240,240,0.3)', border: 'rgba(200,200,200,0.4)', badge: 'gray', label: '?' };

// ── ローカライズ正規化 ──────────────────────────────────
export const LAYER_LABEL_TO_KEY: Record<string, string> = {
    '基本石': 'base', '기본석': 'base', 'Base Stone': 'base', 'base': 'base',
    '月運石': 'monthly', '월운석': 'monthly', 'Monthly Stone': 'monthly', 'monthly': 'monthly',
    '護身石': 'protection', '호신석': 'protection', 'Protection Stone': 'protection', 'protection': 'protection',
};

export const GOGYO_NORMALIZE: Record<string, string> = {
    '水': '水', 'Water': '水', '수': '水',
    '木': '木', 'Wood': '木', '목': '木',
    '火': '火', 'Fire': '火', '화': '火',
    '土': '土', 'Earth': '土', '토': '土',
    '金': '金', 'Metal': '金', '금': '金',
};
