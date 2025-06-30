from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from apps.ninja_api.schemas.products import ProductSchema, ProductCreateUpdateSchema
from apps.store.models import Product

router = Router()


@router.get("/", response=List[ProductSchema],
            tags=["Products"])  # tags bu defoultdan qutilish uchun yordam beradi i + sort uchun
def list_products(request):
    return Product.objects.order_by("id")


@router.get("/{product_id}", response=ProductSchema, tags=["Products"])
def get_product(request, product_id: int):
    return get_object_or_404(Product, id=product_id)


@router.post("/", response=ProductSchema, tags=["Products"])
def create_product(request, data: ProductCreateUpdateSchema):
    product = Product.objects.create(**data.dict())
    return product


@router.put("/{product_id}", response=ProductSchema, tags=["Products"])
def update_product(request, product_id: int, data: ProductCreateUpdateSchema):
    product = get_object_or_404(Product, id=product_id)
    for attr, value in data.dict().items():
        setattr(product, attr, value)
    product.save()
    return product


@router.delete("/{product_id}", tags=["Products"])
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {"success": True}




