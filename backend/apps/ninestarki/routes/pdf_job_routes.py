import os
import uuid
from flask import Blueprint, jsonify, request, send_file
from rq.job import Job
from datetime import datetime

from core.task_queue import pdf_queue, redis_conn
from core.utils.logger import get_logger
from apps.ninestarki.use_cases.dto.report_dtos import ReportInputDTO
from apps.ninestarki.use_cases.dto.validators import validate_report_input
from core.exceptions import AppError, ValidationError

logger = get_logger(__name__)

def create_pdf_jobs_bp(generate_report_use_case):
    """
    PDF 생성 비동기 작업을 위한 Blueprint를 생성합니다.
    """
    pdf_jobs_bp = Blueprint('pdf_jobs', __name__, url_prefix='/api/pdf-jobs')
    
    TMP_DIR = '/tmp/pdf'
    # os.makedirs(TMP_DIR, exist_ok=True) # 워커가 생성하므로 여기서 필요 없을 수 있음

    # 공통 에러 핸들러 등록
    @pdf_jobs_bp.errorhandler(AppError)
    def handle_app_error(e: AppError):
        request_id = request.headers.get('X-Request-ID') or 'n/a'
        return jsonify({"error": e.to_dict(), "request_id": request_id}), e.status

    @pdf_jobs_bp.route('', methods=['POST'])
    def create_job():
        """
        PDF 생성 작업을 RQ(Redis Queue)에 등록합니다.
        - 요청 스키마를 표준 report_data로 정규화 및 검증 후 큐에 등록합니다.
        """
        try:
            # 표준 요청 식별자 생성 (헤더 우선, 없으면 UUID)
            request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())

            payload = request.get_json()
            if not payload:
                logger.warning(f"create_job | request_id={request_id} | empty payload")
                raise ValidationError("Request payload is empty")
            
            rd = payload.get("resultData", {})
            if not isinstance(rd, dict):
                logger.warning(f"create_job | request_id={request_id} | invalid resultData type")
                raise ValidationError("resultData must be an object")

            # 최소 필수 필드 추출 (Clean Arch: 서버 재계산)
            full_name = rd.get("fullName")
            birthdate_raw = rd.get("birthdate")
            gender = rd.get("gender")
            target_year = rd.get("targetYear") or datetime.now().year
            template_id = payload.get("templateId", 1)
            background_id = payload.get("backgroundId", 1)
            use_simple = payload.get("useSimple", False)
            compatibility = rd.get("compatibility")

            # optional partner info (相手鑑定): allow either resultData.partner or compatibility.input.partner
            partner_raw = rd.get("partner")
            if not partner_raw and isinstance(compatibility, dict):
                partner_raw = (compatibility.get("input") or {}).get("partner")

            partner_norm = None
            if isinstance(partner_raw, dict):
                p_name = partner_raw.get("fullName") or partner_raw.get("full_name")
                p_birth = partner_raw.get("birthdate") or partner_raw.get("birth_date")
                p_gender = partner_raw.get("gender")
                # normalize birthdate if possible
                if p_name and p_birth and p_gender:
                    try:
                        for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
                            try:
                                p_birth_norm = datetime.strptime(p_birth, fmt).strftime("%Y-%m-%d")
                                break
                            except Exception:
                                p_birth_norm = None
                        if p_birth_norm:
                            partner_norm = {
                                "full_name": p_name,
                                "birthdate": p_birth_norm,
                                "gender": p_gender,
                            }
                    except Exception:
                        partner_norm = None

            # 필수 키 검증
            missing = []
            if full_name is None: missing.append("resultData.fullName")
            if birthdate_raw is None: missing.append("resultData.birthdate")
            if gender is None: missing.append("resultData.gender")
            if missing:
                logger.warning(f"create_job | request_id={request_id} | missing={missing}")
                raise ValidationError("Missing required fields", fields=missing)

            # birthdate 정규화 (YYYY-MM-DD or YYYY/MM/DD 허용)
            bd_norm = None
            if isinstance(birthdate_raw, str):
                for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
                    try:
                        bd_norm = datetime.strptime(birthdate_raw, fmt).strftime("%Y-%m-%d")
                        break
                    except Exception:
                        continue
            if bd_norm is None:
                logger.warning(f"create_job | request_id={request_id} | invalid birthdate format: {birthdate_raw}")
                raise ValidationError("Invalid birthdate format", fields=["birthdate(format)"])

            # target_year 정수화
            if not isinstance(target_year, int):
                try:
                    target_year = int(target_year)
                except Exception:
                    logger.warning(f"create_job | request_id={request_id} | invalid targetYear type: {target_year}")
                    raise ValidationError("targetYear must be integer", fields=["target_year(type)"])

            # 표준 report_data 구성 (result_data는 서버에서 재계산)
            report_data: ReportInputDTO = {
                'full_name': full_name,
                'birthdate': bd_norm,
                'gender': gender,
                'target_year': target_year,
                'template_id': template_id,
                'background_id': background_id,
                'use_simple': bool(use_simple),
            }

            if partner_norm:
                report_data['partner'] = partner_norm

            logger.info(f"create_job | request_id={request_id} | enqueue | full_name={full_name} | target_year={target_year}")

            # 파일 저장을 위해 고유 ID를 미리 생성합니다.
            job_id = str(uuid.uuid4())

            # 작업 함수를 직접 import하여 전달
            # from apps.ninestarki.tasks import generate_pdf_task # 직접 import

            is_valid, issues = validate_report_input(report_data)
            if not is_valid:
                logger.warning(f"create_job | request_id={request_id} | dto validation failed | issues={issues}")
                raise ValidationError("Invalid or missing fields", fields=issues)

            # 함수 객체 직접 import 대신 문자열 경로로 enqueue하여 순환 참조 위험을 줄임
            job = pdf_queue.enqueue('apps.ninestarki.tasks.generate_pdf_task', report_data, job_id)
            
            # 생성된 RQ의 job.id를 반환합니다.
            logger.info(f"create_job | request_id={request_id} | enqueued | job_id={job.id}")
            return jsonify({"job_id": job.id, "request_id": request_id}), 202

        except AppError as e:
            # AppError는 공통 핸들러로 위임되지만, 로깅도 남김
            logger.warning(f"create_job | request_id={request_id} | app_error: {e.code} {e}")
            raise
        except Exception as e:
            request_id = locals().get('request_id', 'n/a')
            logger.error(f"create_job | request_id={request_id} | error: {e}", exc_info=True)
            return jsonify({
                "error": {"code": "INTERNAL_ERROR", "message": "작업 생성 중 오류가 발생했습니다.", "details": str(e)},
                "request_id": request_id
            }), 500

    @pdf_jobs_bp.route('/<job_id>', methods=['GET'])
    def get_job_status(job_id):
        """등록된 작업의 상태를 확인합니다."""
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            status = job.get_status()
            
            if status == 'finished':
                return jsonify({'status': 'finished', 'download_url': f'/api/pdf-jobs/{job_id}/download'})
            elif status == 'failed':
                return jsonify({'status': 'failed', 'error': job.exc_info}), 500
            
            return jsonify({'status': status}), 200 # 'queued', 'started' 등
        except Exception:
            return jsonify({'status': 'not_found'}), 404

    @pdf_jobs_bp.route('/<job_id>/download', methods=['GET'])
    def download_pdf(job_id):
        """완료된 PDF 파일을 다운로드합니다."""
        file_path = os.path.join(TMP_DIR, f'{job_id}.pdf')
        if not os.path.exists(file_path):
            return jsonify({'error': '파일이 준비되지 않았거나 만료되었습니다.'}), 404
        
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=f'ninestarki_report_{job_id}.pdf', 
            mimetype='application/pdf'
        )

    return pdf_jobs_bp