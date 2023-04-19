import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetConfirmView
from django.views.generic import DetailView, ListView, UpdateView, FormView
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from members.forms import BecomeAMemberForm, ActivateAccountForm
from members.models import MemberSettings, Member
from members.tokens import default_activate_token_generator


class MemberListView(LoginRequiredMixin, ListView):
    model = Member
    paginate_by = 20

    def get_queryset(self):
        members = super().get_queryset()
        query = self.request.GET.get('q')
        members = members.filter(user__is_active=True).order_by("user__first_name")
        if query:
            return members.filter(user__first_name__icontains=query)
        return members
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['pages'] = range(1, context['page_obj'].paginator.num_pages + 1)
        return context


class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "committee_memberships"
        ] = self.object.user.committeemembership_set.order_by("since").all()
        context["board_memberships"] = self.object.boardmembership_set.order_by(
            "board__start"
        ).all()
        context["today"] = datetime.datetime.today()
        return context


class MemberEditView(LoginRequiredMixin, UpdateView):
    model = Member
    fields = (
        "profile_picture",
        "nickname",
        "display_name",
        "bio",
        "gender",
        "pronouns",
        "preferred_language",
    )

    def get_object(self, queryset=None):
        return self.request.user.member


class BecomeAMemberView(FormView):
    template_name = "members/become_a_member.html"
    form_class = BecomeAMemberForm
    success_url = "/"

    @method_decorator(sensitive_post_parameters("password"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["privacyFile"] = MemberSettings.objects.first().privacyFile
        return context


class PasswordSetView(PasswordResetConfirmView):
    template_name = "members/passwerd_set.html"
    token_generator = default_activate_token_generator
    success_url = "/"
    form_class = ActivateAccountForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["privacyFile"] = MemberSettings.objects.first().privacyFile
        if self.user:
            context["user"] = self.user
        return context
