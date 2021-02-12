from typing import Any, Dict, List, Literal, Tuple, Union

import requests
from fastapi import FastAPI, HTTPException, status
from requests.models import Response

from src.nutmeg_api_request_parameters import NutmegApiRequestParameters


def _validate_starting_amount_and_timeframe(
    starting_amount: int, timeframe: int
) -> None:
    minimum_starting_amount: int = 500
    minimum_timeframe: int = 3
    if starting_amount < minimum_starting_amount:
        raise ValueError(
            (
                f"Provided starting amount {starting_amount} "
                f"less than minimum {minimum_starting_amount}"
            )
        )
    if timeframe < minimum_timeframe:
        raise ValueError(
            (
                f"Provided timeframe {timeframe} less than "
                f"minimum {minimum_timeframe}"
            )
        )


def _get_parameters(
    request_parameters: NutmegApiRequestParameters,
) -> Dict[str, Union[int, str]]:
    return {
        "lumpSum": request_parameters.starting_amount,
        "contributions": request_parameters.monthly_contributions,
        "model": request_parameters.risk_level,
        "percentiles": "P5,P50,P95",
        "timeframe": request_parameters.timeframe,
        "investmentStyle": request_parameters.investment_style,
    }


def _get_nutmeg_api_response(
    request_parameters: NutmegApiRequestParameters,
) -> Dict[str, Any]:
    _validate_starting_amount_and_timeframe(
        request_parameters.starting_amount, request_parameters.timeframe
    )
    response: Response = requests.get(
        (
            f"https://api.nutmeg.com/nm-pot-service/projections/"
            f"{request_parameters.account_type}/prospects"
        ),
        params=_get_parameters(request_parameters),
    )
    response.raise_for_status()
    return response.json()


def _get_expected_returns(
    series: Dict[str, Dict[str, List[Union[int, float]]]], percentile: str
) -> List[Union[int, float]]:
    return series[percentile]["expectedReturns"]


def _get_projections(
    request_parameters: NutmegApiRequestParameters,
) -> Tuple[List[Union[int, float]], List[Union[int, float]], List[Union[int, float]]]:
    series: Dict[str, Dict[str, List[Union[int, float]]]] = _get_nutmeg_api_response(
        request_parameters
    )["series"]
    projections: List[Union[int, float]] = _get_expected_returns(series, "P50")
    low_projections: List[Union[int, float]] = _get_expected_returns(series, "P5")
    high_projections: List[Union[int, float]] = _get_expected_returns(series, "P95")
    return projections, low_projections, high_projections


def _get_year_one_projections(
    projections: Tuple[
        List[Union[int, float]], List[Union[int, float]], List[Union[int, float]]
    ],
) -> Tuple[Union[int, float], Union[int, float], Union[int, float]]:
    year_one_index: int = 12
    return (
        projections[0][year_one_index],
        projections[1][year_one_index],
        projections[2][year_one_index],
    )


def _get_timeframe_end_projections(
    projections: Tuple[
        List[Union[int, float]], List[Union[int, float]], List[Union[int, float]]
    ],
) -> Tuple[Union[int, float], Union[int, float], Union[int, float]]:
    return (
        projections[0][-1],
        projections[1][-1],
        projections[2][-1],
    )


def _get_projections_info(
    request_parameters: NutmegApiRequestParameters,
) -> Dict[str, Dict[str, Union[int, float]]]:
    projections: Tuple[
        List[Union[int, float]], List[Union[int, float]], List[Union[int, float]]
    ] = _get_projections(request_parameters)
    year_one_projections: Tuple[
        Union[int, float], Union[int, float], Union[int, float]
    ] = _get_year_one_projections(projections)
    timeframe_end_projections: Tuple[
        Union[int, float], Union[int, float], Union[int, float]
    ] = _get_timeframe_end_projections(projections)
    return {
        "Year one end": {
            "Projection": year_one_projections[0],
            "lowProjection": year_one_projections[1],
            "highProjection": year_one_projections[2],
        },
        "Timeframe-end": {
            "Projection": timeframe_end_projections[0],
            "lowProjection": timeframe_end_projections[1],
            "highProjection": timeframe_end_projections[2],
        },
    }


app = FastAPI()


@app.get("/projections/")
def get_all_projections(
    starting_amount: int,
    monthly_contributions: int,
    timeframe: int,
    investment_style: Literal["FIXED", "SRI", "MANAGED", "SMART_ALPHA"],
    risk_level: Literal["MA", "MB", "MC", "MD", "ME"],
    account_type: Literal["ISA", "GA"],
) -> Dict[str, Dict[str, Union[int, float]]]:
    parameters: NutmegApiRequestParameters = NutmegApiRequestParameters(
        **{
            "starting_amount": starting_amount,
            "monthly_contributions": monthly_contributions,
            "timeframe": timeframe,
            "investment_style": investment_style,
            "risk_level": risk_level,
            "account_type": account_type,
        }
    )
    try:
        return _get_projections_info(parameters)
    except requests.exceptions.HTTPError as exception:
        raise HTTPException(
            status_code=exception.response.status_code, detail=exception.strerror
        ) from None
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=exception.args[0]
        ) from None
