from django.urls import path
#Test Imports
from .views import GetDataView, GetIcompanyId, LoginApi, apipage

# Working Imports
from .views import Dashboard
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema



urlpatterns = [
    #Required 
    # path('login/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
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
    path('login/geticomany', GetIcompanyId.as_view(), name='geticomany'),
    path('login', LoginApi.as_view(), name='login'),
    
    
    path('login/getdata', GetDataView.as_view(), name='get_data'),

    #After Login - Home Page API
    path('login/dashboard', Dashboard.as_view(), name='dashboard'),



]

