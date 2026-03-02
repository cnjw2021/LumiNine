"""WeasyPrintを使用したNine Star Ki PDF生成器の実装"""

import io
import os
from typing import Dict, Any, Optional
from flask import has_app_context
import weasyprint
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from apps.ninestarki.use_cases.interfaces.pdf_generator_interface import PdfGeneratorInterface
from apps.ninestarki.infrastructure.pdf.ninestarki_html_renderer import NineStarKiHtmlRenderer
from apps.ninestarki.infrastructure.pdf.pdf_styling_service import PdfStylingService
from core.utils.logger import get_logger

logger = get_logger(__name__)

class WeasyPrintPdfGenerator(PdfGeneratorInterface):
    """WeasyPrintライブラリを使用したNine Star Ki PDF生成器の実装"""
    
    def __init__(self, base_dir: str):
        self.html_renderer = NineStarKiHtmlRenderer(base_dir=base_dir)
        self.styling_service = PdfStylingService(base_dir=base_dir)
    
    def generate(self, report_data: Dict[str, Any]) -> bytes:
        """Nine Star KiレポートデータからPDFを生成する
        
        Args:
            report_data (Dict[str, Any]): レポートデータ(= UseCaseで構築されたcontext)
            
        Returns:
            bytes: 生成されたPDFのバイトデータ
        """
        # アプリケーションコンテキストはエントリポイント側（Webリクエスト/ワーカー）で管理する
        try:
            if not has_app_context():
                logger.warning("Flaskアプリケーションコンテキストが存在しません。レンダリングで失敗する可能性があります。")
            logger.debug("Nine Star Ki PDF生成開始")
            logger.debug(f"受信したcontext: {report_data}")
            
            # RQジョブIDを取得
            job_id = self._get_job_id()
            logger.info(f"Job ID: {job_id}")
            
            # PDF用にSVG互換モードを有効化してレンダリング
            pdf_context = dict(report_data)
            pdf_context["use_pdf_svg"] = True
            html_content = self._render_ninestarki_html(pdf_context)
            
            pdf_bytes = self._generate_pdf_from_html(html_content)
            
            # RQジョブの場合ファイル保存
            if job_id:
                logger.info(f"RQ Job ID detected: {job_id} - saving PDF file")
                self._save_pdf_file(pdf_bytes, job_id)
            else:
                logger.info("No RQ Job ID detected - PDF file will not be saved")
            
            logger.debug("Nine Star Ki PDF生成完了")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Nine Star Ki PDF生成中にエラーが発生しました: {str(e)}")
            raise
    
    def _render_ninestarki_html(self, context: Dict[str, Any]) -> str:
        """Nine Star KiデータをHTMLにレンダリングする
        
        Args:
            context (Dict[str, Any]): UseCaseで構築されたコンテキスト
            
        Returns:
            str: レンダリングされたHTML
        """
        try:
            # HTMLレンダラーを使用してHTMLを生成
            html_content = self.html_renderer.render(context)
            return html_content
            
        except Exception as e:
            logger.error(f"HTMLレンダリング中にエラーが発生しました: {str(e)}")
            logger.error(f"context: {context}")
            raise
    
    def _generate_pdf_from_html(self, html_content: str) -> bytes:
        """HTMLコンテンツからPDFを生成する
        
        Args:
            html_content (str): HTMLコンテンツ
            
        Returns:
            bytes: 生成されたPDFのバイトデータ
        """
        try:
            logger.info("WeasyPrintを使用したPDF生成開始")
            
            # フォント設定
            font_config = FontConfiguration()
            
            # 基本CSSスタイルを適用
            css_base = self.styling_service.get_base_css_string()
            
            # WeasyPrintでPDFを生成
            document = HTML(string=html_content)
            
            # CSSスタイルシートを作成
            css_stylesheet = weasyprint.CSS(string=css_base)
            
            pdf_bytes = document.write_pdf(
                stylesheets=[css_stylesheet],
                font_config=font_config
            )
            
            logger.info("WeasyPrintを使用したPDF生成完了")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"WeasyPrintを使用したPDF生成中にエラーが発生しました: {str(e)}")
            raise
    
    def _get_job_id(self) -> Optional[str]:
        """RQジョブIDを取得する"""
        try:
            from rq import get_current_job
            current_job = get_current_job()
            return current_job.id if current_job else None
        except Exception:
            return None
    
    def _save_pdf_file(self, pdf_bytes: bytes, job_id: str) -> None:
        """PDFファイルを保存する"""
        try:
            out_dir = '/tmp/pdf'
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{job_id}.pdf")
            
            # ファイルサイズをログに出力
            logger.info(f"PDF生成完了 - サイズ: {len(pdf_bytes)} bytes")
            
            # ファイル書き込み
            with open(out_path, 'wb') as f:
                f.write(pdf_bytes)
            
            # 実際に保存されたかチェック
            if os.path.exists(out_path):
                file_size = os.path.getsize(out_path)
                logger.info(f"PDF file saved successfully: {out_path} (size: {file_size} bytes)")
            else:
                logger.error(f"PDF file was not saved: {out_path}")
                raise Exception(f"PDF file was not saved: {out_path}")
            
        except Exception as e:
            logger.error(f"PDFファイル保存中にエラーが発生しました: {str(e)}")
            logger.error(f"Job ID: {job_id}, PDF bytes length: {len(pdf_bytes) if pdf_bytes else 'None'}")
            raise
