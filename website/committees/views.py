from django.contrib.auth.models import User
from django.utils import timezone
from django.views.generic import ListView, DetailView

from committees.models import Committee


class CommitteeListView(ListView):
    model = Committee

    def get_queryset(self):
        committees = super().get_queryset()
        committees = committees.filter(active=True).order_by(
            "name_en"
        )  # TODO make multilingual
        return committees


class CommitteeDetailView(DetailView):
    model = Committee

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["committee_memberships"] = (
            self.object.committeemembership_set.exclude(until__lte=timezone.now())
            .order_by("since")
            .select_related("user__member")
        )

        # There is a bug in the reverse such that we can't get the member pk in the url
        context["user_member_table"] = {u.pk: u.member.pk for u in User.objects.all()}
        return context
