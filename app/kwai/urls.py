from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()
router.register(r'kwai', views.KwaiViewSet, basename='kwai')

urlpatterns = [
    path('kwai/campaign/', views.CampaignsNotInUseView.as_view(),
         name='campaigns_not_in_use'),


    path('dashboard-campaigns/', views.Dashboard_campaigns.as_view(),
         name='dashboard-campaign-list'),

] + router.urls
