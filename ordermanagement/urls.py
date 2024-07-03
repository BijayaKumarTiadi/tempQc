from django.urls import path
#AIPO Views imports
from .views import ProcessPDFView, SaveResponseView
from .views import GetCompanyFormatsView

#Order Management Imports
from .views import SeriesView 
from .views import ClientDataView 
from .views import ProductDetailsView 
from .views import EstimatedProductView 
from .views import ItemSpecView 
from .views import RateListView 
from .views import SaveWithSeriesView 
from .views import WOCreateView 
from .views import WoListAPIView
from .views import WoJobListAPIView

urlpatterns = [

    #Order Management - AIPO URLS
    path('/aipo/process-pdf/', ProcessPDFView.as_view(), name='process_pdf'),
    path('/aipo/save/', SaveResponseView.as_view(), name='save_response'),
    path('/aipo/templates/', GetCompanyFormatsView.as_view(), name='get_company_formats'),


    #Order Management - Dashboard URLS
    path('/Workorder/', SeriesView.as_view(), name='Workorder'), # view create update delete 
    path('/Workorder/client-data', ClientDataView.as_view(), name='client-data'),
    path('/Workorder/product-by-fp/', ProductDetailsView.as_view(), name='product-details'),
    path('/Workorder/product-by-estimation/', EstimatedProductView.as_view(), name='estimated-product-details'),
    path('/Workorder/item-spec/', ItemSpecView.as_view(), name='item-spec'),
    path('/Workorder/ratelist/', RateListView.as_view(), name='RateListView'),
    path('/Workorder/save/', WOCreateView.as_view(), name='save'),
    # path('/Workorder/save/', SaveWithSeriesView.as_view(), name='save'),
    path('/SoSearch/', WoListAPIView.as_view(), name='so-search'),
    path('/SoJobList/', WoJobListAPIView.as_view(), name='so-job-list'),

    # path('/Workorder/status/', Workorder.as_view(), name='Workorder'), # approve  reject normal , table item_WODetail col - approved



]
