"""RenukaSoft URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from .views import home_page

#For swagger api documentation
from django.urls import re_path
from rest_framework import permissions
from django.conf.urls.static import static
from django.conf import settings

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
    # url='/swagger/openapi.json', # we will add it later

    permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path("",home_page),
    path("api/v1/",include('accounts.urls')),
    path("api/v1/qm",include('estimation.urls')),
    path("api/v1/om",include('ordermanagement.urls')),
    path("api/v1/Genral/", include('GeneralAPIs.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
