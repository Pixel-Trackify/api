from django.urls import path
from . import views

urlpatterns = [
    path('support/', views.SupportListView.as_view(), name='support-list'),
     path('support/replies/list/<uuid:uid>/',
     views.SupportRepliesView.as_view(), name='support-replies'),
    path('support/create/', views.SupportCreateView.as_view(), name='support-create'),
    path('support/reply/<uuid:uid>/', views.SupportReplyCreateView.as_view(),
         name='support-reply-create'),
]
