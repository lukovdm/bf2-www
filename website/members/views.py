from cms.models import settingmodels
from django.contrib.auth.views import PasswordResetConfirmView
from django.views.generic import FormView

from members.forms import BecomeAMemberForm
from members.models import MemberSettings
from members.tokens import AccountActivationTokenGenerator


class BecomeAMemberView(FormView):
    template_name = "members/become_a_member.html"
    form_class = BecomeAMemberForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context["privacyFile"] = MemberSettings.objects.first().privacyFile
        return context


class PasswordSetView(PasswordResetConfirmView):
    template_name = "members/passwerd_set.html"
    token_generator = AccountActivationTokenGenerator()
    success_url = "/"
