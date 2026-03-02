'use client';

import { useEffect, useState } from 'react';
import MainStarWithInfo from './MainStarWithInfo';
import api from '@/utils/api';

// 結果データの型定義
interface ResultData {
  result: {
    main_star: ResultStar;
    month_star: ResultStar;
    day_star: ResultStar;
    hour_star: ResultStar;
    year_star: ResultStar;
    birth_datetime: string;
    target_year: number;
  };
  fullName: string;
  birthdate: string;
  birthtime: string;
  gender: string;
  targetYear?: number;
}

interface ResultProps {
  resultData: ResultData;
  onReset: () => void;
}

// MainStarWithInfoコンポーネントのStar型と互換性のある型を定義
interface StarForInfo {
  number: number;
  name_jp: string;
  name_en?: string;
  element?: string;
  description?: string;
  keywords?: string;
  title?: string;     // 特性タイトルを追加
  advice?: string;    // アドバイスを追加
}

// 結果データの星情報の型定義
interface ResultStar {
  star_number: number;
  name_jp: string;
  name_en?: string;
  element?: string;
  description?: string;
  keywords?: string;
}

// 月命星読みの型定義
interface MonthStarReading {
  id: number;
  star_number: number;
  title: string;
  keywords: string;
  description: string;
}

// 日命星読みの型定義
interface DailyStarReading {
  id: number;
  star_number: number;
  title: string;
  keywords: string | null;
  description: string;
  advice: string | null;
}

export default function SimpleResult({ resultData, onReset }: ResultProps) {
  const { result, fullName, birthdate } = resultData;
  const [monthStarReading, setMonthStarReading] = useState<MonthStarReading | null>(null);
  const [dailyStarReading, setDailyStarReading] = useState<DailyStarReading | null>(null);

  // 月命星読みと日命星読みのデータを取得
  useEffect(() => {
    if (!result) return;

    const fetchReadingData = async () => {
      try {
        const { month_star } = result;

        // 月命星の読みデータを取得
        const monthReadingResponse = await api.get(`/nine-star/month-star-readings?star_number=${month_star.star_number}`);
        if (monthReadingResponse.data && monthReadingResponse.data.length > 0) {
          setMonthStarReading(monthReadingResponse.data[0]);
        }

        // 日命星の読みデータを取得（生年月日が有効な場合のみ）
        if (birthdate) {
          const formattedBirthdate = birthdate.replace(/\//g, '-'); // YYYY/MM/DD → YYYY-MM-DD
          const dailyStarResponse = await api.get(`/nine-star/daily-star-reading?birth_date=${formattedBirthdate}`);
          if (dailyStarResponse.data && dailyStarResponse.data.day_reading) {
            setDailyStarReading(dailyStarResponse.data.day_reading);
          }
        }
      } catch (err) {
        console.error('読みデータの取得中にエラーが発生しました:', err);
      }
    };

    fetchReadingData();
  }, [result, birthdate]);

  if (!result) {
    return null;
  }

  const { main_star, month_star, day_star } = result;

  // 星番号に基づいて色を返す関数
  const getStarColor = (starNumber: number): string => {
    const colors = [
      '#3490dc',  // 1: 一白水星 - 鮮やかな青
      '#2d3748',  // 2: 二黒土星 - 深い黒
      '#38a169',  // 3: 三碧木星 - 爽やかな緑
      '#319795',  // 4: 四緑木星 - ティール
      '#ecc94b',  // 5: 五黄土星 - 黄金色
      '#a0aec0',  // 6: 六白金星 - シルバー
      '#e53e3e',  // 7: 七赤金星 - 情熱的な赤
      '#805ad5',  // 8: 八白土星 - 神秘的な紫
      '#ed64a6'   // 9: 九紫火星 - 鮮やかなピンク
    ];
    return colors[starNumber - 1] || '#3490dc';
  };

  // カンマ区切りのキーワード文字列を処理する関数
  const processKeywords = (keywordsStr: string | null | undefined): string => {
    if (!keywordsStr) return '';
    // カンマと読点を「・」に置き換えて整形
    return keywordsStr.replace(/[,、]/g, '・').trim();
  };

  // StarForInfo形式に変換する関数
  const formatStarForInfo = (star: ResultStar, additionalInfo?: Partial<StarForInfo>): StarForInfo => ({
    number: star.star_number,
    name_jp: star.name_jp,
    name_en: star.name_en || '',
    element: star.element || '',
    description: additionalInfo?.description || star.description || '',
    // キーワードの処理をprocessKeywords関数で統一
    keywords: processKeywords(additionalInfo?.keywords || star.keywords),
    title: additionalInfo?.title || '',
    advice: additionalInfo?.advice || '',
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ 
        padding: '20px', 
        backgroundColor: 'white', 
        borderRadius: '8px', 
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)', 
        border: '1px solid #e0e0e0'
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <h2 style={{ textAlign: 'center', fontSize: '1.2rem', fontWeight: 500, margin: 0 }}>
            {fullName}様の鑑定結果
          </h2>
          <p style={{ textAlign: 'center', color: '#666', margin: 0 }}>
            生年月日: {birthdate}
          </p>
          
          {/* 九星の数字表示セクション */}
          <div style={{ margin: '20px 0' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
              {/* 本命星 */}
              <div style={{
                borderRadius: '8px',
                padding: '10px',
                backgroundColor: `${getStarColor(main_star.star_number)}10`,
                border: `2px solid ${getStarColor(main_star.star_number)}80`,
                textAlign: 'center',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <p style={{ fontSize: '0.75rem', fontWeight: 600, color: '#666', margin: '0 0 5px 0' }}>本命星</p>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '2px' }}>
                  <span style={{ 
                    fontSize: '2.2rem', 
                    fontWeight: 800, 
                    color: getStarColor(main_star.star_number),
                    lineHeight: 1,
                    textShadow: '0px 2px 4px rgba(0,0,0,0.1)',
                    margin: 0
                  }}>
                    {main_star.star_number}
                  </span>
                  <span style={{
                    margin: '2px 0',
                    fontWeight: 600,
                    fontSize: '0.6rem',
                    backgroundColor: getStarColor(main_star.star_number),
                    color: 'white',
                    padding: '2px 4px',
                    borderRadius: '4px',
                    whiteSpace: 'nowrap',
                    minWidth: 'auto'
                  }}>
                    {main_star.name_jp}
                  </span>
                </div>
              </div>

              {/* 月命星 */}
              <div style={{
                borderRadius: '8px',
                padding: '10px',
                backgroundColor: `${getStarColor(month_star.star_number)}10`,
                border: `2px solid ${getStarColor(month_star.star_number)}80`,
                textAlign: 'center',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <p style={{ fontSize: '0.75rem', fontWeight: 600, color: '#666', margin: '0 0 5px 0' }}>月命星</p>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '2px' }}>
                  <span style={{ 
                    fontSize: '2.2rem', 
                    fontWeight: 800, 
                    color: getStarColor(month_star.star_number),
                    lineHeight: 1,
                    textShadow: '0px 2px 4px rgba(0,0,0,0.1)',
                    margin: 0
                  }}>
                    {month_star.star_number}
                  </span>
                  <span style={{
                    margin: '2px 0',
                    fontWeight: 600,
                    fontSize: '0.6rem',
                    backgroundColor: getStarColor(month_star.star_number),
                    color: 'white',
                    padding: '2px 4px',
                    borderRadius: '4px',
                    whiteSpace: 'nowrap',
                    minWidth: 'auto'
                  }}>
                    {month_star.name_jp}
                  </span>
                </div>
              </div>

              {/* 日命星 */}
              <div style={{
                borderRadius: '8px',
                padding: '10px',
                backgroundColor: `${getStarColor(day_star.star_number)}10`,
                border: `2px solid ${getStarColor(day_star.star_number)}80`,
                textAlign: 'center',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <p style={{ fontSize: '0.75rem', fontWeight: 600, color: '#666', margin: '0 0 5px 0' }}>日命星</p>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '2px' }}>
                  <span style={{ 
                    fontSize: '2.2rem', 
                    fontWeight: 800, 
                    color: getStarColor(day_star.star_number),
                    lineHeight: 1,
                    textShadow: '0px 2px 4px rgba(0,0,0,0.1)',
                    margin: 0
                  }}>
                    {day_star.star_number}
                  </span>
                  <span style={{
                    margin: '2px 0',
                    fontWeight: 600,
                    fontSize: '0.6rem',
                    backgroundColor: getStarColor(day_star.star_number),
                    color: 'white',
                    padding: '2px 4px',
                    borderRadius: '4px',
                    whiteSpace: 'nowrap',
                    minWidth: 'auto'
                  }}>
                    {day_star.name_jp}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 本命星のSVGと説明文 */}
      <MainStarWithInfo 
        star={formatStarForInfo(main_star)} 
        title={`本命星\n（性格・運命の流れ）`}
      />

      {/* 月命星のSVGと説明文 */}
      <MainStarWithInfo 
        star={formatStarForInfo(month_star, monthStarReading ? {
          description: monthStarReading.description,
          keywords: monthStarReading.keywords,
          title: monthStarReading.title
        } : undefined)} 
        title={`月命星\n（環境・対人関係）`}
        isMonthStar={true}
      />

      {/* 日命星のSVGと説明文 */}
      <MainStarWithInfo 
        star={formatStarForInfo(day_star, dailyStarReading ? {
          description: dailyStarReading.description,
          keywords: dailyStarReading.keywords || '',
          title: dailyStarReading.title,
          advice: dailyStarReading.advice || ''
        } : undefined)} 
        title={`日命星\n（行動・思考パターン）`}
        isDayStar={true}
      />

      {/* アクションボタン */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '30px' }}>
        <button 
          onClick={onReset}
          style={{
            padding: '10px 20px',
            fontSize: '1rem',
            backgroundColor: 'transparent',
            color: '#3490dc',
            border: '1px solid #3490dc',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 500,
            transition: 'all 0.2s ease'
          }}
        >
          新しい鑑定をする
        </button>
      </div>
    </div>
  );
} 