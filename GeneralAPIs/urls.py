from django.urls import path
from .views import DropDownView

urlpatterns = [
    path('dropdown/', DropDownView.as_view(), name='dropdown-view'),
]
