from typing import Any, Dict, Union

import requests
from requests.models import Response


def test_projections() -> None:
    url: str = "http://nutmegplayground/projections"
    params: Dict[str, Union[int, str]] = {
        "starting_amount": 10000,
        "monthly_contributions": 50,
        "timeframe": 20,
        "investment_style": "FIXED",
        "risk_level": "MC",
        "account_type": "ISA",
    }
    response: Response = requests.request("GET", url, params=params)
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
