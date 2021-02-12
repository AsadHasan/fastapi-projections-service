import json
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from fastapi.exceptions import HTTPException
from pydantic.error_wrappers import ValidationError

from src.main import get_all_projections


def _get_sample_response() -> Dict[str, Any]:
    with open("tests/sample.json") as sample:
        return json.load(sample)


@patch("src.main.requests.get")
def test_projections_success(mock_get: MagicMock) -> None:
    mock_get.return_value.ok = True
    mock_get.return_value.json.return_value = _get_sample_response()
    projections: Dict[str, Dict[str, int]] = get_all_projections(
        500, 10, 3, "FIXED", "MC", "ISA"
    )
    year_one_projections: Dict[str, int] = projections["Year one end"]
    timeframe_end_projections: Dict[str, int] = projections["Timeframe-end"]
    assert year_one_projections
    assert timeframe_end_projections
    assert year_one_projections["Projection"] == 646
    assert year_one_projections["lowProjection"] == 569
    assert year_one_projections["highProjection"] == 735
    assert timeframe_end_projections["Projection"] == 960
    assert timeframe_end_projections["lowProjection"] == 799
    assert timeframe_end_projections["highProjection"] == 1163


def test_invalid_starting_amount_raises_error() -> None:
    with pytest.raises(HTTPException) as excinfo:
        get_all_projections(499, 10, 3, "FIXED", "MC", "ISA")
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Provided starting amount 499 less than minimum 500"


def test_invalid_timeframe_raises_error() -> None:
    with pytest.raises(HTTPException) as excinfo:
        get_all_projections(500, 10, 2, "FIXED", "MC", "ISA")
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Provided timeframe 2 less than minimum 3"


def test_invalid_account_type_raises_error() -> None:
    with pytest.raises(ValidationError) as excinfo:
        get_all_projections(500, 10, 2, "FIXED", "MC", "SAVINGS")
    assert excinfo.value.errors
    assert "account_type" in str(excinfo.value)


def test_invalid_investment_style_raises_error() -> None:
    with pytest.raises(ValidationError) as excinfo:
        get_all_projections(500, 10, 2, "SMART", "MC", "GA")
    assert excinfo.value.errors
    assert "investment_style" in str(excinfo.value)


def test_invalid_risk_level_raises_error() -> None:
    with pytest.raises(ValidationError) as excinfo:
        get_all_projections(500, 10, 2, "MANAGED", "MF", "GA")
    assert excinfo.value.errors
    assert "risk_level" in str(excinfo.value)
