from datetime import datetime, timedelta
from typing import Optional, Tuple


def format_period_range(start_iso: Optional[str], end_iso: Optional[str]) -> Tuple[str, str, str]:
    """
    ISO(YYYY-MM-DD)の開始/終了を受け取り、
    - (YYYY年MM月DD日, YYYY年MM月DD日, (M/D ~ M/D)) を返却
    空値は空文字で返す。
    """
    def _fmt(s: Optional[str]) -> str:
        if not s:
            return ''
        try:
            return datetime.strptime(s, '%Y-%m-%d').strftime('%Y年%m月%d日')
        except Exception:
            return ''

    def _fmt_md(s: Optional[str]) -> str:
        if not s:
            return ''
        try:
            dt = datetime.strptime(s, '%Y-%m-%d')
            return dt.strftime('%-m/%-d') if hasattr(dt, 'strftime') else ''
        except Exception:
            return ''

    start_jp = _fmt(start_iso)
    end_jp = _fmt(end_iso)
    md = f"({_fmt_md(start_iso)} ~ {_fmt_md(end_iso)})" if start_iso and end_iso else ''
    return start_jp, end_jp, md


