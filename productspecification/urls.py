from django.urls import path
from .views import ProductDetail,GetRawMaterial,OurSpecification,PaperBoard

urlpatterns = [
    path('product-details/', ProductDetail.as_view(), name='product-details-api'),
    path('our-specification/', OurSpecification.as_view(), name='our_specification-api'),
    path('get-raw-material/', GetRawMaterial.as_view(), name='get-raw-material-api'),
]