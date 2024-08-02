from django.urls import path
from .views import PageLoadAPI,MachineList

urlpatterns = [
    path('pageload/', PageLoadAPI.as_view(), name='pageload-api'),
    path('machine_list/', MachineList.as_view(), name='process-wise-machine-list'),
]


# MachineList