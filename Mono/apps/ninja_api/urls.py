from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from ninja import NinjaAPI


from apps.ninja_api.routes.categories import router as category_router
from apps.ninja_api.routes.products import router as product_router
from apps.ninja_api.routes.reviews import router as review_router
from apps.ninja_api.routes.shipping_adress import router as shipping_adress_router

api = NinjaAPI(
    title="Mono Store API",  # Bu qoyilmasa defoult Ninja Api bolib chiqadi! Ozimmi Saytimga moslangan!
    description="Mahsulotlar bilan ishlovchi REST API",
    version="2.0.0"  # Versiya xohlagancha bo'lishi mumkin
)

api.add_router("products/", product_router)
api.add_router("categories/", category_router)
api.add_router("reviews/", review_router)
api.add_router('shipping-adresses/', shipping_adress_router)


urlpatterns = [
    path("", api.urls),  # MUHIM: bu yo‘l orqali Ninja API ulanadi

]


