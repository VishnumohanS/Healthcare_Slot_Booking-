from pydantic import BaseModel, ConfigDict, Field, model_validator


class DoctorCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {"name": "Dr. Asha Raman", "specialization": "Cardiology", "start_hour": 9, "end_hour": 17}
            ]
        },
    )

    name: str = Field(min_length=1, max_length=100, description="Doctor's full name.")
    specialization: str = Field(min_length=1, max_length=100)
    start_hour: int = Field(strict=True, ge=0, le=23, description="First working hour (0-23).")
    end_hour: int = Field(strict=True, ge=1, le=24, description="Closing hour (1-24); must be > start_hour.")
    fee_paise: int = Field(default=50000, strict=True, ge=100, le=100_000_000)
    bio: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def _end_after_start(self) -> "DoctorCreate":
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be greater than start_hour")
        return self


class DoctorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    specialization: str
    start_hour: int
    end_hour: int
    fee_paise: int
    bio: str


class DoctorUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    specialization: str = Field(min_length=1, max_length=100)
    start_hour: int = Field(strict=True, ge=0, le=23)
    end_hour: int = Field(strict=True, ge=1, le=24)
    fee_paise: int = Field(strict=True, ge=100, le=100_000_000)
    bio: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def _end_after_start(self) -> "DoctorUpdate":
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be greater than start_hour")
        return self
