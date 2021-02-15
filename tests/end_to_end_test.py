import os
from typing import Any, Dict, Union

import requests
from requests.models import Response


def _get_url() -> str:
    try:
        return f"{os.environ['BASE_URL']}/projections"
    except KeyError as exception:
        raise ValueError(
            f"Environment variable {exception.args[0]} not set"
        ) from exception


def test_projections() -> None:
    params: Dict[str, Union[int, str]] = {
        "starting_amount": 10000,
        "monthly_contributions": 50,
        "timeframe": 20,
        "investment_style": "FIXED",
        "risk_level": "MC",
        "account_type": "ISA",
    }
    response: Response = requests.request("GET", _get_url(), params=params)
    response.raise_for_status()
    projections: Dict[str, Any] = response.json()
    year_one_projections: Dict[str, int] = projections["Year one end"]
    timeframe_end_projections: Dict[str, int] = projections["Timeframe-end"]
    assert year_one_projections
    assert timeframe_end_projections
    assert year_one_projections["Projection"] == 11086
    assert year_one_projections["lowProjection"] == 9618
    assert year_one_projections["highProjection"] == 12787
    assert timeframe_end_projections["Projection"] == 44935
    assert timeframe_end_projections["lowProjection"] == 28387
    assert timeframe_end_projections["highProjection"] == 74828
