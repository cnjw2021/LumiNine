"""StarAttributeService - 星の属性データを取得するサービス"""

from core.models.star_attribute import StarAttribute
from core.utils.logger import get_logger

logger = get_logger(__name__)

class StarAttributeService:
    """星の属性データを取り扱うサービスクラス"""
    
    @staticmethod
    def get_star_attributes(star_number):
        """特定の星番号に関連する属性情報を取得し、タイプ別にグループ化する
        
        Args:
            star_number (int): 星番号（1-9）
            
        Returns:
            dict: タイプ別にグループ化された属性情報
        """
        logger.debug(f"Getting star attributes for star_number: {star_number}")
        
        # 属性データをデータベースから取得
        attributes = StarAttribute.query.filter_by(star_number=star_number).all()
        
        # 属性をタイプ別にグループ化
        grouped_attributes = {}
        for attr in attributes:
            if attr.attribute_type not in grouped_attributes:
                grouped_attributes[attr.attribute_type] = []
            
            grouped_attributes[attr.attribute_type].append({
                "attribute_value": attr.attribute_value,
                "description": attr.description
            })
        
        logger.debug(f"Found {len(attributes)} attributes in {len(grouped_attributes)} groups")
        return grouped_attributes
    
    @staticmethod
    def get_star_attributes_list(star_number):
        """特定の星番号に関連する属性情報をリスト形式で取得する
        
        Args:
            star_number (int): 星番号（1-9）
            
        Returns:
            list: 属性情報のリスト
        """
        logger.debug(f"Getting star attributes list for star_number: {star_number}")
        
        # 属性データをデータベースから取得
        attributes = StarAttribute.query.filter_by(star_number=star_number).all()
        
        # 結果を辞書形式に変換
        result = [attr.to_dict() for attr in attributes]
        
        logger.debug(f"Found {len(result)} attributes")
        return result 