"""IMessageCatalog — i18n 메시지 해석 인터페이스.

i18n 렌더링은 표현 계층 성격이므로 use_cases/interfaces/ 에 배치
(기존 pdf_generator_interface.py 등과 동일, infrastructure/readme.txt 원칙 준수).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional


class IMessageCatalog(ABC):
    """다국어 메시지 해석 인터페이스.

    이 인터페이스를 통해 도메인 reason_key → 번역된 문자열로 변환한다.
    """

    @abstractmethod
    def resolve(
        self,
        key: str,
        locale: str = "ja",
        params: Optional[Dict[str, str]] = None,
    ) -> str:
        """메시지 키 + locale → 번역된 문자열 반환.

        Args:
            key: 메시지 키 (예: "reason.monthly", "direction.south")
            locale: 언어 코드 (기본값: "ja")
            params: 플레이스홀더 치환 딕셔너리 (예: {"direction": "南"})

        Returns:
            치환 완료된 번역 문자열. 키가 없으면 키 자체를 반환.
        """
