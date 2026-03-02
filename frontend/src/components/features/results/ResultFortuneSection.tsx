'use client';

import React, { useEffect, useState } from 'react';
import { Paper, Title, Text, Box, Grid, Stack, Loader, Card } from '@mantine/core';
import api from '@/utils/api';
import DirectionFortune from '../visualization/DirectionFortune';
import AnnualFortune from '../visualization/AnnualDirectionsGrid';
import { PeriodFortuneBoard } from '../visualization';

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

interface YearAcquiredFortuneData {
  directions: Record<string, YearPeriodData>;
  month_star: number;
  target_year: number;
}

// 年間吉方位情報の型
type AnnualFortuneData = PeriodData;

const ResultFortuneSection: React.FC<ResultFortuneSectionProps> = ({ mainStar, monthStar, targetYear, birthdate }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [yearlyData, setYearlyData] = useState<AnnualFortuneData[]>([]);
  const [monthStarData, setMonthStarData] = useState<StarData | null>(null);
  const [birthdayInfo, setBirthdayInfo] = useState<YearAcquiredFortuneData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // 方位の吉凶情報を取得（星番号が有効な場合のみ）
        if (mainStar && monthStar && mainStar >= 1 && mainStar <= 9 && monthStar >= 1 && monthStar <= 9) {
          try {
            // DirectionFortuneコンポーネントはuseDirectionFortuneDataフックを使って自らAPIを呼び出すため、
            // ここではdirection-fortune APIを呼び出さない
            // DirectionFortuneコンポーネントにデータを渡さない（undefinedのまま）

            // 年間吉方位情報を取得
            const annualDirectionsResponse = await api.get(
              `/nine-star/annual-directions?main_star=${mainStar}&month_star=${monthStar}&target_year=${targetYear || new Date().getFullYear()}`
            );

            if (annualDirectionsResponse.data) {
              console.log('API レスポンス (annual-directions):', annualDirectionsResponse.data);
              setYearlyData(annualDirectionsResponse.data as AnnualFortuneData[]);
            }

            // 時の運気情報を取得
            const monthAcquiredFortuneResponse = await api.get(
              `/nine-star/month-acquired-fortune?main_star=${mainStar}&month_star=${monthStar}&target_year=${targetYear || new Date().getFullYear()}`
            );

            if (monthAcquiredFortuneResponse.data) {
              console.log('API レスポンス (time-directions):', monthAcquiredFortuneResponse.data);
              setMonthStarData(monthAcquiredFortuneResponse.data as StarData);
            }

            // 3年分の時の運気情報を取得
            const yearAcquiredFortuneResponse = await api.get(
              `/nine-star/year-acquired-fortune?main_star=${mainStar}&month_star=${monthStar}&target_year=${targetYear || new Date().getFullYear()}`
            );

            if (yearAcquiredFortuneResponse.data) {
              console.log('API レスポンス (year-acquired-fortune):', yearAcquiredFortuneResponse.data);
              setBirthdayInfo(yearAcquiredFortuneResponse.data as YearAcquiredFortuneData);
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
      {/* 3年分の時の運気情報表示 */}
      {/* {birthdayInfo && (
        <Paper shadow="sm" p="md" withBorder>
          <Stack gap="md">
            <Title order={3}>{targetYear ?? new Date().getFullYear()}〜{(targetYear ?? new Date().getFullYear()) + 2} 年の運気</Title>
            <Box>
              <Grid gutter={{ base: 'sm', sm: 'md' }} align="stretch">
                {Object.entries(birthdayInfo.directions)
                  .sort(([a], [b]) => {
                    // year_2023, year_2024...の形式をソート
                    const yearA = parseInt(a.split('_')[1]);
                    const yearB = parseInt(b.split('_')[1]);
                    return yearA - yearB;
                  })
                  .map(([key, periodData]) => {
                    const periodDataFormat = {
                      center_star: periodData.star_number,
                      display_month: `${periodData.year}年 ${periodData.zodiac}`,
                      display_year: '',
                      month: 0, // 月データではないので0を設定
                      year: periodData.year,
                      zodiac: periodData.zodiac,
                      directions: periodData.directions,
                      period_start: periodData.period_start,
                      period_end: periodData.period_end
                    };

                    return (
                      <Grid.Col key={key} span={{ base: 12, sm: 4 }} mb="md">
                        <PeriodFortuneBoard periodData={periodDataFormat} />
                      </Grid.Col>
                    );
                  })}
              </Grid>
            </Box>
          </Stack>
        </Paper>
      )} */}

      {/* 月の運気情報表示 */}
      {/* {monthStarData?.annual_directions && (
        <Paper shadow="sm" p="md" withBorder>
          <Stack gap="md">
            <Title order={3}>{targetYear}年 月の運気</Title>
            <Box>
              <Grid gutter={{ base: 'sm', sm: 'md' }} align="stretch">
                {Object.entries(monthStarData.annual_directions)
                  .sort(([a], [b]) => {
                    // month_1, month_2...の形式をソート
                    const monthA = parseInt(a.split('_')[1]);
                    const monthB = parseInt(b.split('_')[1]);
                    
                    // 1月は最後に表示するための特別な処理
                    if (monthA === 1) return 1;
                    if (monthB === 1) return -1;
                    
                    return monthA - monthB;
                  })
                  .map(([key, periodData]) => {
                    return (
                      <Grid.Col key={key} span={{ base: 12, sm: 6, md: 4 }} mb="md">
                        <PeriodFortuneBoard periodData={{
                          ...periodData,
                          display_month: `${periodData.display_month} ${periodData.zodiac[1]}`
                        }} />
                      </Grid.Col>
                    );
                  })}
              </Grid>
            </Box>
          </Stack>
        </Paper>
      )} */}

      <Card shadow="sm" p="md" withBorder>
        <DirectionFortune
          mainStar={mainStar}
          monthStar={monthStar}
          title={`${targetYear}年`}
          targetYear={targetYear}
        />
      </Card>

      {/* 年間吉方位情報表示（一時的に表示させない） */}
      {targetYear === 0 && yearlyData.length > 0 && (
        <Paper shadow="sm" p="md" withBorder>
          <Stack gap="md">
            <Title order={3}>年間吉方位情報</Title>

            <Box>
              <Grid gutter={{ base: 'sm', sm: 'md' }} align="stretch">
                {yearlyData.map((periodData, index) => {
                  return (
                    <Grid.Col key={index} span={{ base: 12, sm: 6, md: 4 }} mb="md">
                      <AnnualFortune periodData={{
                        ...periodData,
                        // 1月の場合は翌年を表示するよう修正
                        display_month: periodData.month === 1
                          ? `${periodData.year + 1}年${periodData.month}月 ${periodData.zodiac[1]}`
                          : `${periodData.display_month} ${periodData.zodiac[1]}`
                      }} />
                    </Grid.Col>
                  );
                })}
              </Grid>
            </Box>
          </Stack>
        </Paper>
      )}
    </Stack>
  );
};

export default ResultFortuneSection; 