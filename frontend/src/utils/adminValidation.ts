import dayjs from 'dayjs';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import type { DateError } from '@/types/admin';

dayjs.extend(customParseFormat);

/**
 * 管理画面で使用するバリデーションユーティリティ
 * 純粋関数として抽出し、テスト容易性を確保
 */

/** 日付のバリデーション（YYYY/MM/DD形式 + 範囲チェック） */
export function validateDates(start: string, end: string): { valid: boolean; errors: DateError } {
    if (!start || !end) {
        return {
            valid: false,
            errors: {
                startDate: '日付を入力してください',
                endDate: '日付を入力してください',
            },
        };
    }

    // YYYY/MM/DD形式のバリデーション
    const datePattern = /^\d{4}\/\d{2}\/\d{2}$/;
    if (!datePattern.test(start) || !datePattern.test(end)) {
        return {
            valid: false,
            errors: {
                startDate: '日付は YYYY/MM/DD 形式で入力してください',
                endDate: '日付は YYYY/MM/DD 形式で入力してください',
            },
        };
    }

    const startDate = dayjs(start, 'YYYY/MM/DD', true);
    const endDate = dayjs(end, 'YYYY/MM/DD', true);

    if (!startDate.isValid() || !endDate.isValid()) {
        return {
            valid: false,
            errors: {
                startDate: '有効な日付を入力してください',
                endDate: '有効な日付を入力してください',
            },
        };
    }

    if (endDate.isBefore(startDate) || endDate.isSame(startDate)) {
        return {
            valid: false,
            errors: {
                endDate: '終了日は開始日より後の日付を選択してください',
            },
        };
    }

    return { valid: true, errors: {} };
}

/** メールアドレスのバリデーション */
export function validateEmail(email: string): { valid: boolean; error: string } {
    if (!email) {
        return { valid: false, error: 'メールアドレスを入力してください' };
    }

    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(email)) {
        return { valid: false, error: '有効なメールアドレスを入力してください' };
    }

    return { valid: true, error: '' };
}

/** 日付文字列をYYYY/MM/DD形式にフォーマット */
export function formatDateSlash(dateStr: string | undefined | null): string {
    if (!dateStr) return '-';
    return dayjs(dateStr).format('YYYY/MM/DD');
}

/** YYYY/MM/DD → YYYY-MM-DD（API送信用） */
export function formatDateForApi(dateSlash: string): string {
    return dateSlash.replace(/\//g, '-');
}
