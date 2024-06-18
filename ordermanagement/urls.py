from django.urls import path
#AIPO Views imports
from .views import ProcessPDFView, SaveResponseView
from .views import GetCompanyFormatsView

#Order Management Imports
from .views import SeriesView 
from .views import ClientDataView 
from .views import ProductDetailsView 

urlpatterns = [

    #Order Management - AIPO URLS
    path('/aipo/process-pdf/', ProcessPDFView.as_view(), name='process_pdf'),
    path('/aipo/save/', SaveResponseView.as_view(), name='save_response'),
    path('/aipo/templates/', GetCompanyFormatsView.as_view(), name='get_company_formats'),


    #Order Management - Dashboard URLS
    path('/Workorder/', SeriesView.as_view(), name='Workorder'), # view create update delete 
    path('/Workorder/client-data', ClientDataView.as_view(), name='client-data'),
    path('/Workorder/product-details/', ProductDetailsView.as_view(), name='product-details'),

    # path('/Workorder/register/', Workorder.as_view(), name='Workorder'), # for detail view
    # path('/Workorder/status/', Workorder.as_view(), name='Workorder'), # approve  reject normal , table item_WODetail col - approved



]
