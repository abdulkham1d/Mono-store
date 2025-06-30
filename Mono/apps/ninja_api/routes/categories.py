from typing import List
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.store.models import Category
from apps.ninja_api.schemas.categories import CategorySchema, CategoryCreateUpdateSchema

router = Router(tags=["Categories"])

# Serializer funksiyasiga hojat yo'q - Schema avtomatik serializatsiya qiladi
# Faqat image URL ni to'g'rilash kerak bo'lsa, schema validatorda qilinadi

@router.get("/", response=List[CategorySchema])
def list_categories(request):
    return Category.objects.order_by("id").all()

@router.get("/{category_id}", response=CategorySchema)
def get_category(request, category_id: int):
    return get_object_or_404(Category, id=category_id)

@router.post("/", response=CategorySchema)
@transaction.atomic
def create_category(request, data: CategoryCreateUpdateSchema):
    # Slug avtomatik yaratish
    category_data = data.model_dump()
    if not category_data.get('slug'):
        category_data['slug'] = category_data['title'].lower().replace(' ', '-')
    return Category.objects.create(**category_data)

@router.put("/{category_id}", response=CategorySchema)
@transaction.atomic
def update_category(request, category_id: int, data: CategoryCreateUpdateSchema):
    category = get_object_or_404(Category, id=category_id)
    for attr, value in data.model_dump().items():
        setattr(category, attr, value)
    category.save()
    return category

@router.delete("/{category_id}")
@transaction.atomic
def delete_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return {"success": True}