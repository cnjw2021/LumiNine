/**
 * api.ts のレスポンスインターセプターが加工したエラーから
 * 人間が読めるメッセージを抽出するユーティリティ。
 *
 * インターセプターは Axios エラーを spread するため、
 * 非列挙プロパティ (message, stack 等) が失われ、
 * console.error に渡すと `{}` と表示される問題を解決する。
 */
export function extractErrorMessage(err: unknown, fallback: string): string {
    if (err == null) return fallback;

    // interceptor が付与する details オブジェクト
    const details = (err as Record<string, unknown>).details as
        | { message?: string; status?: number; statusText?: string; data?: unknown }
        | undefined;

    if (details) {
        // details.data に backend エラーメッセージがある場合
        if (details.data && typeof details.data === 'object') {
            const data = details.data as Record<string, unknown>;
            // {error: "message"} 形式
            if (typeof data.error === 'string') return data.error;
            // {error: {message: "..."}} 形式 (AppError ハンドラ)
            if (data.error && typeof data.error === 'object' && 'message' in (data.error as object)) {
                return String((data.error as Record<string, unknown>).message);
            }
            // {message: "..."} 形式 (NineStarKiError.to_dict())
            if (typeof data.message === 'string') return data.message;
        }
        if (details.message) return details.message;
        if (details.status) return `HTTP ${details.status}${details.statusText ? ` ${details.statusText}` : ''}`;
    }

    // 401 ハンドラが返すプレーンオブジェクト
    const response = (err as Record<string, unknown>).response as
        | { status?: number; data?: { message?: string; error?: string } }
        | undefined;
    if (response?.data?.error) return response.data.error;
    if (response?.data?.message) return response.data.message;
    if (response?.status === 401) return '認証が必要です。ログインしてください。';

    // 標準 Error オブジェクト
    if (err instanceof Error) return err.message;

    // 文字列がそのまま throw された場合
    if (typeof err === 'string') return err;

    return fallback;
}
