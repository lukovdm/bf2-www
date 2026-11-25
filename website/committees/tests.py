import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from committees.models import Committee, CommitteeMembership


class CommitteeRightsTest(TestCase):
    def setUp(self):
        self.webmasters = Committee.objects.create(
            name_en="Webmasters", name_nl="Webmasters", email="web@example.com"
        )
        self.staff_committee = Committee.objects.create(
            name_en="Board", name_nl="Bestuur", email="b@example.com", is_staff=True
        )

    def test_membership_adds_to_group(self):
        user = User.objects.create_user("a")
        CommitteeMembership.objects.create(user=user, committee=self.webmasters)
        self.assertIn(user, self.webmasters.perm_group.user_set.all())

    def test_editing_one_membership_keeps_others_in_group(self):
        manual = User.objects.create_user("manual")
        self.webmasters.perm_group.user_set.add(manual)
        user = User.objects.create_user("a")
        membership = CommitteeMembership.objects.create(
            user=user, committee=self.webmasters
        )
        membership.chair = True
        membership.save()
        self.assertIn(manual, self.webmasters.perm_group.user_set.all())

    def test_superuser_keeps_staff(self):
        admin = User.objects.create_superuser("admin", "admin@example.com", "pw")
        CommitteeMembership.objects.create(user=admin, committee=self.webmasters)
        admin.refresh_from_db()
        self.assertTrue(admin.is_staff)

    def test_staff_committee_grants_and_revokes_staff(self):
        user = User.objects.create_user("a")
        membership = CommitteeMembership.objects.create(
            user=user, committee=self.staff_committee, since=datetime.date(2020, 1, 1)
        )
        user.refresh_from_db()
        self.assertTrue(user.is_staff)

        membership.until = datetime.date(2021, 1, 1)
        membership.save()
        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertNotIn(user, self.staff_committee.perm_group.user_set.all())
        self.assertTrue(membership.rights_changes)

    def test_until_in_future_is_rejected(self):
        membership = CommitteeMembership(
            user=User.objects.create_user("a"),
            committee=self.webmasters,
            until=datetime.date.today() + datetime.timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            membership.clean()
