from django.urls import path
from .views import ProductDetail_PageLoad,GetRawMaterial,OurSpecification_PageLoad,PaperBoard

urlpatterns = [
    path('product-details/', ProductDetail_PageLoad.as_view(), name='product-details-api'),
    path('get-raw-material/', GetRawMaterial.as_view(), name='get_raw_material'),
    path('our-specification/', OurSpecification_PageLoad.as_view(), name='process-all-data'),
    path('paperboard/', PaperBoard.as_view(), name='paperboard'),
]