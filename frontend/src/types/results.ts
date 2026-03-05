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
} 