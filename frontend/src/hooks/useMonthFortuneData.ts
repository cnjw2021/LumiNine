'use client';

import { useState, useEffect } from 'react';
import api from '@/utils/api';
import { MonthAcquiredFortuneResponse, PeriodFortuneData } from '@/types/directionFortune';

/**
 * 現在の節月に該当する月運データを取得するカスタムフック。
 * month-acquired-fortune APIを呼び出し、period_start/period_endの日付範囲から
 * 今日の日付に該当する月のデータのみを返す。
 */
export const useMonthFortuneData = (mainStar: number, monthStar: number, targetYear: number) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentMonthData, setCurrentMonthData] = useState<PeriodFortuneData | null>(null);

    useEffect(() => {
        if (!mainStar || !monthStar || mainStar < 1 || mainStar > 9 || monthStar < 1 || monthStar > 9) {
            setLoading(false);
            return;
        }

        const fetchData = async () => {
            setLoading(true);
            try {
                const year = targetYear || new Date().getFullYear();
                const response = await api.get(
                    `/nine-star/month-acquired-fortune?main_star=${mainStar}&month_star=${monthStar}&target_year=${year}`
                );

                if (response.data) {
                    const data = response.data as MonthAcquiredFortuneResponse;
                    if (data.annual_directions) {
                        const found = findCurrentSetsuMonth(data.annual_directions);
                        setCurrentMonthData(found);
                    }
                }
                setError(null);
            } catch (err) {
                console.error('月の運気情報の取得に失敗しました:', err);
                setError('月の運気データの取得に失敗しました。');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [mainStar, monthStar, targetYear]);

    return { loading, error, currentMonthData };
};

/**
 * 節月判定: 今日の日付がperiod_start〜period_endに含まれる月を検索する。
 */
function findCurrentSetsuMonth(
    annualDirections: Record<string, PeriodFortuneData>
): PeriodFortuneData | null {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (const data of Object.values(annualDirections)) {
        if (!data.period_start || !data.period_end) continue;
        const start = new Date(data.period_start);
        const end = new Date(data.period_end);
        start.setHours(0, 0, 0, 0);
        end.setHours(23, 59, 59, 999);
        if (today >= start && today <= end) {
            return {
                ...data,
                display_month: `${data.display_month} ${data.zodiac[1]}`,
            };
        }
    }
    return null;
}
