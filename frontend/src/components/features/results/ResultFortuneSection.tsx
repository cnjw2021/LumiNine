'use client';

import React, { useEffect, useState } from 'react';
import { Paper, Title, Text, Box, Grid, Stack, Loader, Card } from '@mantine/core';
import api from '@/utils/api';
import DirectionFortune from '../visualization/DirectionFortune';
import { PeriodFortuneBoard, PowerStoneSection } from '../visualization';

interface StarData {
  number: number;
  name_jp: string;
  name_en: string;
  element: string;
  description: string;
  annual_directions?: Record<string, PeriodData>; // 月の運気情報用に追加
}

interface ResultFortuneSectionProps {
  mainStar: number;
  monthStar: number;
  targetYear: number;
  birthdate?: string;
}

// 吉方位情報の型
interface DirectionInfo {
  is_auspicious: boolean;
  marks: string[];
  reason: string | null;
  is_main_star?: boolean;
  title?: string;
  details?: string;
}

// 期間データの型
interface PeriodData {
  center_star: number;
  display_month: string;
  month: number;
  year: number;
  zodiac: string;
  directions: Record<string, DirectionInfo>;
  period_start?: string;
  period_end?: string;
}

interface YearPeriodData {
  year: number;
  star_number: number;
  zodiac: string;
  directions: Record<string, DirectionInfo>;
  period_start?: string;
  period_end?: string;
}

const ResultFortuneSection: React.FC<ResultFortuneSectionProps> = ({ mainStar, monthStar, targetYear, birthdate }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [monthStarData, setMonthStarData] = useState<StarData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // 方位の吉凶情報を取得（星番号が有効な場合のみ）
        if (mainStar && monthStar && mainStar >= 1 && mainStar <= 9 && monthStar >= 1 && monthStar <= 9) {
          try {
            // 時の運気情報を取得
            const monthAcquiredFortuneResponse = await api.get(
              `/nine-star/month-acquired-fortune?main_star=${mainStar}&month_star=${monthStar}&target_year=${targetYear || new Date().getFullYear()}`
            );

            if (monthAcquiredFortuneResponse.data) {
              console.log('API レスポンス (time-directions):', monthAcquiredFortuneResponse.data);
              setMonthStarData(monthAcquiredFortuneResponse.data as StarData);
            }
          } catch (err) {
            console.error('方位の吉凶情報の取得に失敗しました:', err);
          }
        }

        setError(null);
      } catch (err: unknown) {
        console.error('鑑定データの取得中にエラーが発生しました:', err);
        setError('鑑定データの取得に失敗しました。ネットワーク接続を確認してください。');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [mainStar, monthStar, targetYear, birthdate]);

  if (loading) {
    return (
      <Paper shadow="sm" p="md" withBorder>
        <Stack align="center" py="xl">
          <Loader size="md" />
          <Text>鑑定データを読み込み中...</Text>
        </Stack>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper shadow="sm" p="md" withBorder>
        <Text color="red" ta="center">{error}</Text>
      </Paper>
    );
  }

  return (
    <Stack gap="xl">
      {/* 月の運気情報表示（現在の節月のみ） */}
      {(() => {
        if (!monthStarData?.annual_directions) return null;
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const currentMonth = Object.entries(monthStarData.annual_directions).find(
          ([, data]) => {
            if (!data.period_start || !data.period_end) return false;
            const start = new Date(data.period_start);
            const end = new Date(data.period_end);
            start.setHours(0, 0, 0, 0);
            end.setHours(23, 59, 59, 999);
            return today >= start && today <= end;
          }
        );
        if (!currentMonth) return null;
        const [key, periodData] = currentMonth;
        return (
          <PeriodFortuneBoard key={key} periodData={{
            ...periodData,
            display_month: `${periodData.display_month} ${periodData.zodiac[1]}`
          }} />
        );
      })()}

      {/* パワーストーン推薦 — DirectionFortuneから完全に独立 */}
      <PowerStoneSection
        mainStar={mainStar}
        monthStar={monthStar}
        targetYear={targetYear}
        birthDate={birthdate}
      />

    </Stack>
  );
};

export default ResultFortuneSection; 