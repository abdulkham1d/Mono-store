from django.urls import path

from .views import *

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('category/<slug:slug>/', CategoryListView.as_view(), name='category_detail'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('save_review/<int:product_id>/', save_review, name='save_review'),
    path('subcategory/<slug:slug>/', SubCategoryProductsView.as_view(), name='subcategory_products'),
    path('delete_review/<int:review_id>/', delete_review, name='delete_review'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('search/', search_results, name='search'),
    path('user_profile/', user_profile, name='user_pofile'),
    path('add_favourite/<slug:product_slug>', save_favourite_products, name='add_favourite'),
    path('my_favourite/', FavouriteProductsView.as_view(), name='my_favourite'),
    path('cart/', cart, name='cart'),
    path('to_cart/<int:product_id>/<str:action>/', to_cart, name='to_cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment/', create_checkout_session, name='payment'),
    path('success/', payment_success, name='success'),
    path('success_page/', success_page, name='success_page'),
    path('clear_cart/', clear_cart, name='clear_cart'),
    path('contact/', ContactCreateView.as_view(), name='contact'),
    # path('order_history/', order_history, name='order_history'),

]
