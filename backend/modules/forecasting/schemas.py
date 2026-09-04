from pydantic import BaseModel, Field


class ForecastRunCreate(BaseModel):
    horizon_days: int = Field(default=14, ge=1, le=90)
    location_id: str = Field(default="main", min_length=1, max_length=60)
    lookback_days: int = Field(default=60, ge=14, le=365)
