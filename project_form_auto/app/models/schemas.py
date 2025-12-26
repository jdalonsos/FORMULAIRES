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