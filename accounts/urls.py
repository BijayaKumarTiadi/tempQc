from django.urls import path
#Test Imports
from .views import GetDataView, LoginApi, apipage

# Working Imports
from .views import Dashboard
from .views import CustomUserLoginView


#For swagger api documentation
from django.urls import re_path
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="SmartMIS-Backend",
        default_version='v1',
        description="RenukaSoftech Django Rest Framework API Documentation",
        terms_of_service="https://www.renukasoftech.com/terms/",
        contact=openapi.Contact(email="contact@renukasoftech.com"),
        license=openapi.License(name="License Name"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    #Required 
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    #Login and Get Server
    path('', apipage, name='apipage'),
    path('login', CustomUserLoginView.as_view(), name='user-login'),
    path('login-view', LoginApi.as_view(), name='login-view'),
    path('getdata', GetDataView.as_view(), name='get_data'),

    #After Login - Home Page API
    path('dashboard', Dashboard.as_view(), name='dashboard'),


    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]

