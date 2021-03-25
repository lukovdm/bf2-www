from django.contrib.auth.views import PasswordResetConfirmView
from django.views.generic import FormView

from members.forms import BecomeAMemberForm
from members.tokens import AccountActivationTokenGenerator


class BecomeAMemberView(FormView):
    template_name = "members/become_a_member.html"
    form_class = BecomeAMemberForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PasswordSetView(PasswordResetConfirmView):
    template_name = "members/passwerd_set.html"
    token_generator = AccountActivationTokenGenerator()
    success_url = "/"
