'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/utils/api';
import { AxiosError } from 'axios';
import { STORAGE_KEY, DEFAULT_BIRTH_TIME } from '@/components/features/form/readingFormConstants';
import { Gender } from '@/types';

/**
 * ReadingForm のAPI送信・結果保存
 *
 * SRP: バリデーション → API呼び出し → localStorage保存 → 画面遷移
 */

interface UseReadingSubmitParams {
    token: string;
    isSuperuser: boolean;
    currentYear: number;
}

interface SubmitData {
    birthdate: string;
    fullName: string;
    gender: Gender;
    targetYear: number;
}

export function useReadingSubmit({ token, isSuperuser, currentYear }: UseReadingSubmitParams) {
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const handleSubmit = useCallback(async (
        data: SubmitData,
        setError: (error: string | null) => void,
    ) => {
        const { birthdate, fullName, gender, targetYear } = data;

        // --- バリデーション ---
        if (!birthdate) {
            setError('生年月日を入力してください');
            return;
        }

        const birthdateParts = birthdate.split('/');
        if (birthdateParts.length !== 3) {
            setError('生年月日を正しく入力してください');
            return;
        }

        const [birthYearStr, birthMonthStr, birthDayStr] = birthdateParts;
        const birthYearNum = Number(birthYearStr);
        const birthMonthNum = Number(birthMonthStr);
        const birthDayNum = Number(birthDayStr);

        if (
            !Number.isInteger(birthYearNum) ||
            !Number.isInteger(birthMonthNum) ||
            !Number.isInteger(birthDayNum) ||
            birthMonthNum < 1 ||
            birthMonthNum > 12 ||
            birthDayNum < 1 ||
            birthDayNum > 31
        ) {
            setError('生年月日を正しく入力してください');
            return;
        }

        const birthDate = new Date(birthYearNum, birthMonthNum - 1, birthDayNum);
        if (
            birthDate.getFullYear() !== birthYearNum ||
            birthDate.getMonth() !== birthMonthNum - 1 ||
            birthDate.getDate() !== birthDayNum
        ) {
            setError('生年月日を正しく入力してください');
            return;
        }

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (birthDate > today) {
            setError('生年月日は未来の日付を指定できません');
            return;
        }

        // 非スーパーユーザーが未来年を指定した場合は currentYear に矯正
        const effectiveTargetYear = (!isSuperuser && targetYear > currentYear)
            ? currentYear
            : targetYear;

        if (!fullName) {
            setError('氏名を入力してください');
            return;
        }

        // --- API送信 ---
        setIsLoading(true);
        try {
            const normalizedMonth = birthMonthStr.padStart(2, '0');
            const normalizedDay = birthDayStr.padStart(2, '0');
            const birthDateTimeISO = `${birthYearStr}-${normalizedMonth}-${normalizedDay} ${DEFAULT_BIRTH_TIME}`;

            const response = await api.post('/nine-star/calculate', {
                birth_datetime: birthDateTimeISO,
                target_year: effectiveTargetYear,
            }, {
                headers: { Authorization: `Bearer ${token}` },
            });

            if (response.data) {
                // ローカルストレージのアクセス確認
                try {
                    localStorage.setItem('test-storage', 'test');
                    localStorage.removeItem('test-storage');
                } catch (storageAccessError) {
                    console.error('ローカルストレージアクセスエラー:', storageAccessError);
                    setError('ブラウザのストレージ設定が制限されています。プライベートブラウジングやCookieの設定を確認してください。');
                    return;
                }

                const userData = {
                    result: response.data,
                    fullName,
                    birthdate,
                    gender,
                    targetYear: effectiveTargetYear,
                };

                try {
                    localStorage.removeItem(STORAGE_KEY);
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(userData));
                } catch (storageSaveError) {
                    console.error('ローカルストレージ保存エラー:', storageSaveError);
                    setError('結果の保存中にエラーが発生しました。ブラウザのストレージ設定を確認してください。');
                    return;
                }

                router.push(`/result?t=${Date.now()}`);
            } else {
                setError('鑑定結果が返されませんでした');
            }
        } catch (err: unknown) {
            const errorMessage = err instanceof AxiosError
                ? err.response?.data?.error || '鑑定中にエラーが発生しました'
                : '鑑定中にエラーが発生しました';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    }, [token, isSuperuser, currentYear, router]);

    return { isLoading, handleSubmit };
}
