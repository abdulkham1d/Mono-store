from typing import Optional

from django.conf import settings
from pydantic import BaseModel, ConfigDict
from pydantic import field_validator


class CategorySchema(BaseModel):
    id: int
    title: str
    image: Optional[str] = None
    slug: Optional[str] = None
    parent: Optional[int] = None

    # Pydantic v2 usuli
    model_config = ConfigDict(from_attributes=True)

    @field_validator('image')
    def image_full_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            return f"{settings.BASE_URL}{v}"
        return v


class CategoryCreateUpdateSchema(BaseModel):
    title: str
    image: Optional[str] = None
    slug: Optional[str] = None
    parent: Optional[int] = None

    @field_validator('title')
    def title_length(cls, v):
        if len(v) < 2:
            raise ValueError("Title too short")
        return v
