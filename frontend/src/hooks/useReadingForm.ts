'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Gender } from '@/types';
import { ERROR_TIMEOUT_MS, FOCUS_DELAY_MS } from '@/components/features/form/readingFormConstants';

/**
 * ReadingForm の入力状態管理
 *
 * SRP: フォーム状態の管理と年度バリデーションのみを担当
 */

interface UseReadingFormParams {
    isSuperuser: boolean;
    currentYear: number;
}

export function useReadingForm({ isSuperuser, currentYear }: UseReadingFormParams) {
    const [birthdate, setBirthdate] = useState<string>('');
    const [fullName, setFullName] = useState<string>('');
    const [gender, setGender] = useState<Gender>('male');
    const [targetYear, setTargetYear] = useState<number>(currentYear);
    const [error, setError] = useState<string | null>(null);
    const birthdateInputRef = useRef<HTMLInputElement>(null);

    // コンポーネントマウント時に生年月日フィールドにフォーカス
    useEffect(() => {
        const timer = setTimeout(() => {
            if (birthdateInputRef.current) {
                birthdateInputRef.current.focus();
            }
        }, FOCUS_DELAY_MS);

        return () => clearTimeout(timer);
    }, []);

    // 年度の入力チェック
    const handleYearChange = useCallback((value: string | number) => {
        if (value === null || value === undefined || value === '') return;

        const numValue = typeof value === 'string' ? parseInt(value, 10) : value;

        // スーパーユーザーでなく、現在年より未来が入力された場合
        if (!isSuperuser && numValue > currentYear) {
            setError(`${currentYear}年以降の鑑定はできません。現在の年に修正しました。`);
            setTargetYear(currentYear);

            setTimeout(() => {
                setError(null);
            }, ERROR_TIMEOUT_MS);
        } else {
            if (error && error.includes('鑑定はできません')) {
                setError(null);
            }
            setTargetYear(numValue);
        }
    }, [isSuperuser, currentYear, error]);

    return {
        birthdate,
        setBirthdate,
        fullName,
        setFullName,
        gender,
        setGender,
        targetYear,
        error,
        setError,
        birthdateInputRef,
        handleYearChange,
    };
}
