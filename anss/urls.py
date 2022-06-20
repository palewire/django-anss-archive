from django.urls import path

from anss import views

urlpatterns = [
    path("feed/latest.json", views.LatestFeedView.as_view()),
    path("feed/list.json", views.FeedListView.as_view()),
]
