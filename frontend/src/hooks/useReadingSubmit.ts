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

        const [birthYear, birthMonth, birthDay] = birthdate.split('/');
        const birthDate = new Date(`${birthYear}-${birthMonth}-${birthDay}`);
        birthDate.setHours(0, 0, 0, 0);

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (birthDate > today) {
            setError('生年月日は未来の日付を指定できません');
            return;
        }

        if (!isSuperuser && targetYear > currentYear) {
            setError(`${currentYear}年より未来の年は鑑定できません`);
            return;
        }

        if (!fullName) {
            setError('氏名を入力してください');
            return;
        }

        // --- API送信 ---
        setIsLoading(true);
        try {
            const birthdateParts = birthdate.split('/');
            if (birthdateParts.length !== 3) {
                setError('生年月日の形式が正しくありません');
                setIsLoading(false);
                return;
            }

            const [year, month, day] = birthdateParts;
            const birthDateTimeISO = `${year}-${month}-${day} ${DEFAULT_BIRTH_TIME}`;

            const response = await api.post('/nine-star/calculate', {
                birth_datetime: birthDateTimeISO,
                target_year: targetYear,
            }, {
                headers: { Authorization: `Bearer ${token}` },
            });

            if (response.data) {
                try {
                    // ローカルストレージのアクセス確認
                    try {
                        localStorage.setItem('test-storage', 'test');
                        localStorage.removeItem('test-storage');
                    } catch (storageAccessError) {
                        console.error('ローカルストレージアクセスエラー:', storageAccessError);
                        setError('ブラウザのストレージ設定が制限されています。プライベートブラウジングやCookieの設定を確認してください。');
                        setIsLoading(false);
                        return;
                    }

                    const userData = {
                        result: response.data,
                        fullName,
                        birthdate,
                        gender,
                        targetYear,
                    };

                    localStorage.removeItem(STORAGE_KEY);
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(userData));

                    router.push(`/result?t=${Date.now()}`);
                } catch (storageError) {
                    console.error('データ保存エラー:', storageError);
                    setError('結果の保存中にエラーが発生しました');
                    setIsLoading(false);
                }
            } else {
                setError('鑑定結果が返されませんでした');
                setIsLoading(false);
            }
        } catch (err: unknown) {
            const errorMessage = err instanceof AxiosError
                ? err.response?.data?.error || '鑑定中にエラーが発生しました'
                : '鑑定中にエラーが発生しました';
            setError(errorMessage);
            setIsLoading(false);
        }
    }, [token, isSuperuser, currentYear, router]);

    return { isLoading, handleSubmit };
}
