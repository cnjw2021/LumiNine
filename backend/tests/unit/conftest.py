"""powerstone 테스트 공용 pytest fixture.

상수/팩토리는 powerstone_test_fixtures.py에 집약하고,
이 conftest는 pytest fixture만 노출한다.

Issue #128: Copilot 리뷰 반영 — SUT는 각 테스트 모듈에서 직접 import하고, 이 파일은 공용 mock/결과 fixture만 제공한다.
"""
from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from tests.unit.powerstone_test_fixtures import make_gogyo_result, make_numerology_result


@pytest.fixture
def gogyo_result() -> Dict[str, Any]:
    return make_gogyo_result()


@pytest.fixture
def numerology_result() -> Dict[str, Any]:
    return make_numerology_result()


@pytest.fixture
def mock_stone_uc() -> MagicMock:
    """구성기학 UseCase mock (SUT import 없이 사용 가능)."""
    uc = MagicMock()
    uc.execute.return_value = make_gogyo_result()
    return uc


@pytest.fixture
def mock_engine() -> MagicMock:
    """수비술 엔진 mock (SUT import 없이 사용 가능)."""
    engine = MagicMock()
    engine.recommend_as_dict.return_value = make_numerology_result()
    return engine
