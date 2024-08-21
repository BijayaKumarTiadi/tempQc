from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TextMatterCheckingViewSet,PageLoadDropdown,ColorcheckingreportAPIView

router = DefaultRouter()
router.register(r'textmatterchecking', TextMatterCheckingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('page-load-dropdown/', PageLoadDropdown.as_view(), name='page-load-dropdown'),
    path('colorcheckingreport/', ColorcheckingreportAPIView.as_view(), name='colorcheckingreport-list-create'),
    path('colorcheckingreport/<int:pk>/', ColorcheckingreportAPIView.as_view(), name='colorcheckingreport-detail'),
]
