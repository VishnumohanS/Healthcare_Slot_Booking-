from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    field: str = Field(description="Location of the problem, e.g. 'body.slot'.")
    message: str
    type: str


class ErrorBody(BaseModel):
    code: str = Field(examples=["not_found"])
    message: str = Field(examples=["Doctor 42 not found."])
    details: list[ErrorDetail] | None = None


class ErrorResponse(BaseModel):
    """Uniform error envelope returned for every 4xx/5xx response."""

    error: ErrorBody


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])


class SchedulingConfig(BaseModel):
    slot_duration_minutes: int = Field(description="Length of every appointment slot.", examples=[30])
