from django.views.generic import FormView

from members.forms import BecomeAMemberForm


class BecomeAMemberView(FormView):
    template_name = "members/become_a_member.html"
    form_class = BecomeAMemberForm
    success_url = "/"   

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    