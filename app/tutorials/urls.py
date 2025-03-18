from django.urls import path
from . import views

urlpatterns = [
    path('tutoriais/', views.TutorialListView.as_view(),
         name='tutorial-list-create'),
    path('tutoriais/create/', views.TutorialCreateView.as_view(),
         name='tutorial-create'),
    path('tutoriais/<int:pk>/',
         views.TutorialRetrieveUpdateDestroyView.as_view(), name='tutorial-detail'),
]
