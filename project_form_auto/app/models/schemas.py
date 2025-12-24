from pydantic import BaseModel, Field, HttpUrl


class DetectRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL de la page à analyser")
