// 星情報の型定義
export interface Star {
  star_number: number;
  name_jp: string;
  name_en: string;
  element: string;
  keywords?: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

// 計算結果の型定義
export interface CalculationResult {
  main_star: Star;
  month_star: Star;
  day_star: Star;
  hour_star: Star;
  year_star: Star;
  birth_datetime: string;
  target_year: number;
}

// 月命星読みの型定義
export interface MonthStarReading {
  id: number;
  star_number: number;
  title: string;
  keywords: string;
  description: string;
}

// 日命星読みの型定義
export interface DailyStarReading {
  id: number;
  star_number: number;
  title: string;
  keywords: string | null;
  description: string;
  advice: string | null;
}

// 結果表示用の星情報
export interface StarForInfo {
  number: number;
  name_jp: string;
  name_en?: string;
  element?: string;
  description?: string;
  keywords?: string;
  title?: string;     // 特性タイトル
  advice?: string;    // アドバイス
} 