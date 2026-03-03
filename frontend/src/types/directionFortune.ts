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

// ── Phase 4: パワーストーン推薦 ──

export interface StoneRecommendation {
  stone_id: string;
  stone_name: string;
  /** Localized layer label (e.g. "基本石", "기본석", "Base Stone") */
  layer: string;
  /** Localized 五行 label (e.g. "水", "수", "Water") */
  gogyo: string;
  reason: string;
}

export interface PowerStones {
  base_stone: StoneRecommendation;
  monthly_stone: StoneRecommendation;
  protection_stone: StoneRecommendation;
}