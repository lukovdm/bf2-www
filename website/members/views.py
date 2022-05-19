from django.contrib.auth.views import PasswordResetConfirmView
from django.views.generic import FormView
from django.views.decorators.debug import sensitive_post_parameters

from members.forms import BecomeAMemberForm, ActivateAccountForm
from members.models import MemberSettings
from members.tokens import default_activate_token_generator


class BecomeAMemberView(FormView):
    template_name = "members/become_a_member.html"
    form_class = BecomeAMemberForm
    success_url = "/"

    @sensitive_post_parameters("password")
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
