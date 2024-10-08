from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
#imports views
from estimation.views import EstimationHome,papermaster_boards
from estimation.views import EstProcessInputDetailList
from estimation.views import ProcessInputView
from estimation.views import Costsheet
from estimation.views import EstNewQuoteListCreateView
from estimation.views import PaperGridQtyAPIView




urlpatterns = [
    #Required 
    path('', EstimationHome.as_view(), name='estimation'),
    path('/boards', papermaster_boards.as_view(), name='papermaster_boards'),
    path('/process', EstProcessInputDetailList.as_view(), name='EstProcessInputDetailList'),
    path('/processinput', ProcessInputView.as_view(), name='ProcessInputView'),
    path('/costsheet', Costsheet.as_view(), name='Costsheet'),
    path('/estimations', EstNewQuoteListCreateView.as_view(), name='estimations'),
    path('/papergrid', PaperGridQtyAPIView.as_view(), name='papergrid_qty'),
    # path('/api4', EstimationHome.as_view(), name='estimation'),
    # path('/api6', EstimationHome.as_view(), name='estimation'),
    # path('/api5', EstimationHome.as_view(), name='estimation'),
]

