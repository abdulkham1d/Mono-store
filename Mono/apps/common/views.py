from django.views.generic import ListView

from .models import *


class ProductListView(ListView):
    model = Product
    context_object_name = 'categories'
    extra_context = {
        'title': 'MONO - Minimalist Shopping',
    }

    template_name = 'common/product_list.html'

