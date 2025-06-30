from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReviewSchema(BaseModel):
    id: int
    text: str
    author: Optional[int]
    product: Optional[int]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReviewCreateUpdateSchema(BaseModel):
    text: str
    author: Optional[int] = None
    product: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
