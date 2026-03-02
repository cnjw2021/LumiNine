"""PDF生成のインターフェース定義"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class PdfGeneratorInterface(ABC):
    """PDF生成のインターフェース"""
    
    @abstractmethod
    def generate(self, report_data: Dict[str, Any]) -> bytes:
        """Nine Star KiレポートデータからPDFを生成する
        
        Args:
            report_data (Dict[str, Any]): レポートデータ
            
        Returns:
            bytes: 生成されたPDFのバイトデータ
        """
        pass
