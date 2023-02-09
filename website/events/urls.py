from django.urls import path

from events.views import (
    EventListView,
    EventDetailView,
    EventRegisterView,
    EventUnregisterView,
    EventFormView,
    EventICSView,
)

urlpatterns = [
    path("", EventListView.as_view(), name="list"),
    path("events.ics", EventICSView.as_view(), name="ics"),
    path("<int:pk>/", EventDetailView.as_view(), name="detail"),
    path("<int:pk>/register/", EventRegisterView.as_view(), name="register"),
    path("<int:pk>/form", EventFormView.as_view(), name="form"),
    path("<int:pk>/unregister/", EventUnregisterView.as_view(), name="unregister"),
]
