import api from '@/utils/api';

// 型定義
export interface NineStarKiFormData {
  // フォームデータの型定義
  birthdate: string;
  gender: string;
  name?: string;
}

export interface NineStarKiResult {
  // 結果データの型定義
  main_star: number;
  month_star: number;
  day_star: number;
  personal_year_star: number;
  personal_month_star: number;
  personal_day_star: number;
  date_string: string;
  gender: string;
  name?: string;
}

export interface CombinationFortuneResult {
  // 鑑定結果データの型定義
  fortune: {
    basic: {
      title: string;
      description: string;
      advice?: string;
    };
    color: {
      title: string;
      description: string;
      advice?: string;
    };
    place: {
      title: string;
      description: string;
      advice?: string;
    };
  };
  attributes: {
    main_star: {
      color: string[];
      place: string[];
      item: string[];
      food: string[];
      direction: string[];
    };
    month_star: {
      color: string[];
      place: string[];
      item: string[];
      food: string[];
      direction: string[];
    };
  };
}

// 星と人生のガイダンス情報の型定義
export interface StarLifeGuidanceResult {
  main_star: number;
  month_star: number;
  job: string | null;
  lucky_color: string | null;
  lucky_item: string | null;
}

/**
 * 九星気学フォームの結果を取得
 */
export const fetchNineStarKiResult = async (formData: NineStarKiFormData): Promise<NineStarKiResult> => {
  const response = await api.post<NineStarKiResult>('/nine-star/result', formData);
  return response.data;
};

/**
 * 本命星と月命星の組み合わせによる鑑定結果を取得
 */
export const fetchCombinationFortune = async (mainStar: number, monthStar: number): Promise<CombinationFortuneResult> => {
  const response = await api.get<CombinationFortuneResult>(`/nine-star/combination-fortune?main_star=${mainStar}&month_star=${monthStar}`);
  return response.data;
};

/**
 * 本命星と月命星に基づく適職、ラッキーカラー、ラッキーアイテムの情報を取得
 */
export const fetchStarLifeGuidance = async (mainStar: number, monthStar: number): Promise<StarLifeGuidanceResult> => {
  const response = await api.get<StarLifeGuidanceResult>(`/star-life-guidance?main_star=${mainStar}&month_star=${monthStar}`);
  return response.data;
};

/**
 * 鑑定データを一括登録（管理者用）
 */
export const batchCreateStarFortune = async (data: StarFortuneData[]): Promise<BatchProcessResult> => {
  const response = await api.post<BatchProcessResult>('/admin/star-fortune-batch', data);
  return response.data;
};

/**
 * 属性データを一括登録（管理者用）
 */
export const batchCreateStarAttribute = async (data: StarAttributeData[]): Promise<BatchProcessResult> => {
  const response = await api.post<BatchProcessResult>('/admin/star-attribute-batch', data);
  return response.data;
};

// 型定義
export interface StarFortuneData {
  main_star: number;
  month_star: number;
  category: string;
  title: string;
  description: string;
  advice?: string;
}

export interface StarAttributeData {
  main_star: number;
  month_star?: number | null;
  attribute_type: string;
  attribute_value: string;
  description?: string;
  weight?: number;
}

export interface BatchProcessResult {
  message: string;
  results: {
    created: number;
    updated: number;
    failed: number;
    errors: Array<{
      data: StarFortuneData | StarAttributeData;
      error: string;
    }>;
  };
} 