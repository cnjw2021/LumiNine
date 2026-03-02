'use client';

import { useState, useEffect } from 'react';
import api from '@/utils/api';
import { DirectionFortuneStatus, MovingDateInfo, WaterDrawingDateInfo, AuspiciousTableData } from '@/types/directionFortune';

export const useDirectionFortuneData = (mainStar: number, monthStar: number, targetYear?: number) => {
    const [loading, setLoading] = useState(true);
    const [directionFortuneStatus, setDirectionFortuneStatus] = useState<DirectionFortuneStatus | null>(null);
    const [yearlyStar, setYearlyStar] = useState<number | null>(null);
    const [zodiac, setZodiac] = useState<string>('');
    const [springStartDate, setSpringStartDate] = useState<string>('');
    const [springEndDate, setSpringEndDate] = useState<string>('');
    const [movingDates, setMovingDates] = useState<MovingDateInfo[]>([]);
    const [waterDrawingDates, setWaterDrawingDates] = useState<WaterDrawingDateInfo[]>([]);
    const [movingTable, setMovingTable] = useState<AuspiciousTableData>([]);
    const [waterDrawingTable, setWaterDrawingTable] = useState<AuspiciousTableData>([]);

    useEffect(() => {
        if (!mainStar || !monthStar) {
            setLoading(false);
            return;
        };

        const fetchData = async () => {
            setLoading(true);
            try {
                const year = targetYear || new Date().getFullYear();
                
                // 1. 年運星、干支、立春情報などを一括で取得
                const yearInfoResponse = await api.get(`/nine-star/year-star?year=${year}`);
                if (yearInfoResponse.data) {
                    setYearlyStar(yearInfoResponse.data.star_number);
                    setZodiac(yearInfoResponse.data.zodiac);
                    setSpringStartDate(yearInfoResponse.data.spring_start_date);
                    setSpringEndDate(yearInfoResponse.data.spring_end_date);
                }

                // 2. 方位の吉凶情報を取得
                const fortuneStatusResponse = await api.get(`/nine-star/direction-fortune?main_star=${mainStar}&month_star=${monthStar}&year=${year}`);
                setDirectionFortuneStatus(fortuneStatusResponse.data);

                // 3. 引越し吉日・水取り吉日を一括で取得
                const auspiciousDatesResponse = await api.get(`/reports/auspicious-days?year=${year}&mainStar=${mainStar}&monthStar=${monthStar}`);
                if (auspiciousDatesResponse.data) {
                    setMovingDates(auspiciousDatesResponse.data.moving_dates || []);
                    setWaterDrawingDates(auspiciousDatesResponse.data.water_drawing_dates || []);
                    setMovingTable(auspiciousDatesResponse.data.moving_table || []);
                    setWaterDrawingTable(auspiciousDatesResponse.data.water_drawing_table || []);
                }
            } catch (error) {
                console.error("方位運データの取得中にエラーが発生しました:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [mainStar, monthStar, targetYear]);

    return { loading, directionFortuneStatus, yearlyStar, zodiac, springStartDate, springEndDate, movingDates, waterDrawingDates, movingTable, waterDrawingTable };
};