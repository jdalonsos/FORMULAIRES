from pydantic import BaseModel, Field, HttpUrl


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
