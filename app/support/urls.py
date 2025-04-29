from django.urls import path
from . import views

urlpatterns = [
    path('support/', views.SupportListView.as_view(), name='support-list'),
    path('support/<uuid:uid>/', views.SupportDetailView.as_view(),
         name='support-detail'),
    path('support/replies/list/<uuid:uid>/',
         views.SupportRepliesView.as_view(), name='support-replies'),
    path('support/create/', views.SupportCreateView.as_view(), name='support-create'),
    path('support/reply/<uuid:uid>/', views.SupportReplyCreateView.as_view(),
         name='support-reply-create'),
    path('support/<str:uid>/close/', views.close_ticket, name='close_ticket'),
]
