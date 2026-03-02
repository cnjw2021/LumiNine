import pytest
import requests
import json
import os

# API 서버의 기본 URL
BASE_URL = "http://backend:5001"
YEAR = 2025

def load_golden_master_data(file_path: str) -> dict:
    """
    '정답' JSON 파일을 로드하는 함수
    (예: "test_daily_star_reading/case_19670303.json")
    """
    if not file_path:
        raise ValueError("file_path is required")
    
    # 이 테스트 파일의 위치를 기준으로 golden_master 디렉토리의 절대 경로를 찾습니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir + "/test_daily_star_reading/", file_path)
    
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@pytest.mark.parametrize("input_params, golden_master_file", [
    ({"birth_date": "1967-03-03"}, "case_19670303.json"),
    ({"birth_date": "1971-03-22"}, "case_19710322.json"),
    ({"birth_date": "1972-09-24"}, "case_19720924.json"),
    ({"birth_date": "1984-10-14"}, "case_19841014.json"),
])
def test_daily_star_reading(input_params, golden_master_file):
    """
    /api/nine-star/daily-star-reading 엔드포인트가
    저장된 '정답'과 동일한 결과를 반환하는지 검증합니다.
    """
    # 1. '정답' 데이터를 로드합니다.
    golden_master = load_golden_master_data(golden_master_file)

    # 2. 실제 API에 GET 요청을 보냅니다.
    response = requests.get(
        f"{BASE_URL}/api/nine-star/daily-star-reading",
        params=input_params
    )
    
    # 3. 응답을 검증합니다.
    # HTTP 상태 코드가 200 (성공)인지 확인
    assert response.status_code == 200
    
    # 실제 응답 데이터를 JSON으로 파싱
    actual_response = response.json()
    
    # '정답' 데이터와 실제 응답 데이터가 정확히 일치하는지 확인
    assert actual_response == golden_master, "API 응답이 저장된 정답과 다릅니다!"