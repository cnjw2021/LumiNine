/**
 * 管理者ユーザー管理画面で使用する型定義
 */

/** ユーザー情報 */
export interface AdminUser {
    id: number;
    name: string;
    email: string;
    is_superuser?: boolean;
    is_admin?: boolean;
    subscription_start?: string;
    subscription_end?: string;
    is_subscription_active?: boolean;
    account_limit?: number;
    remaining_accounts?: number;
    created_accounts_count?: number;
    is_deleted?: boolean;
    deleted_at?: string;
    deleted_by_email?: string;
}

/** ユーザー更新データ */
export interface UpdateUserData {
    name: string;
    email: string;
    is_admin?: boolean;
    subscription_start: string;
    subscription_end: string;
    password?: string;
}

/** アカウント制限更新データ */
export interface UpdateAccountLimitData {
    account_limit: number;
}

/** 日付バリデーションエラー */
export interface DateError {
    startDate?: string;
    endDate?: string;
}
