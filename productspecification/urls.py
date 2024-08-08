from django.urls import path
from .views import PageLoadAPI,GetRawMaterial,ProcessAllData,PaperBoard

urlpatterns = [
    path('pageload/', PageLoadAPI.as_view(), name='pageload-api'),
    path('get-raw-material/', GetRawMaterial.as_view(), name='get_raw_material'),
    path('process-all-data/', ProcessAllData.as_view(), name='process-all-data'),
    path('paperboard/', PaperBoard.as_view(), name='paperboard'),
]