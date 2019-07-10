from anss import views
from django.urls import path


urlpatterns = [
    path('feed/latest.json', views.LatestFeedView.as_view()),
    path('feed/list.json', views.FeedListView.as_view()),
]
