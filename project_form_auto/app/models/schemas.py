from typing import Optional

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

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


# -------------------------------------------------------------------------------------------------
# Models related to automatic form filling
# -------------------------------------------------------------------------------------------------

class AutoFillRequest(BaseModel):
    """Request body for auto‑filling a form.

    A request specifying which URL should be loaded and a set of user data
    attributes. The API will attempt to match form fields on the page to
    properties of the ``user_data`` object and input those values via a headless
    browser. The ``url`` field does not enforce ``HttpUrl`` so that local or
    internal resources can be targeted as well.
    """

    url: str
    user_data: UserData


class AutofilledField(MappedFormField):
    """Representation of a single form field after auto‑filling.

    Extends ``MappedFormField`` with a ``filled`` boolean that indicates
    whether a value was actually inserted into the corresponding DOM element.
    The inherited ``matched_key`` and ``confidence`` indicate why a user
    property was chosen for this field and how confident the heuristic was.
    """

    filled: bool = False


class AutoFillResponse(BaseModel):
    """Response returned after attempting to auto‑fill a web form.

    Contains high level statistics about the number of form fields encountered
    and how many were successfully filled, along with detailed information
    about each field.
    """

    url: str
    total_fields: int
    filled_fields: int
    fields: list[AutofilledField]
