from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ProductSchema(BaseModel):
    id: int
    title: str
    color: Optional[str]
    price: Decimal
    slug: Optional[str]
    description: Optional[str]
    category_id: int
    quantity: Optional[int]
    size: Optional[str]
    country_of_origin: Optional[str]
    material: Optional[str]
    weight: Optional[str]
    warranty: Optional[str]
    model: Optional[str]

    class Config:
        from_attributes = True


class ProductCreateUpdateSchema(BaseModel):
    title: str
    color: Optional[str] = None
    price: Decimal
    slug: Optional[str] = None
    description: Optional[str] = None
    category_id: int
    quantity: Optional[int] = None
    size: Optional[str] = None
    country_of_origin: Optional[str] = None
    material: Optional[str] = None
    weight: Optional[str] = None
    warranty: Optional[str] = None
    model: Optional[str] = None

