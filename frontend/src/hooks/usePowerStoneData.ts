'use client';

import { useState, useEffect } from 'react';
import api from '@/utils/api';
import { PowerStones } from '@/types/directionFortune';

/**
 * パワーストーン推薦データを独立して取得するフック。
 * monthly-board API から現在の節月に該当する power_stones を取得する。
 *
 * DirectionFortune とは完全に分離されており、
 * 任意のコンポーネントで自由に配置・表示制御が可能。
 */
export const usePowerStoneData = (mainStar: number, monthStar: number, targetYear?: number) => {
    const [loading, setLoading] = useState(false);
    const [powerStones, setPowerStones] = useState<PowerStones | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!mainStar || !monthStar || mainStar < 1 || mainStar > 9 || monthStar < 1 || monthStar > 9) {
            setPowerStones(null);
            return;
        }

        const fetchPowerStones = async () => {
            setLoading(true);
            setError(null);
            setPowerStones(null);

            try {
                const year = targetYear || new Date().getFullYear();
                const res = await api.get(
                    `/monthly/monthly-board?main_star=${mainStar}&month_star=${monthStar}&year=${year}`
                );

                if (res.data?.monthly_boards) {
                    const today = new Date().toISOString().slice(0, 10);
                    const boards = res.data.monthly_boards as Record<
                        string,
                        { period_start?: string; period_end?: string; power_stones?: PowerStones }
                    >;
                    const currentBoard = Object.values(boards).find(
                        (b) => b.period_start && b.period_end && b.period_start <= today && today <= b.period_end
                    );
                    setPowerStones(currentBoard?.power_stones ?? null);
                }
            } catch (err) {
                console.warn('パワーストーンデータの取得に失敗:', err);
                setError('パワーストーンデータの取得に失敗しました');
            } finally {
                setLoading(false);
            }
        };

        fetchPowerStones();
    }, [mainStar, monthStar, targetYear]);

    return { loading, powerStones, error };
};
