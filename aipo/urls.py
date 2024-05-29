from django.urls import path
from .views import ProcessPDFView, SaveResponseView
from .views import GetCompanyFormatsView


urlpatterns = [
    path('/process-pdf/', ProcessPDFView.as_view(), name='process_pdf'),
    path('/save/', SaveResponseView.as_view(), name='save_response'),
    path('/templates/', GetCompanyFormatsView.as_view(), name='get_company_formats'),

]
