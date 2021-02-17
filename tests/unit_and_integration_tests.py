import json
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import fastapi
import pytest
import requests_mock
from pydantic.error_wrappers import ValidationError

from src.main import get_all_projections
from src.nutmeg_api_request_parameters import NutmegApiRequestParameters


def _get_sample_response() -> Dict[str, Any]:
    with open("tests/sample.json") as sample:
        return json.load(sample)


@patch("src.main.requests.get")
def test_projections_success(mock_get: MagicMock) -> None:
    mock_get.return_value.ok = True
    mock_get.return_value.json.return_value = _get_sample_response()
    query_parameters: NutmegApiRequestParameters = NutmegApiRequestParameters(
        **{
            "starting_amount": 500,
            "monthly_contributions": 10,
            "timeframe": 3,
            "investment_style": "FIXED",
            "risk_level": "MC",
            "account_type": "ISA",
        }
    )
    projections: Dict[str, Dict[str, int]] = get_all_projections(query_parameters)
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
    with pytest.raises(ValidationError) as excinfo:
        NutmegApiRequestParameters(
            **{
                "starting_amount": 499,
                "monthly_contributions": 10,
                "timeframe": 3,
                "investment_style": "FIXED",
                "risk_level": "MC",
                "account_type": "ISA",
            }
        )
    assert "Provided starting amount 499 less than minimum 500" in str(excinfo.value)


def test_invalid_monthly_contribution_raises_error() -> None:
    with pytest.raises(ValidationError) as excinfo:
        NutmegApiRequestParameters(
            **{
                "starting_amount": 500,
                "monthly_contributions": -1,
                "timeframe": 3,
                "investment_style": "FIXED",
                "risk_level": "MC",
                "account_type": "ISA",
            }
        )
    assert "Invalid monthly contribution" in str(excinfo.value)


def test_invalid_timeframe_raises_error() -> None:
    with pytest.raises(ValidationError) as excinfo:
        NutmegApiRequestParameters(
            **{
                "starting_amount": 500,
                "monthly_contributions": 10,
                "timeframe": 2,
                "investment_style": "FIXED",
                "risk_level": "MC",
                "account_type": "ISA",
            }
        )
    assert "Provided timeframe 2 less than minimum 3" in str(excinfo.value)


def test_invalid_account_type_raises_error() -> None:
    with pytest.raises(ValidationError) as excinfo:
        NutmegApiRequestParameters(
            **{
                "starting_amount": 500,
                "monthly_contributions": 10,
                "timeframe": 3,
                "investment_style": "FIXED",
                "risk_level": "MC",
                "account_type": "SAVINGS",
            }
        )
    assert excinfo.value.errors
    assert "account_type" in str(excinfo.value)


def test_invalid_investment_style_raises_error() -> None:
    with pytest.raises(ValidationError) as excinfo:
        NutmegApiRequestParameters(
            **{
                "starting_amount": 500,
                "monthly_contributions": 10,
                "timeframe": 3,
                "investment_style": "SMART",
                "risk_level": "MC",
                "account_type": "ISA",
            }
        )
    assert excinfo.value.errors
    assert "investment_style" in str(excinfo.value)


def test_invalid_risk_level_raises_error() -> None:
    with pytest.raises(ValidationError) as excinfo:
        NutmegApiRequestParameters(
            **{
                "starting_amount": 500,
                "monthly_contributions": 10,
                "timeframe": 3,
                "investment_style": "FIXED",
                "risk_level": "MF",
                "account_type": "ISA",
            }
        )
    assert excinfo.value.errors
    assert "risk_level" in str(excinfo.value)


def test_http_exception():
    query_parameters: NutmegApiRequestParameters = NutmegApiRequestParameters(
        **{
            "starting_amount": 500,
            "monthly_contributions": 10,
            "timeframe": 3,
            "investment_style": "FIXED",
            "risk_level": "MC",
            "account_type": "ISA",
        }
    )
    error_message: str = "Internal Server Error"
    with requests_mock.mock() as mock_request:
        mock_request.get(requests_mock.ANY, status_code=500, text=error_message)
        with pytest.raises(fastapi.exceptions.HTTPException) as excinfo:
            get_all_projections(query_parameters)
    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == error_message
