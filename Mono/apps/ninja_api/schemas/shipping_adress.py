from typing import Optional

from ninja import Schema
from ninja.orm import create_schema

from apps.store.models import ShippingAddress

# Output schema (for responses)
ShippingAddressOut = create_schema(
    ShippingAddress,
    fields=['id', 'customer', 'order', 'address', 'city', 'region',  'created_at']  # qaysi fieldga yozmoqchi bosam osha fieldni chaqirsam boladi!!!
)


class ShippingAddressIn(Schema):
    customer_id: Optional[int] = None
    order_id: Optional[int] = None
    address: str
    city: str
    region: str
    phone: str
    created_at: Optional[str] = None
    class Config:
        from_attributes = True


# Update schema (partial updates)
class ShippingAddressUpdate(Schema):
    customer_id: Optional[int] = None
    order_id: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[str] = None
