import re
from datetime import timedelta

import stripe
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView

from shop import settings
from .forms import *
from .models import *
from .utils import *


class ProductListView(ListView):
    model = Product
    context_object_name = 'categories'
    extra_context = {
        'title': 'MONO - Minimalist Shopping',
    }

    template_name = 'store/product_list.html'

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories


class CategoryListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/category_page.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        main_category = Category.objects.get(slug=self.kwargs['slug'])
        context['category'] = main_category
        context['title'] = f'{main_category.title}'

        subcategories = main_category.subcategories.all()
        subcategories_data = []

        for subcategory in subcategories:
            subcategory_products = Product.objects.filter(category=subcategory)[:3]
            if subcategory_products:  # Agar mahsulot bo'lsa qo'shamiz
                subcategories_data.append({
                    'subcategory': subcategory,
                    'products': subcategory_products
                })

        context['subcategories_data'] = subcategories_data
        return context


class SubCategoryProductsView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/subcategory_products.html'

    def get_queryset(self):
        subcategory = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Product.objects.filter(category=subcategory)

        sort_by = self.request.GET.get('sort')
        if sort_by:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subcategory = Category.objects.get(slug=self.kwargs['slug'])
        context['subcategory'] = subcategory
        context['title'] = f"All Products in {subcategory.title}"
        return context


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = self.object.title

        context['reviews'] = Review.objects.filter(product=product)

        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()

        return context


# Yozvotgan cometariya soxranit bolib ketishi mumkin

def save_review(request, product_id):
    form = ReviewForm(data=request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        product = Product.objects.get(pk=product_id)
        review.product = product
        review.save()
    else:
        pass
    return redirect('product_detail', product.slug)


@login_required
@user_passes_test(lambda u: u.is_staff)  # Faqat adminlar uchun
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    product_slug = review.product.slug
    review.delete()
    return redirect('product_detail', slug=product_slug)


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()  # foydalanuvchini yaratamiz
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # backend belgilash
            login(request, user)  # avtomatik login
            return redirect('product_list')  # asosiy sahifaga yo‘naltirish
        else:
            messages.error(request, 'Form is not valid')
            return redirect('register')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
        'title': 'Registration'
    }
    return render(request, 'store/register.html', context)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # backend belgilash
            login(request, user)
            return redirect('product_list')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def search_results(request):
    query = request.GET.get('q')
    product = Product.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )

    context = {
        'product': product,
    }
    return render(request, 'store/category_page.html', context)


from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy


def save_favourite_products(request, product_slug):
    user = request.user if request.user.is_authenticated else None
    product = get_object_or_404(Product, slug=product_slug)

    if user:
        fav_product = FavouriteProducts.objects.filter(user=user, product=product)
        if fav_product.exists():
            fav_product.delete()
        else:
            FavouriteProducts.objects.create(user=user, product=product)

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect(reverse('product_list'))


def user_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        customer = None

    orders = Order.objects.filter(customer=customer)

    context = {
        'orders': orders,
        'customer': customer,
    }
    return render(request, 'store/user_profile.html', context)


class FavouriteProductsView(LoginRequiredMixin, ListView):
    model = FavouriteProducts
    context_object_name = 'products'
    template_name = 'store/favourite_products.html'
    login_url = 'login'

    def get_queryset(self):
        user = self.request.user
        favs = FavouriteProducts.objects.filter(user=user)
        products = [i.product for i in favs]
        return products


def cart(request):
    cart_info = get_cart_data(request)

    context = {
        'title': 'Shopping Cart',
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'order': cart_info['order'],
        'products': cart_info['products']
    }

    return render(request, 'store/cart.html', context)


def to_cart(request, product_id, action):
    if request.user.is_authenticated:
        user_cart = CartAuthenticatedUser(request, product_id, action)
        return redirect('cart')
    else:
        messages.error(request, 'You must be logged ')
        return redirect('login')


def clear_cart(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(customer=customer)
        order.orderproduct_set.all().delete()
        messages.success(request, 'Cart cleared successfully!')
    return redirect('cart')


def checkout(request):
    cart_info = get_cart_data(request)

    context = {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'order': cart_info['order'],
        'products': cart_info['products'],
        'title': 'Buy products',
        'customer_form': CustomerForm(),
        'shipping_form': ShippingAddressForm()
    }

    return render(request, 'store/checkout.html', context)

def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()

        total_price = cart_info['cart_total_price']
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Store Mono'
                    },
                    'unit_amount': int(total_price * 100)
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success_page')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )
        return redirect(session.url, 303)


def payment_success(request):
    customer = request.user.customer
    order = Order.objects.get(customer=customer, complete=False)
    order.complete = True
    order.save()



    # OrderProduct lar allaqachon mavjud bo‘ladi, shunchaki vaqt qo‘shiladi
    for item in order.orderproduct_set.all():
        item.date_ordered = timezone.now()
        item.save()

    return render(request, 'payment_success.html', {'order': order})


def success_page(request):
    user = request.user
    customer = Customer.objects.get(user=user)

    # Eng oxirgi buyurtmani olish
    last_order = Order.objects.filter(customer=customer).order_by('-created_at').first()

    if not last_order:
        return render(request, 'store/components/_message_for_success.html', {'message': 'Buyurtma topilmadi.'})

    ordered_products = OrderProduct.objects.filter(order=last_order)

    context = {
        'message': 'To‘lov muvaffaqiyatli amalga oshirildi!',
        'order': last_order,
        'ordered_products': ordered_products,
    }

    return render(request, 'store/components/_message_for_success.html', context)


def clear_cart(request):
    user_cart = CartAuthenticatedUser(request)
    order = user_cart.get_cart_info()['order']
    order_products = order.orderproduct_set.all()
    for order_product in order_products:
        quantity = order_product.quantity
        product = order_product.product
        order_product.delete()
        product.quantity += quantity
        product.delete()
    return redirect('cart')



def order_history(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(customer=user, complete=True).all()
    return render(request, 'store/_order_history.html', {'orders': orders})


class ContactCreateView(CreateView):
    """
    Contact form Class-based view
    CreateView automatically handles GET and POST methods
    """

    # Basic settings
    model = Contact
    form_class = ContactForm
    template_name = 'store/contact.html'
    success_url = reverse_lazy('contact')
    context_object_name = 'contact'

    def get_context_data(self, **kwargs):
        """
        Add extra context data to template
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Contact Us'
        context['page_description'] = 'Have questions? Get in touch with us!'
        context['recent_contacts'] = Contact.objects.filter(
            is_replied=False
        ).count()  # Unreplied messages count
        return context

    def form_valid(self, form):
        """Method that runs when form is filled correctly"""
        # Get data from form
        contact_data = form.cleaned_data

        # Add additional information
        form.instance.ip_address = self.get_client_ip()
        form.instance.user_agent = self.request.META.get('HTTP_USER_AGENT', '')

        # If user is logged in, save them too
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user

        # Save the form (this creates self.object)
        response = super().form_valid(form)

        # Send email notification
        self.send_notification_email(contact_data)

        # Success message
        messages.success(
            self.request,
            f"Thank you {contact_data['name']}! Your message has been sent successfully. "
            "We'll get back to you soon."
        )

        return response  # <- Bu muhim!

    def form_invalid(self, form):
        """
        Method that runs when form is filled incorrectly
        """
        messages.error(
            self.request,
            'There are errors in the form. Please check and try again.'
        )

        return super().form_invalid(form)

    def send_notification_email(self, contact_data):
        """
        Email sending function
        """
        try:
            # Email to admin
            admin_subject = f"New Contact Message: {contact_data['subject']}"
            admin_message = f"""
            New message received from website:

            Name: {contact_data['name']}
            Email: {contact_data['email']}
            Phone: {contact_data.get('phone', 'Not provided')}
            Subject: {contact_data['subject']}

            Message:
            {contact_data['message']}

            IP Address: {self.get_client_ip()}
            Time: {self.object.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            """

            send_mail(
                subject=admin_subject,
                message=admin_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            # Confirmation email to client
            client_subject = "Message Received - We'll Be In Touch"
            client_message = f"""
            Dear {contact_data['name']},

            Thank you for contacting us. We have received your message and will get back to you shortly.

            Message Details:
            Subject: {contact_data['subject']}
            Time: {self.object.created_at.strftime('%Y-%m-%d %H:%M:%S')}

            Best regards,
            The Team
            """

            send_mail(
                subject=client_subject,
                message=client_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[contact_data['email']],
                fail_silently=True,  # Don't throw error if client email fails
            )

        except Exception as e:
            # Continue even if email fails
            messages.warning(
                self.request,
                'Your message was saved, but there was an issue sending the email notification.'
            )

    def phone_validator(self, value):
        """Telefon raqamni tekshirish"""
        if value and not re.match(r'^\+?[0-9\s\-\(\)]{7,20}$', value):
            raise forms.ValidationError('Please enter a valid phone number')
        return value

    def get_client_ip(self):
        """
        Get client's IP address
        """
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def dispatch(self, request, *args, **kwargs):
        """
        Check before each request
        """
        # Rate limiting - prevent too many messages from one IP
        client_ip = self.get_client_ip()
        recent_contacts = Contact.objects.filter(
            ip_address=client_ip,
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).count()

        if recent_contacts >= 3:  # More than 3 messages in 5 minutes
            messages.error(request, 'Too many messages sent. Please wait a moment before trying again.')
            return redirect('contact')

        return super().dispatch(request, *args, **kwargs)




def create_shipping_address(request):
    if request.method == "POST":
        address = request.POST.get("address")
        city = request.POST.get("city")
        region = request.POST.get("region")
        phone = request.POST.get("phone")

        # Misol uchun: foydalanuvchi bilan bog‘liq customer va order ni olish
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.filter(customer=customer, complete=False).first()


        return redirect('success-page')  # Bu sizning muvaffaqiyat sahifangiz

    return render(request, "shipping_address.html")


