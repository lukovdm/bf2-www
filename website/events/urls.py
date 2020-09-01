from django.urls import path

from events.views import EventListView, EventDetailView, EventRegisterView

urlpatterns = [
    path("", EventListView.as_view(), name="list"),
    path("<int:pk>/", EventDetailView.as_view(), name="detail"),
    path("<int:pk>/register/", EventRegisterView.as_view(), name="register"),
]
