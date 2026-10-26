from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, Field, ConfigDict, field_validator


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class RegisterRequest(APIModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=72)
    password_confirmation: str = Field(validation_alias=AliasChoices("passwordConfirmation", "password_confirmation"))

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        if not EMAIL_PATTERN.fullmatch(email):
            raise ValueError("Укажите корректный email")
        return email


class LoginRequest(APIModel):
    email: str = Field(min_length=3, max_length=255)
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        if not EMAIL_PATTERN.fullmatch(email):
            raise ValueError("Укажите корректный email")
        return email


class DraftUpdate(APIModel):
    company_data: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("companyData", "company_data"))
    financial_data: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("financialData", "financial_data"))


class SubmitRequest(APIModel):
    product_id: str = Field(validation_alias=AliasChoices("productId", "selectedProductId", "product_id"))


class StaffDecisionRequest(APIModel):
    decision: Literal["approved", "rejected", "needs_info", "counteroffer"]
    comment: str = Field(default="", max_length=2000)
    proposed_amount: int | None = Field(default=None, validation_alias=AliasChoices("proposedAmount", "proposed_amount"), gt=0)
    proposed_term_months: int | None = Field(default=None, validation_alias=AliasChoices("proposedTermMonths", "proposed_term_months"), gt=0, le=120)


class OfferDecisionRequest(APIModel):
    decision: Literal["accept", "decline"]


class CompanySaveRequest(APIModel):
    inn: str
    ogrn: str = ""
    company_name: str = Field(validation_alias=AliasChoices("companyName", "company_name"))
    address: str = ""
    okved: str

    @field_validator("inn")
    @classmethod
    def validate_inn(cls, value: str) -> str:
        inn = value.strip()
        if not re.fullmatch(r"(\d{10}|\d{12})", inn):
            raise ValueError("ИНН должен содержать 10 или 12 цифр")
        return inn

    @field_validator("ogrn")
    @classmethod
    def validate_ogrn(cls, value: str) -> str:
        ogrn = value.strip()
        if ogrn and not re.fullmatch(r"(\d{13}|\d{15})", ogrn):
            raise ValueError("ОГРН/ОГРНИП должен содержать 13 или 15 цифр")
        return ogrn



