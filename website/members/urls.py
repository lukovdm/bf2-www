from django.urls import path

from members.views import MemberListView, MemberDetailView, MemberEditView

urlpatterns = [
    path("", MemberListView.as_view(), name="list"),
    path("<int:pk>/", MemberDetailView.as_view(), name="detail"),
    path("edit/", MemberEditView.as_view(), name="edit"),
]
