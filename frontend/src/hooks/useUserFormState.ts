'use client';

import { useState, useCallback, useMemo } from 'react';
import type { DateError } from '@/types/admin';
import {
    validateDates,
    validateEmail,
} from '@/utils/adminValidation';
import { notifications } from '@mantine/notifications';

// ── 型定義 ──────────────────────────────────────────

interface UserFormFields {
    name: string;
    email: string;
    password: string;
    subscriptionStart: string;
    subscriptionEnd: string;
    isAdmin: boolean;
}

interface UserFormErrors {
    emailError: string;
    dateError: DateError;
}

export interface UseUserFormStateReturn {
    // フィールド
    fields: UserFormFields;
    errors: UserFormErrors;
    // セッター
    setName: (v: string) => void;
    setEmail: (v: string) => void;
    setPassword: (v: string) => void;
    setSubscriptionStart: (v: string) => void;
    setSubscriptionEnd: (v: string) => void;
    setIsAdmin: (v: boolean) => void;
    // エラーセッター
    setEmailError: (v: string) => void;
    setDateError: (v: DateError) => void;
    // ユーティリティ
    reset: () => void;
    validate: (opts?: { requirePassword?: boolean }) => boolean;
}

// ── フック ──────────────────────────────────────────

/**
 * create/edit フォームで独立的に使用できるフォーム状態フック.
 *
 * 各インスタンスが独立した状態を持つため、
 * create と edit のフローがお互いの状態を干渉しない.
 *
 * 注意: `fields` と `errors` は useMemo で安定化されているため、
 * 依存配列に含めてもフィールド値が変わらない限り再実行されない.
 */
export function useUserFormState(): UseUserFormStateReturn {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [subscriptionStart, setSubscriptionStart] = useState('');
    const [subscriptionEnd, setSubscriptionEnd] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);
    const [emailError, setEmailError] = useState('');
    const [dateError, setDateError] = useState<DateError>({});

    const reset = useCallback(() => {
        setName('');
        setEmail('');
        setPassword('');
        setSubscriptionStart('');
        setSubscriptionEnd('');
        setIsAdmin(false);
        setEmailError('');
        setDateError({});
    }, []);

    const validate = useCallback((opts?: { requirePassword?: boolean }): boolean => {
        // エラー状態をクリア
        setEmailError('');
        setDateError({});

        if (!name.trim()) {
            notifications.show({
                title: 'エラー',
                message: '名前を入力してください',
                color: 'red',
            });
            return false;
        }

        const emailResult = validateEmail(email);
        if (!emailResult.valid) {
            setEmailError(emailResult.error);
            return false;
        }

        const dateResult = validateDates(subscriptionStart, subscriptionEnd);
        if (!dateResult.valid) {
            setDateError(dateResult.errors);
            return false;
        }

        const requirePw = opts?.requirePassword ?? false;
        if (requirePw && password.length < 8) {
            notifications.show({
                title: 'エラー',
                message: 'パスワードは8文字以上である必要があります',
                color: 'red',
            });
            return false;
        }
        if (!requirePw && password && password.length < 8) {
            notifications.show({
                title: 'エラー',
                message: 'パスワードは8文字以上である必要があります',
                color: 'red',
            });
            return false;
        }

        return true;
    }, [name, email, password, subscriptionStart, subscriptionEnd]);

    // useMemo で安定化: フィールド値が変わらない限り同一参照を維持
    const fields = useMemo<UserFormFields>(() => ({
        name, email, password, subscriptionStart, subscriptionEnd, isAdmin,
    }), [name, email, password, subscriptionStart, subscriptionEnd, isAdmin]);

    const errors = useMemo<UserFormErrors>(() => ({
        emailError, dateError,
    }), [emailError, dateError]);

    return {
        fields,
        errors,
        setName,
        setEmail,
        setPassword,
        setSubscriptionStart,
        setSubscriptionEnd,
        setIsAdmin,
        setEmailError,
        setDateError,
        reset,
        validate,
    };
}

