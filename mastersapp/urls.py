from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TextMatterCheckingViewSet

router = DefaultRouter()
router.register(r'textmatterchecking', TextMatterCheckingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
