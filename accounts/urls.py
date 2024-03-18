from django.urls import path
#Test Imports
from .views import *

# Working Imports
from .views import Dashboard
from .views import CustomUserLoginView
from rest_framework_simplejwt.views import TokenRefreshView




urlpatterns = [
    #Required 
    path('settings/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    #Login and Get Server
    path('', apipage, name='apipage'),
    path('settings/geticomany', GetIcompanyId.as_view(), name='geticomany'),
    path('settings/login', CustomUserLoginView.as_view(), name='user-login'),
    path('settings/login-view', LoginApi.as_view(), name='login-view'),
    path('settings/settingsgetdata', GetDataView.as_view(), name='get_data'),
    
    
    path('settings/forgot-otp/', ForgotPasswordOTPView.as_view(), name='forgot-otp'),
    path('settings/verify-forgot-otp/', VerifyForgotPasswordOTPView.as_view(), name='verify-forgot-otp'),
    # path('settings/update-password/', UpdatePasswordView.as_view(), name='update-password'),
    

    #After Login - Home Page API
    path('dashboard', Dashboard.as_view(), name='dashboard'),



]

