from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from estimation.views import EstimationHome




urlpatterns = [
    #Required 
    path('', EstimationHome.as_view(), name='estimation'),
]

