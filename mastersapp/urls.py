from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TextMatterCheckingViewSet,PageLoadDropdown,ColorcheckingreportAPIView

router = DefaultRouter()
router.register(r'textmatterchecking', TextMatterCheckingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('page-load-dropdown/', PageLoadDropdown.as_view(), name='page-load-dropdown'),
    # URL for listing all reports and creating a new report
    path('colorcheckingreport/', ColorcheckingreportAPIView.as_view(), name='colorcheckingreport-list-create'),
    # URL for retrieving, updating, and deleting a specific report by primary key
    path('colorcheckingreport/<int:pk>/', ColorcheckingreportAPIView.as_view(), name='colorcheckingreport-detail'),
]
