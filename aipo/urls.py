from django.urls import path
from .views import PDFUploadView

urlpatterns = [
    path('', PDFUploadView.as_view(), name='pdf-upload'),
]