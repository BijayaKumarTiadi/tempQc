from django.urls import path, re_path
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
from .views import WoListView
from .views import CompanyListView
from .views import WoRegisterView
from .views import PrintPIDataView

urlpatterns = [

    #Order Management - Dashboard URLS
    path('/series', SeriesView.as_view(), name='proformainvoice'), # Completed without names
    path('/client-data', ClientDataView.as_view(), name='client-data'), # Completed without names
    path('/product-by-fp/', ProductDetailsView.as_view(), name='product-details'), # Completed without names
    # path('/product-by-estimation/', EstimatedProductView.as_view(), name='estimated-product-details'),
    # path('/item-spec/', ItemSpecView.as_view(), name='item-spec'),
    # path('/ratelist/', RateListView.as_view(), name='RateListView'),
    path('/save/', WOCreateView.as_view(), name='save'),

    path('/soSearch/', WoListAPIView.as_view(), name='so-search'), #Script Incomplete ~@Rajat
    path('/soJoblist/', WoJobListAPIView.as_view(), name='so-job-list'), #Script Incomplete  ~@Rajat
    path('/piList/', WoListView.as_view(), name='pi-list'), #Completed all with names
    path('/companyList/', CompanyListView.as_view(), name='Company-list'), #Completed all with names
    # path('/register/', WoRegisterView.as_view(), name='wo-register'),

    path('/printdata/', PrintPIDataView.as_view(), name='pi-printView'),

]
