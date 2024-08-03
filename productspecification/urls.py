from django.urls import path
from .views import PageLoadAPI,MachineList,GetRawMaterial

urlpatterns = [
    path('pageload/', PageLoadAPI.as_view(), name='pageload-api'),
    path('machine-list/', MachineList.as_view(), name='process-wise-machine-list'),
    path('get-raw-material/', GetRawMaterial.as_view(), name='get_raw_material'),
]