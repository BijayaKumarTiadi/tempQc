from django.urls import path
#AIPO Views imports
from .views import ProcessPDFView, SaveResponseView
from .views import GetCompanyFormatsView

#Order Management Imports
from .views import Workorder 
from .views import SeriesView 

urlpatterns = [

    #Order Management - AIPO URLS
    path('/aipo/process-pdf/', ProcessPDFView.as_view(), name='process_pdf'),
    path('/aipo/save/', SaveResponseView.as_view(), name='save_response'),
    path('/aipo/templates/', GetCompanyFormatsView.as_view(), name='get_company_formats'),


    #Order Management - Dashboard URLS
    path('/Workorder/', SeriesView.as_view(), name='Workorder'), # view create update delete 

    path('/Workorder/register/', Workorder.as_view(), name='Workorder'), # for detail view
    path('/Workorder/status/', Workorder.as_view(), name='Workorder'), # approve  reject normal , table item_WODetail col - approved



]
