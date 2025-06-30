import os
from datetime import datetime


from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class User_tg(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    phone = PhoneNumberField(max_length=100, null=True, blank=True, unique=True)
    bio = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    last_login = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Tg User"
        verbose_name_plural = "Tg Users"


def category_image_upload_path(instance, filename):
    category_slug = slugify(instance.title)
    ext = filename.split('.')[-1]
    filename = f"{category_slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    return os.path.join('Tg/Categories', category_slug, filename)


def product_image_upload_path(instance, filename):
    product_slug = slugify(instance.product.title)
    ext = filename.split('.')[-1]
    filename = f"{product_slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    return os.path.join('Tg/Product', product_slug, filename)


class Category(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    image = models.ImageField(_('Image'), upload_to=category_image_upload_path, null=True, blank=True)
    slug = models.SlugField(_('Slug'), unique=True)
    parent = models.ForeignKey('self',
                               on_delete=models.CASCADE,
                               null=True, blank=True,
                               verbose_name=_('Parent'),
                               related_name='subcategories')

    objects = models.Manager()

    def get_absolute_url(self):
        ...

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return ''

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'<Category: pk={self.pk}>, title={self.title}'

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class Product(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    color = models.CharField(_('Color'), max_length=255)
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'),
                                 related_name='products')
    size = models.CharField(_('Size'), max_length=255)

    objects = models.Manager()

    def get_absolute_url(self):
        ...

    def get_first_photo(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return 'X'
        else:
            return 'X'

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'<Product: pk={self.pk}>, title={self.title}, price={self.price}>'

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')


class Gallery(models.Model):
    image = models.ImageField(_('Picture'), upload_to=product_image_upload_path, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name = _('Picture')
        verbose_name_plural = _('Pictures')


