from typing import Literal

from pydantic import BaseModel, validator


class NutmegApiRequestParameters(BaseModel):
    starting_amount: int
    monthly_contributions: int
    timeframe: int
    investment_style: Literal["FIXED", "SRI", "MANAGED", "SMART_ALPHA"]
    risk_level: Literal["MA", "MB", "MC", "MD", "ME"]
    account_type: Literal["ISA", "GA"]

    @validator("starting_amount")
    def minimum_starting_amount(cls, v):
        minimum_starting_amount: int = 500
        if v < minimum_starting_amount:
            raise ValueError(
                (
                    f"Provided starting amount {v} less than minimum"
                    f" {minimum_starting_amount}"
                )
            )
        return v

    @validator("monthly_contributions")
    def monthly_contributions_not_negative(cls, v):
        if v < 0:
            raise ValueError("Invalid monthly contribution")
        return v

    @validator("timeframe")
    def minimum_timeframe(cls, v):
        minimum_timeframe: int = 3
        if v < minimum_timeframe:
            raise ValueError(
                f"Provided timeframe {v} less than minimum {minimum_timeframe}"
            )
        return v
