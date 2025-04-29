from django.urls import path
from . import views

urlpatterns = [
    path('kwai/campaign/', views.CampaignsNotInUseView.as_view(),
         name='campaigns_not_in_use'),
    path('kwai/', views.KwaiListView.as_view(), name='kwai_list'),
    path('kwai/<str:uid>/', views.KwaiDetailView.as_view(), name='kwai_detail'),
    path('kwai/multiple-delete/', views.KwaiDetailView.as_view(),
         name='kwai_multiple_delete'),

    path('kwai-campaigns/', views.KwaiOverview.as_view(),
         name='kwai-campaign-list'),

]
