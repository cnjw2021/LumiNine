"""수비술 특성(traits) 데이터 로더.

numerology_traits.json 에서 Life Path Number 별 title / traits 텍스트를 제공.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_TRAITS_FILE = _DATA_DIR / "numerology_traits.json"


@lru_cache(maxsize=1)
def _load_traits() -> Dict[str, Any]:
    """JSON 파일을 1회만 로드하고 캐싱."""
    with _TRAITS_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def get_numerology_traits(life_path_number: int) -> Optional[Dict[str, str]]:
    """Life Path Number 에 해당하는 title + traits 반환.

    Args:
        life_path_number: 1~9 또는 11/22/33

    Returns:
        ``{"title": "リーダー", "traits": "..."}`` 또는 ``None``
    """
    data = _load_traits()
    entry = data.get(str(life_path_number))
    if entry is None:
        return None
    return {
        "title": entry.get("title", ""),
        "traits": entry.get("traits", ""),
    }
