from injector import inject
from typing import Any, Dict

from core.utils.logger import get_logger
from apps.ninestarki.services.star_attribute_service import StarAttributeService


logger = get_logger(__name__)


class StarAttributeUseCase:
    """
    星属性データ取得ユースケース。
    既存HTTPスキーマの互換性を維持したまま、アプリケーション層からドメインサービスを呼び出します。
    """

    @inject
    def __init__(self, star_attribute_service: StarAttributeService) -> None:
        self._star_attribute_service = star_attribute_service

    def get_star_attributes(self, star_number: int) -> Dict[str, Any]:
        # 既存サービスの出力（一覧形式）をそのまま返す設計だが、
        # テストの期待に合わせてユースケースで責務を集約
        return self._star_attribute_service.get_star_attributes_list(star_number)


