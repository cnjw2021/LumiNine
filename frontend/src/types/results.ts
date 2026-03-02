import { CalculationResult } from './stars';

// 結果データの型定義
export interface ResultData {
  result: CalculationResult;
  fullName: string;
  birthdate: string;
  birthtime: string;
  gender: string;
  targetYear?: number;
  isCompatibilityReading?: boolean;
}

// 相性鑑定文の型
export interface CompatibilityReading {
  id: number;
  pattern_code: string;
  theme?: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

// 相性鑑定結果の型
export interface CompatibilityResult {
  main_star: number;
  target_star: number;
  main_birth_month: number;
  target_birth_month: number;
  is_male: boolean;
  symbols: string;
  pattern_code: string;
  readings: {
    [theme: string]: CompatibilityReading;
  };
}

export interface PersonInfo {
  name: string;
  star: {
    star_number: number;
    star_name: string;
    star_element: string;
    star_kanji: string;
    star_attribute: string;
  };
  birthdate: string;
}

export interface CompatibilityData {
  result: CompatibilityResult;
  mainPerson: PersonInfo;
  targetPerson: PersonInfo;
  gender: 'male' | 'female';
}

// --- PDFジョブ最小ペイロード用の型 ---
export type Gender = 'male' | 'female';

export interface PartnerMinimal {
  fullName: string;
  birthdate: string; // YYYY-MM-DD
  gender: Gender;
}

export interface PdfJobResultDataMinimal {
  fullName: string;
  birthdate: string; // YYYY-MM-DD
  gender: Gender;
  targetYear: number;
  partner?: PartnerMinimal;
}

// Result コンポーネントのProps型定義
export interface ResultProps {
  resultData: ResultData;
  onReset: () => void;
  compatibilityData?: CompatibilityData | null;
} 