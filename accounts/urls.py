from django.urls import path
from .views import LoginApi, apipage
from .views import CustomUserLoginView

urlpatterns = [
    path('', apipage, name='apipage'),
    path('login/', CustomUserLoginView.as_view(), name='user-login'),
    path('login-view/', LoginApi.as_view(), name='login-view'),

]

