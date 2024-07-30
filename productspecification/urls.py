from django.urls import path
from .views import PageLoadAPI

urlpatterns = [
    path('pageload/', PageLoadAPI.as_view(), name='pageload-api'),
]
