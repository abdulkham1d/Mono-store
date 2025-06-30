import os
from datetime import datetime

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from apps.users.models import User


def category_image_upload_path(instance, filename):
    category_slug = slugify(instance.title)
    ext = filename.split('.')[-1]
    filename = f"{category_slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    return os.path.join('Categories', category_slug, filename)


def product_image_upload_path(instance, filename):
    product_slug = slugify(instance.product.title)
    ext = filename.split('.')[-1]
    filename = f"{product_slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    return os.path.join('Product', product_slug, filename)


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
        return reverse('category_detail', kwargs={'slug': self.slug})

    def get_image(self):
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
    title = models.CharField(_('Name of product'), max_length=255)
    color = models.CharField(_('Color'), max_length=255, null=True, blank=True)
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    slug = models.SlugField(_('Slug'), unique=True, null=True)
    description = models.TextField(_('Description'), null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'),
                                 related_name='products')

    quantity = models.IntegerField(_('Quantity'), null=True, blank=True)
    size = models.CharField(_('Size'), max_length=255, null=True, blank=True)
    country_of_origin = models.CharField(_('Country of origin'), max_length=255, null=True, blank=True)
    material = models.CharField(_('Material'), max_length=255, null=True, blank=True)
    weight = models.CharField(_('Weight'), max_length=255, null=True, blank=True)
    warranty = models.CharField(_('Warranty'), max_length=255, null=True, blank=True)
    model = models.CharField(_('Model'), max_length=255, null=True, blank=True)

    objects = models.Manager()

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

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


class Review(models.Model):
    text = models.TextField(_('Review'), null=False, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')


class FavouriteProducts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = _('Favourite Products')
        verbose_name_plural = _('Favourite Products')


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, verbose_name=_('User'), null=True, blank=True)
    name = models.CharField(_('Name of user'), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Customer'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Date time order'))
    shipping = models.BooleanField(default=True, verbose_name=_('Shipping'))

    def __str__(self):
        return str(self.pk) + ' '

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    # Obshiy summasini xisoblidi addelni
    @property
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price

    # Obshiy sonini xisoblidi addelni
    @property
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name=_('Product'))
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name=_('Order'))
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name=_('Quantity'))
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Order Product')
        verbose_name_plural = _('Order Products')

    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    region = models.CharField(max_length=120)
    phone = PhoneNumberField(region='UZ', unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = _('Shipping Address')
        verbose_name_plural = _('Shipping Addresses')


from django.utils import timezone


class Contact(models.Model):
    """
    Contact form model
    """

    # Basic information
    name = models.CharField(_('Full Name'), max_length=100)
    email = models.EmailField(_('Email Address'))
    phone = models.CharField(_('Phone Number'), max_length=20, blank=True, null=True)
    subject = models.CharField(_('Subject'), max_length=200)
    message = models.TextField(_('Message'))

    # Additional information
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('User')
    )
    ip_address = models.GenericIPAddressField(_('IP Address'), blank=True, null=True)
    user_agent = models.TextField(_('User Agent'), blank=True)

    # Status
    is_read = models.BooleanField(_('Read'), default=False)
    is_replied = models.BooleanField(_('Replied'), default=False)
    reply_message = models.TextField(_('Reply Message'), blank=True)

    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    replied_at = models.DateTimeField(_('Replied At'), blank=True, null=True)

    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject[:50]}"

    def mark_as_read(self):
        """Xabarni o'qilgan deb belgilash"""
        self.is_read = True
        self.save()

    def mark_as_replied(self, reply_message=""):
        """Xabarni javob berilgan deb belgilash"""
        self.is_replied = True
        self.replied_at = timezone.now()
        if reply_message:
            self.reply_message = reply_message
        self.save()

    @property
    def short_message(self):
        """Qisqa xabar ko'rsatish uchun"""
        if len(self.message) > 100:
            return self.message[:100] + "..."
        return self.message


