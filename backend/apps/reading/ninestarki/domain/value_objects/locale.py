"""Locale Enum — 지원 언어 정의.

기본 언어: ja (일본어).
"""
from __future__ import annotations

from enum import Enum


class Locale(str, Enum):
    """지원 언어 코드."""

    JA = "ja"
    KO = "ko"
    EN = "en"
