'use client';

import React from 'react';
import { isSixLayer, PowerStones, SixLayerPowerStones, PeriodFortuneData } from '@/types/directionFortune';
import YearlyFortuneSection from './YearlyFortuneSection';
import MonthlyFortuneSection from './MonthlyFortuneSection';

interface ResultFortuneSectionProps {
  targetYear: number;
  powerStones: PowerStones | SixLayerPowerStones | null;
  currentMonthData: PeriodFortuneData | null;
  loading: boolean;
  error: string | null;
}

const ResultFortuneSection: React.FC<ResultFortuneSectionProps> = ({
  targetYear,
  powerStones,
  currentMonthData,
  loading,
  error,
}) => {
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
        <span style={{ color: '#d4af37', fontSize: '14px' }}>鑑定データを読み込み中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '32px', color: '#d8a7a7' }}>
        {error}
      </div>
    );
  }

  const sixLayer = powerStones && isSixLayer(powerStones) ? powerStones : null;

  const monthlyStone = sixLayer?.monthly_stone
    ?? (powerStones && !isSixLayer(powerStones) ? powerStones.monthly_stone : null)
    ?? null;
  const protectionStone = sixLayer?.protection_stone
    ?? (powerStones && !isSixLayer(powerStones) ? powerStones.protection_stone : null)
    ?? null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
      {/* 今年の運勢 (Yearly Fortune) */}
      {sixLayer?.yearly_stone && (
        <YearlyFortuneSection
          yearlyStone={sixLayer.yearly_stone}
          targetYear={targetYear}
        />
      )}

      {/* 今月の運勢 (Monthly Direction Guide) */}
      <MonthlyFortuneSection
        currentMonthData={currentMonthData}
        monthlyStone={monthlyStone}
        protectionStone={protectionStone}
      />
    </div>
  );
};

export default ResultFortuneSection;