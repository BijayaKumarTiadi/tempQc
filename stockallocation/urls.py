from django.urls import path, re_path
#Stock Allocation Views imports
from .views import ProcessPayloadView



urlpatterns = [

    #Stock Allocation - URLS
    path('/stockallocation/wo-allocation', ProcessPayloadView.as_view(), name='wo-allocation'),


]
