import requests


BASE_URL = "http://backend:5001"


def _get_main_month_stars(birth_datetime: str, target_year: int) -> tuple[int, int]:
    response = requests.post(
        f"{BASE_URL}/api/nine-star/calculate",
        json={"birth_datetime": birth_datetime, "target_year": target_year},
    )
    assert response.status_code == 200
    data = response.json()
    return data["main_star"]["star_number"], data["month_star"]["star_number"]


def test_direction_fortune_inauspicious_directions_for_birthdate_1967_0303_2026():
    """
    1967-03-03生まれの2026年方位運の凶方位が
    north/south のみであることを検証する。
    """
    main_star, month_star = _get_main_month_stars("1967-03-03 00:00", 2026)
    response = requests.get(
        f"{BASE_URL}/api/nine-star/direction-fortune",
        params={"main_star": main_star, "month_star": month_star, "year": 2026},
    )
    assert response.status_code == 200
    data = response.json()
    inauspicious = {direction for direction, status in data.items() if status.get("is_auspicious") is False}
    assert inauspicious == {"north", "south"}
