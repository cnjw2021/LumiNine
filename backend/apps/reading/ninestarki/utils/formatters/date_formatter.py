from datetime import date, datetime
from typing import Any


def format_date_ja(value: Any) -> str:
    """YYYY-MM-DD もしくは date を 'YYYY年MM月DD日' に整形"""
    if value is None:
        return ''
    if isinstance(value, date):
        return value.strftime('%Y年%m月%d日')
    try:
        return datetime.strptime(str(value), '%Y-%m-%d').strftime('%Y年%m月%d日')
    except Exception:
        return ''


def now_string_ja() -> str:
    return datetime.now().strftime('%Y年%m月%d日')


