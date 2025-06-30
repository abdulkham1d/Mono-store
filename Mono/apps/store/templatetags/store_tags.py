from django import template
from apps.store.models import *

register = template.Library()


@register.simple_tag()
def get_category():
    return Category.objects.filter(parent=True)


@register.simple_tag()
def get_category_s():
    return Category.objects.filter(parent=None)


@register.simple_tag()
def get_subcategory(category):
    return Category.objects.filter(parent=category)


@register.simple_tag()
def get_sorted():
    sorters = [
        {
            'title': 'Price',
            'sorters': [
                ('price', ' Low to High'),
                ('-price', 'High to Low')
            ]
        }
    ]
    return sorters

@register.simple_tag()
def get_favourite_products(user):
    if user.is_authenticated:
        fav = FavouriteProducts.objects.filter(user=user)
        return [i.product for i in fav]
    return []

@register.simple_tag
def order_total(order):
    return sum(item.product.price * item.quantity for item in order.items.all())