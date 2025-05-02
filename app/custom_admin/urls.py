from rest_framework.routers import DefaultRouter
from .views import AdminDashboardViewSet

router = DefaultRouter()
router.register('admin-dashboard', AdminDashboardViewSet,
                basename='admin-dashboard')

urlpatterns = router.urls
