'use client';

import React from 'react';
import { Paper, Text, Stack, Loader } from '@mantine/core';
import { PeriodFortuneBoard, PowerStoneSection } from '../visualization';
import { useMonthFortuneData } from '@/hooks/useMonthFortuneData';

interface ResultFortuneSectionProps {
  mainStar: number;
  monthStar: number;
  targetYear: number;
  birthdate?: string;
}

const ResultFortuneSection: React.FC<ResultFortuneSectionProps> = ({ mainStar, monthStar, targetYear, birthdate }) => {
  const { loading, error, currentMonthData } = useMonthFortuneData(mainStar, monthStar, targetYear);

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
      {currentMonthData && (
        <PeriodFortuneBoard periodData={currentMonthData} />
      )}

      {/* パワーストーン推薦 */}
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