/**
 * ReadingForm 定数定義
 *
 * SSoT: フォーム関連の全定数を一元管理
 */

/** ローカルストレージキー */
export const STORAGE_KEY = 'luminine-result-data';

/** フォーカス遅延 (ms) */
export const FOCUS_DELAY_MS = 100;

/** エラーメッセージ自動消去遅延 (ms) */
export const ERROR_TIMEOUT_MS = 3000;

/** ISO日時生成時のデフォルト時刻 */
export const DEFAULT_BIRTH_TIME = '12:00';

/** 鑑定年 (targetYear) の最小値 */
export const MIN_TARGET_YEAR = 1900;

/** スーパーユーザーの最大鑑定年 */
export const MAX_YEAR_SUPERUSER = 2100;

/**
 * 一般ユーザーの鑑定年入力上限 (NumberInput の max 制約用ガード値)
 * 実際の鑑定可能な最大年は useReadingForm 側で currentYear に矯正される
 */
export const MAX_YEAR_NORMAL = 3000;
