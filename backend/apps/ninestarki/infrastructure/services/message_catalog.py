"""MessageCatalog — JSON 기반 i18n 메시지 해석 구현체.

SSoT: data/messages/{locale}.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


from apps.ninestarki.use_cases.interfaces.message_catalog_interface import (
    IMessageCatalog,
)


# ── 메시지 파일 경로 ─────────────────────────────────────
_MESSAGES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "messages"

# 지원 locale (기본: ja)
_DEFAULT_LOCALE = "ja"


class MessageCatalog(IMessageCatalog):
    """JSON 기반 다국어 메시지 카탈로그.

    인스턴스 생성 시 모든 locale 파일을 로드하여 메모리에 캐시한다.
    미지원 locale → ja fallback.
    """

    def __init__(self, messages_dir: Path | None = None) -> None:
        base_dir = messages_dir or _MESSAGES_DIR
        self._bundles: Dict[str, Dict[str, str]] = {}

        for json_file in sorted(base_dir.glob("*.json")):
            locale = json_file.stem  # "ja", "ko", "en"
            with open(json_file, encoding="utf-8") as f:
                self._bundles[locale] = json.load(f)

    # ── 공개 메서드 ──────────────────────────────────────

    def resolve(
        self,
        key: str,
        locale: str = "ja",
        params: Optional[Dict[str, str]] = None,
    ) -> str:
        """메시지 키 + locale → 번역된 문자열 반환.

        1. 요청 locale 번들에서 키 조회
        2. 요청 locale 에 메시지가 없고, locale != "ja" 인 경우 ja 번들에서 키 조회 (ja fallback)
        3. 위 조건에 해당하지 않거나, ja fallback 에서도 없으면 키 자체 반환
        4. params 가 있으면 플레이스홀더 치환

        Args:
            key: 메시지 키
            locale: 언어 코드 (기본값: "ja")
            params: 플레이스홀더 치환 딕셔너리

        Returns:
            치환 완료된 번역 문자열
        """
        # locale 번들에서 먼저 조회, 필요 시에만 ja 번들로 fallback
        bundle = self._bundles.get(locale, {})
        template = bundle.get(key)

        if template is None and locale != _DEFAULT_LOCALE:
            # ja fallback 시도
            ja_bundle = self._bundles.get(_DEFAULT_LOCALE, {})
            template = ja_bundle.get(key, key)

        if template is None:
            template = key

        # 플레이스홀더 치환
        if params:
            for placeholder, value in params.items():
                template = template.replace(f"{{{placeholder}}}", value)

        return template
