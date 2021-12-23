from django.urls import path

from committees.views import CommitteeListView, CommitteeDetailView

urlpatterns = [
    path("", CommitteeListView.as_view(), name="list"),
    path("<int:pk>/", CommitteeDetailView.as_view(), name="detail"),
]
