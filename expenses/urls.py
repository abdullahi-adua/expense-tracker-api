from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"transactions", views.TransactionViewSet, basename="transaction")

urlpatterns = router.urls