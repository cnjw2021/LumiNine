from typing import Any


def format_zodiac(value: Any) -> str:
    """干支の表示フォーマットを統一（そのまま文字列化、将来の置換余地を確保）"""
    return '' if value is None else str(value)


