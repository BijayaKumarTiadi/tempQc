from django.urls import path
#Test Imports
from .views import *

# Working Imports
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema



urlpatterns = [
   
    path('login/token/refresh', 
         swagger_auto_schema(
             methods=['post'],  # Specify the method(s) for which the schema applies
             operation_summary="Refresh access token",
             operation_description="Refreshes the access token by exchanging a valid refresh token.",
             responses={200: "Success", 401: "Unauthorized"}
         )(TokenRefreshView.as_view()), 
         name='token_refresh'),

    #Login and Get Server
    path('', apipage, name='apipage'),
    path('login/geticompany', GetIcompanyId.as_view(), name='geticompany'),
    path('login', LoginApi.as_view(), name='login'),
    
    
    path('login/getdata', GetDataView.as_view(), name='get_data'),
    
    
    path('login/forgot-otp/', ForgotPasswordOTPView.as_view(), name='forgot-otp'),
    path('login/verify-forgot-otp/', VerifyForgotPasswordOTPView.as_view(), name='verify-forgot-otp'),
    path('login/update-password/', UpdatePasswordView.as_view(), name='update-password'),
    

    #After Login - Home Page API
    path('login/dashboard', Dashboard.as_view(), name='dashboard'),


]

