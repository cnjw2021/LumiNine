import traceback
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from core.database import db
from core.models.compatibility_master import CompatibilityMaster
from core.models.compatibility_readings_master import CompatibilityReadingsMaster
from core.models.compatibility_symbol_pattern_master import CompatibilitySymbolPatternMaster
from core.utils.logger import get_logger

logger = get_logger(__name__)

class CompatibilityService:
    """九星気学の相性鑑定サービス"""
    
    @staticmethod
    def get_compatibility_symbols(main_star: int, target_star: int, 
                                  main_birth_month: int, 
                                  target_birth_month: int,
                                  is_male: bool = True) -> str:
        """
        主星と対象星の本命星と生年月から相性記号を取得する
        
        Args:
            main_star: 主星の本命星番号
            target_star: 対象星の本命星番号
            main_birth_month: 主星の持ち主の生まれ月
            target_birth_month: 対象星の持ち主の生まれ月
            is_male: 主星の持ち主が男性かどうか (男性視点: True, 女性視点: False)
            
        Returns:
            相性記号 (★,○,P,F,N,▲ など)
        """
        try:
            return CompatibilityMaster.get_compatibility_symbols(
                main_star, target_star, main_birth_month, target_birth_month, is_male
            )
        except Exception as e:
            logger.error(f"相性記号取得中にエラーが発生しました: {str(e)}")
            logger.error(traceback.format_exc())
            return ""
    
    @staticmethod
    def get_pattern_code(symbols: str) -> Optional[str]:
        """
        相性記号からパターンコードを取得する
        
        Args:
            symbols: 相性記号
            
        Returns:
            パターンコード (PATTERN_1 など) または None
        """
        try:
            pattern = CompatibilitySymbolPatternMaster.query.filter_by(symbols=symbols).first()
            return pattern.pattern_code if pattern else None
        except Exception as e:
            logger.error(f"パターンコード取得中にエラーが発生しました: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def get_compatibility_readings(pattern_code: str) -> Optional[Dict]:
        """
        パターンコードから相性鑑定文をテーマごとに取得する
        
        Args:
            pattern_code: パターンコード (PATTERN_1 など)
            
        Returns:
            テーマごとの相性鑑定文の辞書データ または None
        """
        try:
            # テーマリストをCSVデータの実際のテーマに合わせる
            themes = ['general', 'relationship', 'business', 'friendship', 'family']
            readings = {}
            
            # 各テーマの鑑定文を取得
            for theme in themes:
                reading = CompatibilityReadingsMaster.query.filter_by(
                    pattern_code=pattern_code,
                    theme=theme
                ).first()
                
                if reading:
                    readings[theme] = reading.to_dict()
            
            return readings if readings else None
        except Exception as e:
            logger.error(f"相性鑑定文取得中にエラーが発生しました: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    @classmethod
    def get_compatibility(cls, main_star: int, target_star: int, 
                         main_birth_month: int, 
                         target_birth_month: int,
                         is_male: bool = True) -> Dict:
        """
        主星と対象星の本命星と生年月から相性鑑定結果を取得する
        
        Args:
            main_star: 主星の本命星番号
            target_star: 対象星の本命星番号
            main_birth_month: 主星の持ち主の生まれ月
            target_birth_month: 対象星の持ち主の生まれ月
            is_male: 主星の持ち主が男性かどうか (男性視点: True, 女性視点: False)
            
        Returns:
            相性鑑定結果の辞書データ
        """
        result = {
            "main_star": main_star,
            "target_star": target_star,
            "main_birth_month": main_birth_month,
            "target_birth_month": target_birth_month,
            "is_male": is_male,
            "symbols": "",
            "pattern_code": "",
            "readings": {}
        }
        
        try:
            # 相性記号を取得
            symbols = cls.get_compatibility_symbols(
                main_star, target_star, main_birth_month, target_birth_month, is_male
            )
            result["symbols"] = symbols
            
            if not symbols:
                logger.warning(f"相性記号が取得できませんでした: main_star={main_star}, target_star={target_star}")
                return result
            
            # パターンコードを取得
            pattern_code = cls.get_pattern_code(symbols)
            result["pattern_code"] = pattern_code or ""
            
            if not pattern_code:
                logger.warning(f"パターンコードが取得できませんでした: symbols={symbols}")
                return result
            
            # テーマごとの相性鑑定文を取得
            readings = cls.get_compatibility_readings(pattern_code)
            result["readings"] = readings or {}
            
            return result
            
        except Exception as e:
            logger.error(f"相性鑑定中にエラーが発生しました: {str(e)}")
            logger.error(traceback.format_exc())
            return result 