from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")


class DetectRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL de la page à analyser")


class DetectResponse(BaseModel):
    url: str
    http_status: int
    has_form: bool
    forms_count: int
    has_inputs: bool
    probable_form: bool
    reasons: list[str]


class FormField(BaseModel):
    tag: str
    type: Optional[str] = None
    name: Optional[str] = None
    id: Optional[str] = None
    placeholder: Optional[str] = None
    label: Optional[str] = None


class FormAnalyzeResponse(BaseModel):
    url: str
    fields_count: int
    fields: list[FormField]


class UserData(BaseModel):
    # Identité
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    birth_day: Optional[int] = None
    birth_month: Optional[int] = None
    birth_year: Optional[int] = None
    age: Optional[int] = None

    # Contact
    email: Optional[str] = None
    phone: Optional[str] = None

    # Adresse
    address: Optional[str] = None
    street: Optional[str] = None
    street_number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    company: Optional[str] = None


class UserResponse(BaseModel):
    user: UserData | None


class UserPatchRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    birth_day: Optional[int] = None
    birth_month: Optional[int] = None
    birth_year: Optional[int] = None
    age: Optional[int] = None

    email: Optional[str] = None
    phone: Optional[str] = None

    address: Optional[str] = None
    street: Optional[str] = None
    street_number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    company: Optional[str] = None


class MappedFormField(FormField):
    matched_key: Optional[str] = Field(
        None, description="UserData key matched to this form field"
    )
    confidence: float = Field(
        0.0, ge=0.0, le=1.0, description="Confidence score of the matching"
    )
    reason: Optional[str] = Field(
        None, description="Explanation of why this field was matched"
    )


class FormMapRequest(BaseModel):
    url: str
    user_data: UserData


class FormMapResponse(BaseModel):
    url: str
    total_fields: int
    matched_fields: int
    fields: list[MappedFormField]
