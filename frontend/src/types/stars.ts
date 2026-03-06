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
export interface NumerologyResult {
  life_path_number: number;
  planet: string;
  planet_name: string;
  keywords: string[];
  description: string;
  strengths: string[];
  weaknesses: string[];
}

export interface CalculationResult {
  main_star: Star;
  month_star: Star;
  day_star: Star;
  hour_star: Star;
  year_star: Star;
  birth_datetime: string;
  target_year: number;
  numerology?: NumerologyResult;
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