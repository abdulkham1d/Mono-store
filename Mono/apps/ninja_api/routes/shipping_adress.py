from datetime import datetime

from django.shortcuts import get_object_or_404
from ninja import Router

from apps.ninja_api.schemas.shipping_adress import ShippingAddressOut, ShippingAddressIn, ShippingAddressUpdate
from apps.store.models import ShippingAddress

router = Router(tags=['Shipping-addresses'])


@router.post('/', response=ShippingAddressOut)
def create_shipping_address(request, payload: ShippingAddressIn):
    data = payload.dict()
    if not data.get('created_at'):
        data['created_at'] = datetime.now().isoformat()

    return ShippingAddress.objects.create(**data)



@router.get('/{shipping_address_id}/', response=ShippingAddressOut)
def get_shipping_address(request, shipping_address_id: int):
    return get_object_or_404(ShippingAddress, id=shipping_address_id)


@router.get('/', response=list[ShippingAddressOut])
def list_shipping_addresses(request, limit: int = 100, offset: int = 0):
    return ShippingAddress.objects.all()[offset:offset + limit]


@router.put('/{shipping_address_id}/', response=ShippingAddressOut)
def update_shipping_address(request, shipping_address_id: int, payload: ShippingAddressIn):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)

    for attr, value in payload.dict().items():
        if value is not None:
            setattr(shipping_address, attr, value)

    shipping_address.save()
    return shipping_address


@router.patch('/{shipping_address_id}/', response=ShippingAddressOut)
def partial_update_shipping_address(request, shipping_address_id: int, payload: ShippingAddressUpdate):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)

    for attr, value in payload.dict().items():
        if value is not None:
            setattr(shipping_address, attr, value)

    shipping_address.save()
    return shipping_address


@router.delete('/{shipping_address_id}/')
def delete_shipping_address(request, shipping_address_id: int):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)
    shipping_address.delete()
    return {"success": True}

