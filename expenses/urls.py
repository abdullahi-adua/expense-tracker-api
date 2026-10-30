from django.urls import path
from . import views, auth_views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"transactions", views.TransactionViewSet, basename="transaction")



urlpatterns = router.urls + [
    path("auth/register/", auth_views.RegisterAPIView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name= "login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name= "refresh")
    ]