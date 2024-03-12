from django.urls import path
from .views import GetDataView, LoginApi, apipage
from .views import CustomUserLoginView


#For swagger api documentation
from django.urls import re_path
from rest_framework import permissions
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
    path('', apipage, name='apipage'),
    path('login/', CustomUserLoginView.as_view(), name='user-login'),
    path('login-view/', LoginApi.as_view(), name='login-view'),
    path('getdata/', GetDataView.as_view(), name='get_data'),



    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]

