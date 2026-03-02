import os

from injector import Injector
from apps.ninestarki.use_cases.generate_report_use_case import GenerateReportUseCase
from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository
from core.utils.logger import get_logger
from core.config import get_config

logger = get_logger(__name__)

__all__ = ['generate_pdf_task']

def generate_pdf_task(report_data: dict, job_id: str):
    """
    RQ Workerが実際に実行する関数。
    Appの初期化とアプリケーションコンテキストはワーカーエントリポイント側で管理する。
    """
    try:
        logger.info(f"generate_pdf_task | start | job_id={job_id}")

        # 1) DIコンテナからUseCaseを解決
        from apps.ninestarki.dependency_module import AppModule
        injector = Injector([AppModule()])
        use_case = injector.get(GenerateReportUseCase)

        # 2) 最小入力ベースでresult_dataを再計算
        birthdate = report_data.get('birthdate')  # 'YYYY-MM-DD'
        gender = report_data.get('gender')
        target_year = report_data.get('target_year')

        cfg = get_config()
        noon = getattr(cfg, 'DEFAULT_NOON_TIME', '12:00')
        birth_datetime_str = f"{birthdate} {noon}"
        calc_use_case = injector.get(CalculateStarsUseCase)
        calc_result = calc_use_case.execute(birth_datetime_str, gender, target_year)

        # 3) UseCaseに渡すコンテキストを構成
        enriched_report_data = {
            **report_data,
            'result_data': calc_result,
        }

        # 4) PDF生成
        logger.info(f"generate_pdf_task | execute_pdf | job_id={job_id}")
        pdf_bytes = use_case.execute_pdf(enriched_report_data)

        # 5) ファイル保存
        TMP_DIR = '/tmp/pdf'
        os.makedirs(TMP_DIR, exist_ok=True)
        out_path = os.path.join(TMP_DIR, f"{job_id}.pdf")
        with open(out_path, 'wb') as f:
            f.write(pdf_bytes)

        logger.info(f"generate_pdf_task | success | job_id={job_id} | path={out_path}")
        return out_path

    except Exception as e:
        logger.error(f"generate_pdf_task | error | job_id={job_id} | {e}", exc_info=True)
        raise
