from django.urls import path
from .views import *

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
]
