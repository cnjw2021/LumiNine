'use client';

import { useState, useEffect } from 'react';
import api from '@/utils/api';
import { PeriodFortuneData } from '@/types/directionFortune';

/**
 * 現在の節月に該当する月運データを取得するカスタムフック。
 * monthly-board API を呼び出し、period_start/period_end の日付範囲から
 * 今日の日付に該当する月のデータのみを返す。
 *
 * Issue #68: month-acquired-fortune (旧) → monthly-board (新) に移行。
 * MonthlyDirectionsUseCase は正しく月干支 (month_zodiac) を使用するため、
 * 破 方位の計算が正確になる。
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
                    `/monthly/monthly-board?main_star=${mainStar}&month_star=${monthStar}&year=${year}`
                );

                if (response.data?.monthly_boards) {
                    const found = findCurrentSetsuMonth(response.data.monthly_boards);
                    setCurrentMonthData(found);
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
 * monthly-board API の応答 (monthly_boards) における1節月分のデータ型。
 */
interface MonthlyBoardEntry {
    setsu_month_index: number;
    center_star: number;
    month_zodiac: string;
    month_stem?: string;
    month_branch?: string;
    period_start: string;
    period_end: string;
    directions: Record<string, unknown>;
    power_stones?: unknown;
}

/**
 * 節月判定: 今日の日付が period_start 〜 period_end に含まれる月を検索し、
 * monthly-board 応答を PeriodFortuneData 形式に変換する。
 */
function findCurrentSetsuMonth(
    monthlyBoards: Record<string, MonthlyBoardEntry>
): PeriodFortuneData | null {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (const board of Object.values(monthlyBoards)) {
        if (!board.period_start || !board.period_end) continue;
        const start = new Date(`${board.period_start}T00:00:00`);
        const end = new Date(`${board.period_end}T23:59:59.999`);

        if (today >= start && today <= end) {
            // monthly-board 応答 → PeriodFortuneData 変換
            const startMonth = start.getMonth() + 1;
            const startYear = start.getFullYear();
            const zodiac = board.month_zodiac || '';
            const branch = board.month_branch || (zodiac.length >= 2 ? zodiac[1] : zodiac);

            return {
                center_star: board.center_star,
                display_month: `${startYear}年${startMonth}月 ${branch}`,
                month: startMonth,
                year: startYear,
                zodiac: zodiac,
                directions: board.directions as PeriodFortuneData['directions'],
                period_start: board.period_start,
                period_end: board.period_end,
                power_stones: board.power_stones as PeriodFortuneData['power_stones'],
            };
        }
    }
    return null;
}
