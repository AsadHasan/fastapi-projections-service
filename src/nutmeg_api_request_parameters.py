from typing import Literal

from pydantic import BaseModel


class NutmegApiRequestParameters(BaseModel):
    starting_amount: int
    monthly_contributions: int
    timeframe: int
    investment_style: Literal["FIXED", "SRI", "MANAGED", "SMART_ALPHA"]
    risk_level: Literal["MA", "MB", "MC", "MD", "ME"]
    account_type: Literal["ISA", "GA"]
