from typing import Any, Dict, List, Tuple, Union

import requests
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ValidationError
from requests.models import Response

from src.nutmeg_api_request_parameters import NutmegApiRequestParameters


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


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.get("/projections/")
def get_all_projections(
    nutmeg_api_request_parameters: NutmegApiRequestParameters = Depends(),
) -> Dict[str, Dict[str, Union[int, float]]]:
    try:
        return _get_projections_info(nutmeg_api_request_parameters)
    except requests.exceptions.HTTPError as exception:
        raise HTTPException(
            status_code=exception.response.status_code, detail=exception.strerror
        ) from None
