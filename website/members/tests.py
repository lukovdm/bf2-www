from django.test import TestCase
from django.urls import reverse

from members.forms import BecomeAMemberForm
from members.models import MemberSettings


class BecomeAMemberFormTest(TestCase):
    def test_other_club_no_is_false(self):
        form = BecomeAMemberForm(data={"other_club": "false"})
        form.is_valid()
        self.assertIs(form.cleaned_data.get("other_club"), False)

    def test_other_club_yes_is_true(self):
        form = BecomeAMemberForm(data={"other_club": "true"})
        form.is_valid()
        self.assertIs(form.cleaned_data.get("other_club"), True)


class BecomeAMemberViewTest(TestCase):
    def setUp(self):
        MemberSettings.objects.create()

    def test_values_are_kept_after_validation_error(self):
        response = self.client.post(
            reverse("become-a-member"),
            {
                "firstname": "Alex",
                "lastname": "Frisbee",
                "birthday": "not a date",
                "city": "Nijmegen",
                "remarks": "Hello there",
                "other_club": "true",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Alex"')
        self.assertContains(response, 'value="Frisbee"')
        self.assertContains(response, 'value="not a date"')
        self.assertContains(response, 'value="Nijmegen"')
        self.assertContains(response, "Hello there</textarea>")
