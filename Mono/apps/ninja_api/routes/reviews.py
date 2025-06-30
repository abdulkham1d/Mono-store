from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from apps.ninja_api.schemas.reviews import *
from apps.store.models import Review

router = Router()



@router.get("/", response=List[ReviewSchema], tags=["Reviews"])
def list_reviews(request):
    reviews = Review.objects.select_related('author', 'product').all()
    return [
        ReviewSchema(        # xar 1tasiga alohida qib yozib chiqsa bolarkan!!!
            id=review.id,
            text=review.text,
            author=review.author.id if review.author else None,
            product=review.product.id if review.product else None,
            created_at=review.created_at
        ) for review in reviews
    ]


@router.get("/{review_id}", response=ReviewSchema, tags=["Reviews"])
def get_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    return ReviewSchema(
        id=review.id,
        text=review.text,
        author=review.author.id if review.author else None,
        product=review.product.id if review.product else None,
        created_at=review.created_at
    )


@router.post("/", response=ReviewSchema, tags=["Reviews"])
def create_review(request, data: ReviewCreateUpdateSchema):
    review = Review.objects.create(**data.dict())
    return ReviewSchema(
        id=review.id,
        text=review.text,
        author=review.author.id if review.author else None,
        product=review.product.id if review.product else None,
        created_at=review.created_at
    )


@router.put("/{review_id}", response=ReviewSchema, tags=["Reviews"])
def update_review(request, review_id: int, data: ReviewCreateUpdateSchema):
    review = get_object_or_404(Review, id=review_id)
    for attr, value in data.dict().items():
        setattr(review, attr, value)
    review.save()
    return ReviewSchema(
        id=review.id,
        text=review.text,
        author=review.author.id if review.author else None,
        product=review.product.id if review.product else None,
        created_at=review.created_at
    )


@router.delete("/{review_id}", tags=["Reviews"])  # response=ReviewSchema ni olib tashlash kerak
def delete_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return {"success": True}  # Bu dict qaytaradi, ReviewSchema emas
