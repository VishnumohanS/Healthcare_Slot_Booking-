from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)
    role: Literal["patient", "doctor"]
    specialization: str | None = Field(default=None, min_length=1, max_length=100)
    start_hour: int | None = Field(default=None, strict=True, ge=0, le=23)
    end_hour: int | None = Field(default=None, strict=True, ge=1, le=24)
    fee_paise: int | None = Field(default=None, strict=True, ge=100, le=100_000_000)
    bio: str = Field(default="", max_length=2000)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.lower()

    @model_validator(mode="after")
    def validate_role_fields(self):
        if self.role == "doctor":
            if not self.specialization or self.start_hour is None or self.end_hour is None or self.fee_paise is None:
                raise ValueError("Doctor registration requires specialization, working hours, and consultation fee.")
            if self.end_hour <= self.start_hour:
                raise ValueError("end_hour must be greater than start_hour.")
        elif any(value is not None for value in (self.specialization, self.start_hour, self.end_hour, self.fee_paise)):
            raise ValueError("Doctor profile fields are only valid for doctor accounts.")
        return self


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.lower()


class UserRead(BaseModel):
    id: int
    username: str
    name: str
    role: Literal["patient", "doctor"]
    doctor_id: int | None = None


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
