from django.urls import path
#Test Imports
from .views import GetDataView, GetIcompanyId, LoginApi, apipage

# Working Imports
from .views import Dashboard
from .views import CustomUserLoginView
from rest_framework_simplejwt.views import TokenRefreshView




urlpatterns = [
    #Required 
    path('login/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    #Login and Get Server
    path('', apipage, name='apipage'),
    path('geticomany', GetIcompanyId.as_view(), name='geticomany'),
    path('login', CustomUserLoginView.as_view(), name='user-login'),
    path('login-view', LoginApi.as_view(), name='login-view'),
    path('getdata', GetDataView.as_view(), name='get_data'),

    #After Login - Home Page API
    path('dashboard', Dashboard.as_view(), name='dashboard'),



]

