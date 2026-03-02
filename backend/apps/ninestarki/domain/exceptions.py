"""九星気学ドメイン固有の例外クラス.

core.exceptions.AppError を基底クラスとし、九星気学ドメインで発生する
計算エラー・データ不足・バリデーション違反を構造的に表現する。

設計方針:
- 既存の ValueError を段階的に置き換え可能にする (ValueError を継承しない)
- AppError.code / AppError.status で API レイヤが HTTP ステータスを一意に判定可能
- ルートハンドラでは AppError を捕捉して JSON エラーレスポンスに変換する
"""
from __future__ import annotations

from typing import Optional

from core.exceptions import AppError


class NineStarKiError(AppError):
    """九星気学ドメインの共通基底例外."""

    def __init__(
        self,
        message: str = "Nine-star calculation error",
        *,
        code: str = "NINESTARKI_ERROR",
        status: int = 500,
        details: Optional[str] = None,
    ):
        super().__init__(message, code=code, status=status, details=details)


class SetsuMonthNotFoundError(NineStarKiError):
    """절기(節氣)데이터가 DB에 존재하지 않아 절월을 결정할 수 없는 경우."""

    def __init__(self, message: str = "절기 데이터를 찾을 수 없습니다.", *, details: Optional[str] = None):
        super().__init__(message, code="SETSU_MONTH_NOT_FOUND", status=422, details=details)


class YearInfoNotFoundError(NineStarKiError):
    """연반(年盤) 정보가 DB에 존재하지 않는 경우."""

    def __init__(self, message: str = "연반 정보를 찾을 수 없습니다.", *, details: Optional[str] = None):
        super().__init__(message, code="YEAR_INFO_NOT_FOUND", status=422, details=details)


class MonthlyBoardCalculationError(NineStarKiError):
    """월반(月盤) 편성 중 발생하는 계산/데이터 오류."""

    def __init__(self, message: str = "월반 편성 오류가 발생했습니다.", *, details: Optional[str] = None):
        super().__init__(message, code="MONTHLY_BOARD_CALC_ERROR", status=500, details=details)
