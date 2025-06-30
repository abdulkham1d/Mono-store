from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.store.models import *


class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category', 'price', 'quantity', 'size', 'color', 'get_photo')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('price', 'quantity')
    list_filter = ('size', 'color', 'price')
    list_display_links = ('title',)
    inlines = [GalleryInline]

    def get_photo(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="70" height="70">')
            except:
                return 'X'
        return 'X'


admin.site.register(Gallery)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderProduct)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order', 'address', 'city', 'region', 'phone', 'created_at')
    search_fields = ('address', 'city', 'region', 'phone')
    list_filter = ('region', 'created_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass
