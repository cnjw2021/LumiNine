import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// 星の情報の型定義
interface Star {
  star_number: number;
  name_jp: string;
  name_en: string;
  element: string;
  keywords?: string;  // キーワード情報を追加
  created_at: string;
  updated_at: string;
}

// 月命星読みの型定義
interface MonthlyStarReading {
  id: number;
  star_number: number;
  title: string;
  keywords: string;
  description: string;
  created_at?: string;
  updated_at?: string;
}

// 日命星読みの型定義
interface DailyStarReading {
  id: number;
  star_number: number;
  title: string;
  keywords: string | null;
  description: string;
  advice: string | null;
  created_at?: string;
  updated_at?: string;
}

// 九星気学の結果の型定義
interface NineStarKiResult {
  birth_datetime: string;
  target_year: number;
  main_star: Star;
  month_star: Star;
  day_star: Star;
  hour_star: Star;
  year_star: Star;
}

// 性別の型定義
export type Gender = 'male' | 'female';

// ストアの状態の型定義
interface NineStarKiState {
  birthDateTime: string | null; // ISO形式の生年月日時
  birthdate: string | null;     // YYYY/MM/DD形式の生年月日
  birthtime: string | null;     // HH:MM形式の時間
  fullName: string | null;      // 氏名
  gender: Gender | null;        // 性別
  targetYear: number | null;    // 鑑定対象年
  result: NineStarKiResult | null; // 計算結果
  monthlyStarReading: MonthlyStarReading | null; // 月命星読みデータ
  dailyStarReading: DailyStarReading | null; // 日命星読みデータ
  setBirthDateTime: (birthDateTime: string) => void;
  setBirthdate: (birthdate: string) => void;
  setBirthtime: (birthtime: string) => void;
  setFullName: (fullName: string) => void;
  setGender: (gender: Gender) => void;
  setTargetYear: (targetYear: number) => void;
  setResult: (result: NineStarKiResult) => void;
  setMonthlyStarReading: (reading: MonthlyStarReading) => void; // 月命星読みデータを設定
  setDailyStarReading: (reading: DailyStarReading) => void; // 日命星読みデータを設定
  setUserData: (data: { 
    birthDateTime: string, 
    birthdate: string, 
    birthtime: string, 
    fullName: string,
    gender: Gender,
    targetYear?: number
  }) => void;
  reset: () => void;
}

// 九星気学ストアの作成
export const useNineStarKiStore = create<NineStarKiState>()(
  persist(
    (set) => ({
      birthDateTime: null,
      birthdate: null,
      birthtime: null,
      fullName: null,
      gender: null,
      targetYear: null,
      result: null,
      monthlyStarReading: null,
      dailyStarReading: null,
      
      // 生年月日時を設定（ISO形式）
      setBirthDateTime: (birthDateTime: string) => set({ birthDateTime }),
      
      // 生年月日を設定（YYYY/MM/DD形式）
      setBirthdate: (birthdate: string) => set({ birthdate }),
      
      // 時間を設定（HH:MM形式）
      setBirthtime: (birthtime: string) => set({ birthtime }),
      
      // 氏名を設定
      setFullName: (fullName: string) => set({ fullName }),
      
      // 性別を設定
      setGender: (gender: Gender) => set({ gender }),
      
      // 鑑定対象年を設定
      setTargetYear: (targetYear: number) => set({ targetYear }),
      
      // 結果を設定
      setResult: (result: NineStarKiResult) => set({ result }),

      // 月命星読みデータを設定
      setMonthlyStarReading: (reading: MonthlyStarReading) => set({ monthlyStarReading: reading }),
      
      // 日命星読みデータを設定
      setDailyStarReading: (reading: DailyStarReading) => set({ dailyStarReading: reading }),

      // ユーザーデータをまとめて設定
      setUserData: (data: { 
        birthDateTime: string, 
        birthdate: string, 
        birthtime: string, 
        fullName: string,
        gender: Gender,
        targetYear?: number
      }) => set({
        birthDateTime: data.birthDateTime,
        birthdate: data.birthdate,
        birthtime: data.birthtime,
        fullName: data.fullName,
        gender: data.gender,
        targetYear: data.targetYear !== undefined ? data.targetYear : null
      }),
      
      // ストアをリセット
      reset: () => set({ 
        birthDateTime: null, 
        birthdate: null, 
        birthtime: null, 
        fullName: null,
        gender: null,
        targetYear: null,
        result: null,
        monthlyStarReading: null,
        dailyStarReading: null,
      }, true), // trueを追加してステート全体を置き換え
    }),
    {
      name: 'ninestarki-storage', // ローカルストレージのキー
      partialize: (state) => ({
        // 保存するステートを選択
        birthDateTime: state.birthDateTime,
        birthdate: state.birthdate,
        birthtime: state.birthtime,
        fullName: state.fullName,
        gender: state.gender,
        targetYear: state.targetYear,
        result: state.result,
        monthlyStarReading: state.monthlyStarReading,
        dailyStarReading: state.dailyStarReading,
      }),
    }
  )
); 