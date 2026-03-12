/**
 * 대시보드 관련 타입 정의
 */

// ── Superuser 대시보드 ─────────────────────────────────

/** 전체 요약 통계 */
export interface AdminDashboardSummary {
    total_readings: number;
    total_pdfs: number;
    active_users: number;
}

/** 차트 데이터 포인트 */
export interface ChartDataPoint {
    date: string;
    count: number;
}

/** 차트 API 응답 */
export interface AdminChartData {
    readings: ChartDataPoint[];
    pdfs: ChartDataPoint[];
    start: string;
    end: string;
    interval: string;
}

/** 사용자별 통계 행 */
export interface UserStatsRow {
    id: number;
    name: string;
    email: string;
    reading_count: number;
    pdf_count: number;
    last_reading_date: string | null;
}

/** 페이징 메타데이터 */
export interface PaginationMeta {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
}

/** 사용자 목록 API 응답 */
export interface AdminUsersResponse {
    users: UserStatsRow[];
    pagination: PaginationMeta;
}

// ── 일반 사용자 대시보드 ───────────────────────────────

/** 개인 요약 통계 */
export interface MyDashboardSummary {
    reading_count: number;
    pdf_count: number;
    last_reading_date: string | null;
}

/** 감정 이력 아이템 */
export interface ReadingHistoryItem {
    id: number;
    target_year: number;
    target_month: number;
    locale: string;
    created_at: string;
}

/** PDF 다운로드 이력 아이템 */
export interface PdfHistoryItem {
    id: number;
    target_name: string | null;
    target_year: number | null;
    target_month: number | null;
    created_at: string;
}

/** 페이징된 이력 */
export interface PaginatedHistory<T> {
    items: T[];
    total: number;
    page: number;
    per_page: number;
}

/** 개인 이력 API 응답 */
export interface MyHistoryResponse {
    readings: PaginatedHistory<ReadingHistoryItem>;
    pdfs: PaginatedHistory<PdfHistoryItem>;
}

/** 미니 차트 데이터 포인트 */
export interface MiniChartPoint {
    month: string;
    count: number;
}

/** 미니 차트 API 응답 */
export interface MyChartResponse {
    readings: MiniChartPoint[];
}

/** 기간 프리셋 */
export type DateRangePreset = '7d' | '30d' | '90d' | '1y' | 'custom';

/** 차트 유형 */
export type ChartType = 'line' | 'bar';

/** 집계 간격 */
export type AggregationInterval = 'daily' | 'weekly' | 'monthly';
