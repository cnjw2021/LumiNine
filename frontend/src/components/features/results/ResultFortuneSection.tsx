'use client';

import React from 'react';
import { Stack, Loader, Text, Paper } from '@mantine/core';
import { usePowerStoneData } from '@/hooks/usePowerStoneData';
import { useMonthFortuneData } from '@/hooks/useMonthFortuneData';
import { isSixLayer } from '@/types/directionFortune';
import NumerologyProfileSection from './NumerologyProfileSection';
import YearlyFortuneSection from './YearlyFortuneSection';
import MonthlyFortuneSection from './MonthlyFortuneSection';

interface ResultFortuneSectionProps {
  mainStar: number;
  monthStar: number;
  mainStarName: string;
  monthStarName: string;
  targetYear: number;
  birthdate?: string;
}

/**
 * 鑑定結果セクション — 3つのセクションを時間軸順に表示
 *
 * Section A: 数秘プロフィール (Life Path — 一生涯)
 * Section B: 今年の運勢 (Personal Year — 今年)
 * Section C: 今月の運勢 (九星気学 — 今月)
 */
const ResultFortuneSection: React.FC<ResultFortuneSectionProps> = ({
  mainStar,
  monthStar,
  mainStarName,
  monthStarName,
  targetYear,
  birthdate,
}) => {
  // パワーストーンデータ
  const {
    loading: stonesLoading,
    powerStones,
    error: stonesError,
  } = usePowerStoneData(mainStar, monthStar, targetYear, birthdate);

  // 月の方位データ
  const {
    loading: fortuneLoading,
    currentMonthData,
    error: fortuneError,
  } = useMonthFortuneData(mainStar, monthStar, targetYear);

  const loading = stonesLoading || fortuneLoading;
  const error = stonesError || fortuneError;

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
        <Text c="red" ta="center">{error}</Text>
      </Paper>
    );
  }

  const sixLayer = powerStones && isSixLayer(powerStones) ? powerStones : null;

  // 3-Layer フォールバック: birth_date 未提供時でも monthly/protection stone を表示
  const monthlyStone = sixLayer?.monthly_stone
    ?? (powerStones && !isSixLayer(powerStones) ? powerStones.monthly_stone : null)
    ?? null;
  const protectionStone = sixLayer?.protection_stone
    ?? (powerStones && !isSixLayer(powerStones) ? powerStones.protection_stone : null)
    ?? null;

  return (
    <Stack gap="lg">
      {/* ─── Section A: 数秘プロフィール (一生涯) ─── */}
      {sixLayer && (
        <NumerologyProfileSection stoneData={sixLayer} />
      )}

      {/* ─── Section B: 今年の運勢 ─── */}
      {sixLayer?.yearly_stone && (
        <YearlyFortuneSection
          yearlyStone={sixLayer.yearly_stone}
          personalYearNumber={sixLayer.personal_year_number}
        />
      )}

      {/* ─── Section C: 今月の運勢 (九星気学) ─── */}
      <MonthlyFortuneSection
        mainStar={{ star_number: mainStar, name_jp: mainStarName }}
        monthStar={{ star_number: monthStar, name_jp: monthStarName }}
        currentMonthData={currentMonthData}
        monthlyStone={monthlyStone}
        protectionStone={protectionStone}
      />
    </Stack>
  );
};

export default ResultFortuneSection;