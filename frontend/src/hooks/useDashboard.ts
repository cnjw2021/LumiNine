'use client';

import { useState, useEffect, useCallback } from 'react';
import api from '@/utils/api';
import {
    MyDashboardSummary,
    MyHistoryResponse,
    MyChartResponse,
    AdminDashboardSummary,
    AdminChartData,
    AdminUsersResponse,
    AggregationInterval,
} from '@/types/dashboard';

// ── 일반 사용자 대시보드 훅 ─────────────────────────────

/** 개인 요약 통계 조회 */
export function useMyDashboardSummary() {
    const [summary, setSummary] = useState<MyDashboardSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                const { data } = await api.get<MyDashboardSummary>('/dashboard/my/summary');
                if (!cancelled) setSummary(data);
            } catch (e: unknown) {
                if (!cancelled) setError('サマリーデータを読み込めませんでした。');
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => { cancelled = true; };
    }, []);

    return { summary, loading, error };
}

/** 개인 이력 조회 (페이징) */
export function useMyDashboardHistory(page: number, perPage: number) {
    const [history, setHistory] = useState<MyHistoryResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            setLoading(true);
            setError(null);
            try {
                const { data } = await api.get<MyHistoryResponse>('/dashboard/my/history', {
                    params: { page, per_page: perPage },
                });
                if (!cancelled) setHistory(data);
            } catch (e: unknown) {
                if (!cancelled) setError('履歴データを読み込めませんでした。');
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => { cancelled = true; };
    }, [page, perPage]);

    return { history, loading, error };
}

/** 개인 미니 차트 조회 */
export function useMyDashboardChart() {
    const [chartData, setChartData] = useState<MyChartResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                const { data } = await api.get<MyChartResponse>('/dashboard/my/chart');
                if (!cancelled) setChartData(data);
            } catch (e: unknown) {
                if (!cancelled) setError('チャートデータを読み込めませんでした。');
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => { cancelled = true; };
    }, []);

    return { chartData, loading, error };
}

// ── Superuser 대시보드 훅 ───────────────────────────────

/** 관리자 전체 요약 조회 */
export function useAdminDashboardSummary() {
    const [summary, setSummary] = useState<AdminDashboardSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                const { data } = await api.get<AdminDashboardSummary>(
                    '/admin/dashboard/summary',
                );
                if (!cancelled) setSummary(data);
            } catch (e: unknown) {
                if (!cancelled) setError('管理者サマリーを読み込めませんでした。');
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => { cancelled = true; };
    }, []);

    return { summary, loading, error };
}

/** 관리자 차트 데이터 조회 */
export function useAdminDashboardChart(
    start: string | null,
    end: string | null,
    interval: AggregationInterval,
) {
    const [chartData, setChartData] = useState<AdminChartData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            setLoading(true);
            setError(null);
            try {
                const params: Record<string, string> = { interval };
                if (start) params.start = start;
                if (end) params.end = end;

                const { data } = await api.get<AdminChartData>(
                    '/admin/dashboard/chart',
                    { params },
                );
                if (!cancelled) setChartData(data);
            } catch (e: unknown) {
                if (!cancelled) setError('チャートデータを読み込めませんでした。');
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => { cancelled = true; };
    }, [start, end, interval]);

    return { chartData, loading, error };
}

/** 관리자 사용자별 집계 리스트 조회 */
export function useAdminDashboardUsers(
    page: number,
    perPage: number,
    sort: string,
    order: string,
    search: string,
) {
    const [data, setData] = useState<AdminUsersResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            setLoading(true);
            setError(null);
            try {
                const { data: resp } = await api.get<AdminUsersResponse>(
                    '/admin/dashboard/users',
                    { params: { page, per_page: perPage, sort, order, search: search || undefined } },
                );
                if (!cancelled) setData(resp);
            } catch (e: unknown) {
                if (!cancelled) setError('ユーザー一覧を読み込めませんでした。');
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => { cancelled = true; };
    }, [page, perPage, sort, order, search]);

    return { data, loading, error };
}

// ── PDF 이벤트 기록 ─────────────────────────────────────

/** PDF 다운로드 이벤트를 백엔드에 기록 (fire-and-forget) */
export async function recordPdfDownload(
    targetName?: string,
    targetYear?: number,
    targetMonth?: number,
): Promise<void> {
    try {
        await api.post('/events/pdf-download', {
            target_name: targetName,
            target_year: targetYear,
            target_month: targetMonth,
        });
    } catch {
        // 이벤트 기록 실패는 사용자 경험에 영향을 주지 않으므로 무시
        console.warn('[Dashboard] PDF 다운로드 이벤트 기록 실패');
    }
}
