from django.urls import path
from .views import KwaiOverview

urlpatterns = [
    path('kwai-campaigns/', KwaiOverview.as_view(),
         name='kwai-campaign-list'),

]
