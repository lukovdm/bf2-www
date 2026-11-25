from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import include, path, reverse
from django.utils import timezone

from events.models import Event, Registration

# The events app is normally attached through a CMS apphook, mount it directly
# for the tests.
urlpatterns = [
    path("events/", include(("events.urls", "events"))),
]


def make_event(**kwargs):
    now = timezone.now()
    defaults = dict(
        name_en="Tournament",
        name_nl="Toernooi",
        location="Nijmegen",
        start_date=now + timedelta(days=7),
        end_date=now + timedelta(days=8),
        registration_start=now - timedelta(days=1),
        registration_end=now + timedelta(days=1),
    )
    defaults.update(kwargs)
    return Event.objects.create(**defaults)


class EventCleanTest(TestCase):
    def test_missing_dates_do_not_crash(self):
        event = Event(name_en="a", name_nl="a", location="here")
        with self.assertRaises(ValidationError) as cm:
            event.full_clean()
        self.assertIn("start_date", cm.exception.message_dict)
        self.assertIn("end_date", cm.exception.message_dict)

    def test_clean_with_missing_values(self):
        # clean() is called even when field validation already failed
        Event(name_en="a", name_nl="a", location="here").clean()

    def test_start_after_end(self):
        now = timezone.now()
        event = Event(start_date=now, end_date=now - timedelta(hours=1))
        with self.assertRaises(ValidationError) as cm:
            event.clean()
        self.assertIn("start_date", cm.exception.message_dict)

    def test_only_one_registration_date(self):
        now = timezone.now()
        event = Event(start_date=now, end_date=now, registration_start=now)
        with self.assertRaises(ValidationError) as cm:
            event.clean()
        self.assertIn("registration_end", cm.exception.message_dict)

    def test_multiple_errors_reported_together(self):
        now = timezone.now()
        event = Event(
            start_date=now,
            end_date=now - timedelta(hours=1),
            registration_start=now,
            registration_end=now - timedelta(hours=1),
            limit=0,
        )
        with self.assertRaises(ValidationError) as cm:
            event.clean()
        self.assertEqual(
            set(cm.exception.message_dict),
            {
                "start_date",
                "end_date",
                "registration_start",
                "registration_end",
                "limit",
            },
        )


class EventAdminTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "pw")
        self.client.force_login(self.admin)

    def test_add_event_without_dates_shows_errors(self):
        response = self.client.post(
            reverse("admin:events_event_add"),
            {
                "name_en": "No dates",
                "name_nl": "Geen data",
                "location": "Nijmegen",
                "show_end_date": "on",
                "registration_set-TOTAL_FORMS": "0",
                "registration_set-INITIAL_FORMS": "0",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("start_date", response.context["adminform"].form.errors)
        self.assertFalse(Event.objects.exists())


@override_settings(ROOT_URLCONF=__name__)
class EventRegistrationViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "user@example.com", "pw")
        self.client.force_login(self.user)

    def test_register(self):
        event = make_event()
        self.client.post(reverse("events:register", args=[event.pk]))
        self.assertTrue(
            Registration.objects.filter(event=event, user=self.user).exists()
        )

    def test_register_event_without_registrations(self):
        event = make_event(registration_start=None, registration_end=None)
        self.client.post(reverse("events:register", args=[event.pk]))
        self.assertFalse(Registration.objects.exists())

    def test_register_full_event(self):
        event = make_event(limit=1)
        other = User.objects.create_user("other", "other@example.com", "pw")
        Registration.objects.create(event=event, user=other)
        self.client.post(reverse("events:register", args=[event.pk]))
        self.assertFalse(Registration.objects.filter(user=self.user).exists())

    def test_unregister_after_close_keeps_registration(self):
        now = timezone.now()
        event = make_event(
            registration_start=now - timedelta(days=2),
            registration_end=now - timedelta(days=1),
        )
        Registration.objects.create(event=event, user=self.user)
        self.client.post(reverse("events:unregister", args=[event.pk]))
        self.assertTrue(
            Registration.objects.filter(event=event, user=self.user).exists()
        )

    def test_unregister_when_not_registered(self):
        event = make_event()
        response = self.client.post(reverse("events:unregister", args=[event.pk]))
        self.assertRedirects(
            response, event.get_absolute_url(), fetch_redirect_response=False
        )
