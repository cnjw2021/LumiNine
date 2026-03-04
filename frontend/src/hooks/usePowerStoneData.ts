'use client';

import { useState, useEffect } from 'react';
import api from '@/utils/api';
import { PowerStones, SixLayerPowerStones } from '@/types/directionFortune';

/** Type guard: 6-Layer response has `overall_stone` key */
export function isSixLayer(
    stones: PowerStones | SixLayerPowerStones,
): stones is SixLayerPowerStones {
    return 'overall_stone' in stones;
}

/**
 * パワーストーン推薦データを独立して取得するフック。
 * monthly-board API から現在の節月に該当する power_stones を取得する。
 *
 * DirectionFortune とは完全に分離されており、
 * 任意のコンポーネントで自由に配置・表示制御が可能。
 *
 * @param birthDate 生年月日 (YYYY-MM-DD) — 提供時は 6-Layer 応答
 */
export const usePowerStoneData = (
    mainStar: number,
    monthStar: number,
    targetYear?: number,
    birthDate?: string,
) => {
    const [loading, setLoading] = useState(false);
    const [powerStones, setPowerStones] = useState<PowerStones | SixLayerPowerStones | null>(null);
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
                let url = `/monthly/monthly-board?main_star=${mainStar}&month_star=${monthStar}&year=${year}`;

                // birth_date がある場合 6-Layer 応答を要求
                if (birthDate) {
                    const normalized = birthDate.replace(/\//g, '-');
                    url += `&birth_date=${encodeURIComponent(normalized)}`;
                }

                const res = await api.get(url);

                if (res.data?.monthly_boards) {
                    const today = new Date().toISOString().slice(0, 10);
                    const boards = res.data.monthly_boards as Record<
                        string,
                        { period_start?: string; period_end?: string; power_stones?: PowerStones | SixLayerPowerStones }
                    >;
                    const currentBoard = Object.values(boards).find(
                        (b) => b.period_start && b.period_end && b.period_start <= today && today < b.period_end
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
    }, [mainStar, monthStar, targetYear, birthDate]);

    return { loading, powerStones, error };
};
