from rest_framework.routers import DefaultRouter
from .views import TutorialViewSet

router = DefaultRouter()
router.register(r'tutorials', TutorialViewSet, basename='tutorial')

urlpatterns = router.urls
