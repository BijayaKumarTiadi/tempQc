from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
#imports views
from estimation.views import EstimationHome,papermaster_boards
from estimation.views import EstProcessInputDetailList




urlpatterns = [
    #Required 
    path('', EstimationHome.as_view(), name='estimation'),
    path('/boards', papermaster_boards.as_view(), name='papermaster_boards'),
    path('/process', EstProcessInputDetailList.as_view(), name='EstProcessInputDetailList'),
    # path('/api3', EstimationHome.as_view(), name='estimation'),
    # path('/api4', EstimationHome.as_view(), name='estimation'),
    # path('/api6', EstimationHome.as_view(), name='estimation'),
    # path('/api5', EstimationHome.as_view(), name='estimation'),
]

