"""MessageCatalog 단위 테스트.

커버리지:
  - ja/ko/en 각 locale에서 올바른 문자열 반환
  - 미지원 locale → ja fallback
  - params 플레이스홀더 치환 ({direction} → "南")
  - 키 미존재 시 키 자체 반환
"""
from __future__ import annotations

import pytest

from apps.ninestarki.infrastructure.services.message_catalog import MessageCatalog


@pytest.fixture
def catalog() -> MessageCatalog:
    return MessageCatalog()


# ══════════════════════════════════════════════════════
# 기본 locale 조회
# ══════════════════════════════════════════════════════

class TestBasicResolve:
    def test_ja_layer_base(self, catalog: MessageCatalog):
        assert catalog.resolve("layer.base", "ja") == "基本石"

    def test_ko_layer_base(self, catalog: MessageCatalog):
        assert catalog.resolve("layer.base", "ko") == "기본석"

    def test_en_layer_base(self, catalog: MessageCatalog):
        assert catalog.resolve("layer.base", "en") == "Base Stone"

    def test_ja_direction(self, catalog: MessageCatalog):
        assert catalog.resolve("direction.south", "ja") == "南"

    def test_ko_direction(self, catalog: MessageCatalog):
        assert catalog.resolve("direction.south", "ko") == "남"

    def test_en_direction(self, catalog: MessageCatalog):
        assert catalog.resolve("direction.south", "en") == "South"

    def test_ja_threat(self, catalog: MessageCatalog):
        assert catalog.resolve("threat.five_yellow", "ja") == "五黄殺"

    def test_ko_threat(self, catalog: MessageCatalog):
        assert catalog.resolve("threat.five_yellow", "ko") == "오황살"

    def test_en_threat(self, catalog: MessageCatalog):
        assert catalog.resolve("threat.five_yellow", "en") == "Five Yellow"

    def test_ja_gogyo(self, catalog: MessageCatalog):
        assert catalog.resolve("gogyo.木", "ja") == "木"

    def test_ko_gogyo(self, catalog: MessageCatalog):
        assert catalog.resolve("gogyo.火", "ko") == "화"

    def test_en_gogyo(self, catalog: MessageCatalog):
        assert catalog.resolve("gogyo.水", "en") == "Water"


# ══════════════════════════════════════════════════════
# Fallback
# ══════════════════════════════════════════════════════

class TestFallback:
    def test_unsupported_locale_falls_back_to_ja(self, catalog: MessageCatalog):
        """미지원 locale → ja fallback."""
        result = catalog.resolve("layer.base", "zh")
        assert result == "基本石"

    def test_default_locale_is_ja(self, catalog: MessageCatalog):
        """locale 미지정 시 ja."""
        result = catalog.resolve("layer.monthly")
        assert result == "月運石"

    def test_missing_key_returns_key(self, catalog: MessageCatalog):
        """미존재 키 → 키 자체 반환."""
        result = catalog.resolve("nonexistent.key", "ja")
        assert result == "nonexistent.key"


# ══════════════════════════════════════════════════════
# 플레이스홀더 치환
# ══════════════════════════════════════════════════════

class TestPlaceholderSubstitution:
    def test_reason_monthly_ja(self, catalog: MessageCatalog):
        result = catalog.resolve(
            "reason.monthly", "ja",
            params={"direction": "南", "element": "火"},
        )
        assert result == "今月の最良吉方位・南(火)のエネルギーを取り込む石"

    def test_reason_monthly_ko(self, catalog: MessageCatalog):
        result = catalog.resolve(
            "reason.monthly", "ko",
            params={"direction": "남", "element": "화"},
        )
        assert result == "이달 최적 길방위 남(화)의 에너지를 받는 돌"

    def test_reason_monthly_en(self, catalog: MessageCatalog):
        result = catalog.resolve(
            "reason.monthly", "en",
            params={"direction": "South", "element": "Fire"},
        )
        assert result == "Captures energy from the best auspicious direction South(Fire) this month"

    def test_reason_protection_ja(self, catalog: MessageCatalog):
        result = catalog.resolve(
            "reason.protection", "ja",
            params={
                "threat": "五黄殺",
                "direction": "南",
                "threat_element": "火",
                "counter_element": "水",
            },
        )
        assert "五黄殺" in result
        assert "南" in result
        assert "水" in result

    def test_partial_params_leaves_remaining_placeholders(self, catalog: MessageCatalog):
        """일부 params 만 제공하면 나머지 플레이스홀더는 그대로 남는다."""
        result = catalog.resolve(
            "reason.monthly", "ja",
            params={"direction": "南"},
        )
        assert "南" in result
        assert "{element}" in result

    def test_no_params(self, catalog: MessageCatalog):
        """params=None 이면 치환 없이 원본 반환."""
        result = catalog.resolve("reason.monthly", "ja")
        assert "{direction}" in result
        assert "{element}" in result
