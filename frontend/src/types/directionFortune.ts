export interface DirectionStatus {
  is_auspicious: boolean | null;
  reason: string | null;
  marks: string[];
  compatibility_level?: string;
}

export interface DirectionFortuneStatus {
  north: DirectionStatus;
  northeast: DirectionStatus;
  east: DirectionStatus;
  southeast: DirectionStatus;
  south: DirectionStatus;
  southwest: DirectionStatus;
  west: DirectionStatus;
  northwest: DirectionStatus;
}

export interface MovingDateInfo {
  date: string;
  auspicious_directions: string[];
}

export interface WaterDrawingDateInfo {
  date: string;
  auspicious_directions: string[];
  auspicious_times?: Array<{ time: string; ganzhi: string }>;
}

export interface AuspiciousTableRow {
  month: number;
  cells: Record<string, string>;
}

export interface AuspiciousTableYear {
  year: number;
  headers: string[];
  rows: AuspiciousTableRow[];
}

export type AuspiciousTableData = AuspiciousTableYear[];

// ── Phase 4–5: パワーストーン推薦 ──

/** 구성기학 (五行) 기반 스톤 — base / monthly / protection */
export interface GogyoStone {
  stone_id: string;
  stone_name: string;
  /** Localized layer label (e.g. "基本石", "월운석") */
  layer: string;
  /** Localized 五行 label (e.g. "水", "Wood") */
  gogyo: string;
  /** Recommendation reason */
  reason: string;
}

/** 수비술 (Numerology) 기반 스톤 — overall / health / wealth / love */
export interface NumerologyStone {
  stone_id: string;
  stone_name: string;
  /** Localized layer label (e.g. "全体運", "건강운") */
  layer: string;
  /** Stone description */
  description: string;
  /** Secondary sub-stone */
  secondary: {
    stone_id: string;
    stone_name: string;
    description: string;
  };
}

/** Union type — either 구성기학 or 수비술 stone */
export type StoneRecommendation = GogyoStone | NumerologyStone;

/** 3-Layer response (birth_date not provided) */
export interface PowerStones {
  base_stone: GogyoStone;
  monthly_stone: GogyoStone;
  protection_stone: GogyoStone;
}

/** 6-Layer response (birth_date provided) */
export interface SixLayerPowerStones {
  overall_stone: NumerologyStone;
  health_stone: NumerologyStone;
  wealth_stone: NumerologyStone;
  love_stone: NumerologyStone;
  monthly_stone: GogyoStone;
  protection_stone: GogyoStone;
  life_path_number: number;
  planet: string;
}

/** Type guard: 6-Layer response has `overall_stone` key */
export function isSixLayer(
  stones: PowerStones | SixLayerPowerStones,
): stones is SixLayerPowerStones {
  return 'overall_stone' in stones;
}

/** Type guard: check if a stone is a GogyoStone */
export function isGogyoStone(stone: StoneRecommendation): stone is GogyoStone {
  return 'gogyo' in stone;
}