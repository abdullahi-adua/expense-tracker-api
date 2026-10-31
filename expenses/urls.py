from django.urls import path
from . import views, auth_views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .throttles import LoginRateThrottle, RefreshRateThrottle
router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"transactions", views.TransactionViewSet, basename="transaction")


class ThrottledLoginView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]

class ThrottledRefreshView(TokenRefreshView):
    throttle_classes = [RefreshRateThrottle]

urlpatterns = router.urls + [
    path("auth/register/", auth_views.RegisterAPIView.as_view(), name="register"),
    path("auth/login/", ThrottledLoginView.as_view(), name= "login"),
    path("auth/refresh/", ThrottledRefreshView.as_view(), name= "refresh")
    ]