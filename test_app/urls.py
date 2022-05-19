from django.urls import path
from .views import (
    NotificationListView,
    NotificationDeleteView,
    TopicListView,
    TopicDetailView,
    TopicUpdateView,
    TopicDeleteView,
    UserTopicListView,
    StudentRequestListView,
    StudentRequestListView2,
    StudentRequestDeleteView,
    StudentRequestUpdateView
)
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='topics', permanent=False)),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/delete/', NotificationDeleteView.as_view(), name='notification-delete'),
    path('topic/', TopicListView.as_view(), name='topics'),
    path('topic/new/', views.create_topic, name='topic-create'),
    path('topic/<int:pk>', TopicDetailView.as_view(), name='topic-detail'),
    path('topic/<int:pk>/update', TopicUpdateView.as_view(), name='topic-update'),
    path('topic/<int:pk>/delete', TopicDeleteView.as_view(), name='topic-delete'),
    path('user/<str:username>/topics', UserTopicListView.as_view(), name='user-topics'),
    path('topic/<int:pk>/create_request', views.create_studentRequest, name='create-request'),
    path('student_requests/', StudentRequestListView.as_view(), name='student-requests'),
    path('student_requests/<int:pk>/respond/', views.create_requestResponse, name='request-response'),
    path('student_requests/<int:pk>/delete', StudentRequestDeleteView.as_view(), name='request-delete'),
    path('requests/', StudentRequestListView2.as_view(), name='requests-student'),
    path('requests/<int:pk>/update', StudentRequestUpdateView.as_view(), name='request-update'),
    path('student_requests/<int:pk>/decline', views.decline_studentRequest, name='request-decline'),
    path('topic/<int:pk>/create_request_no_topic', views.create_studentRequestNoTopic, name='create-request-no-topic'),
    path('search_venues', views.search_venues, name='search-venues')
]