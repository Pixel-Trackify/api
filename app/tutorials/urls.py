from django.urls import path
from . import views

urlpatterns = [
    path('tutoriais/', views.TutorialListCreateView.as_view(),
         name='tutorial-list-create'),
    path('tutoriais/<int:pk>/',
         views.TutorialRetrieveUpdateDestroyView.as_view(), name='tutorial-detail'),
]
