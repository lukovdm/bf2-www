from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import include, path, reverse
from django.utils import timezone

from events.models import Event, EventDate, Registration

# The events app is normally attached through a CMS apphook, mount it directly
# for the tests.
urlpatterns = [
    path("events/", include(("events.urls", "events"))),
]


def make_event(dates=None, **kwargs):
    """Create an event, by default with one date a week from now.

    ``dates`` is a list of (start, end) tuples or dicts with EventDate fields.
    """
    now = timezone.now()
    defaults = dict(
        name_en="Tournament",
        name_nl="Toernooi",
        location="Nijmegen",
        registration_start=now - timedelta(days=1),
        registration_end=now + timedelta(days=1),
    )
    defaults.update(kwargs)
    event = Event.objects.create(**defaults)
    if dates is None:
        dates = [(now + timedelta(days=7), now + timedelta(days=8))]
    for date in dates:
        if isinstance(date, tuple):
            date = dict(start=date[0], end=date[1])
        EventDate.objects.create(event=event, **date)
    return event


class EventModelTest(TestCase):
    def test_clean_with_missing_values(self):
        # clean() is called even when field validation already failed (#277)
        Event(name_en="a", name_nl="a", location="here").clean()
        EventDate(event=Event()).clean()

    def test_date_start_after_end(self):
        now = timezone.now()
        with self.assertRaises(ValidationError) as cm:
            EventDate(start=now, end=now - timedelta(hours=1)).clean()
        self.assertIn("start", cm.exception.message_dict)

    def test_registration_end_requires_start(self):
        event = Event(registration_end=timezone.now())
        with self.assertRaises(ValidationError) as cm:
            event.clean()
        self.assertIn("registration_start", cm.exception.message_dict)

    def test_registration_start_after_end(self):
        now = timezone.now()
        event = Event(registration_start=now, registration_end=now - timedelta(hours=1))
        with self.assertRaises(ValidationError) as cm:
            event.clean()
        self.assertIn("registration_end", cm.exception.message_dict)

    def test_limit(self):
        with self.assertRaises(ValidationError) as cm:
            Event(limit=0).clean()
        self.assertIn("limit", cm.exception.message_dict)

    def test_dates(self):
        now = timezone.now()
        event = make_event(
            dates=[
                (now + timedelta(days=3), now + timedelta(days=3, hours=2)),
                (now - timedelta(days=3), now - timedelta(days=3, hours=-2)),
                (now + timedelta(days=5), now + timedelta(days=6)),
            ]
        )
        starts = [date.start for date in event.sorted_dates]
        self.assertEqual(starts, sorted(starts))
        self.assertEqual(event.start_date, now - timedelta(days=3))
        self.assertEqual(event.end_date, now + timedelta(days=6))
        self.assertEqual(event.next_date.start, now + timedelta(days=3))
        self.assertEqual(event.upcoming_date_count, 2)

    def test_next_date_when_all_ended(self):
        now = timezone.now()
        event = make_event(dates=[(now - timedelta(days=2), now - timedelta(days=1))])
        self.assertEqual(event.next_date.start, now - timedelta(days=2))
        self.assertEqual(event.upcoming_date_count, 0)

    def test_upcoming_sorts_by_next_date(self):
        now = timezone.now()
        later = make_event(
            name_en="later",
            dates=[
                (now - timedelta(days=10), now - timedelta(days=9)),
                (now + timedelta(days=10), now + timedelta(days=11)),
            ],
        )
        sooner = make_event(
            name_en="sooner", dates=[(now + timedelta(days=5), now + timedelta(days=6))]
        )
        make_event(
            name_en="past", dates=[(now - timedelta(days=5), now - timedelta(days=4))]
        )
        self.assertEqual(list(Event.objects.upcoming()), [sooner, later])

    def test_ongoing_event_is_upcoming(self):
        now = timezone.now()
        event = make_event(dates=[(now - timedelta(hours=1), now + timedelta(hours=1))])
        self.assertEqual(list(Event.objects.upcoming()), [event])

    def test_default_registration_end_is_start_of_event(self):
        now = timezone.now()
        event = make_event(
            registration_start=now,
            registration_end=None,
            dates=[
                (now + timedelta(days=4), now + timedelta(days=4, hours=2)),
                (now + timedelta(days=2), now + timedelta(days=2, hours=2)),
            ],
        )
        event.save()
        self.assertEqual(event.registration_end, now + timedelta(days=2))

    def test_date_location(self):
        event = make_event()
        date = event.sorted_dates[0]
        self.assertEqual(date.location_or_default, "Nijmegen")
        date.location = "Arnhem"
        self.assertEqual(date.location_or_default, "Arnhem")


class EventAdminTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "pw")
        self.client.force_login(self.admin)

    def post_event(self, dates, **extra):
        data = {
            "name_en": "Admin event",
            "name_nl": "Admin evenement",
            "location": "Sportcentrum",
            "registration_set-TOTAL_FORMS": "0",
            "registration_set-INITIAL_FORMS": "0",
            "dates-TOTAL_FORMS": str(len(dates)),
            "dates-INITIAL_FORMS": "0",
            "dates-MIN_NUM_FORMS": "1",
            "dates-MAX_NUM_FORMS": "1000",
        }
        for i, (start, end) in enumerate(dates):
            data.update(
                {
                    f"dates-{i}-start_0": start.strftime("%Y-%m-%d"),
                    f"dates-{i}-start_1": start.strftime("%H:%M:%S"),
                    f"dates-{i}-end_0": end.strftime("%Y-%m-%d"),
                    f"dates-{i}-end_1": end.strftime("%H:%M:%S"),
                    f"dates-{i}-show_end": "on",
                }
            )
        data.update(extra)
        return self.client.post(reverse("admin:events_event_add"), data)

    def test_add_form(self):
        response = self.client.get(reverse("admin:events_event_add"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # The dates are shown above the other fields
        self.assertLess(
            content.index('id="dates-group"'), content.index('name="name_en"')
        )
        self.assertLess(
            content.index('name="name_en"'),
            content.index('id="registration_set-group"'),
        )
        # The registration opens now by default
        self.assertIsNotNone(
            response.context["adminform"].form.initial.get("registration_start")
        )
        # End of day shortcut for the time pickers (#276)
        self.assertContains(response, "admin-end-of-day.js")

    def test_add_event_without_dates(self):
        response = self.post_event([])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Event.objects.exists())
        formset = next(
            f.formset
            for f in response.context["inline_admin_formsets"]
            if f.formset.prefix == "dates"
        )
        self.assertTrue(formset.non_form_errors())

    def test_add_event_with_dates(self):
        start = timezone.localtime().replace(microsecond=0) + timedelta(days=3)
        response = self.post_event(
            [
                (start + timedelta(days=1), start + timedelta(days=1, hours=2)),
                (start, start + timedelta(hours=2)),
            ],
            registration_start_0=timezone.localtime().strftime("%Y-%m-%d"),
            registration_start_1="00:00:00",
        )
        self.assertEqual(response.status_code, 302)
        event = Event.objects.get()
        self.assertEqual(event.dates.count(), 2)
        # The registration closes when the event starts by default
        self.assertEqual(event.registration_end, start)

    def test_add_event_without_registration(self):
        start = timezone.localtime() + timedelta(days=3)
        response = self.post_event([(start, start + timedelta(hours=2))])
        self.assertEqual(response.status_code, 302)
        event = Event.objects.get()
        self.assertIsNone(event.registration_start)
        self.assertIsNone(event.registration_end)

    def test_date_start_after_end(self):
        start = timezone.localtime() + timedelta(days=3)
        response = self.post_event([(start, start - timedelta(hours=2))])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Event.objects.exists())

    def test_changelist(self):
        make_event()
        make_event(hidden=True)
        response = self.client.get(reverse("admin:events_event_changelist"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            reverse("admin:events_event_changelist") + "?hidden__exact=1&o=2"
        )
        self.assertEqual(response.status_code, 200)


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

    def test_registration_only_depends_on_registration_dates(self):
        # The event already started, but the registration is still open
        now = timezone.now()
        event = make_event(
            dates=[(now - timedelta(hours=1), now + timedelta(days=1))],
            registration_end=now + timedelta(hours=1),
        )
        self.client.post(reverse("events:register", args=[event.pk]))
        self.assertTrue(Registration.objects.filter(event=event).exists())

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


@override_settings(ROOT_URLCONF=__name__)
class EventICSTest(TestCase):
    def test_one_calendar_event_per_upcoming_date(self):
        now = timezone.now()
        make_event(
            name_en="Multi",
            location="Main field",
            dates=[
                dict(
                    start=now - timedelta(days=2),
                    end=now - timedelta(days=2, hours=-2),
                    label_en="Past day",
                ),
                dict(
                    start=now + timedelta(days=2),
                    end=now + timedelta(days=2, hours=2),
                    label_en="Day 1",
                ),
                dict(
                    start=now + timedelta(days=3),
                    end=now + timedelta(days=3, hours=2),
                    label_en="Day 2",
                    location="Other field",
                ),
            ],
        )
        make_event(name_en="Secret", hidden=True)
        content = self.client.get(reverse("events:ics")).content.decode()
        self.assertEqual(content.count("BEGIN:VEVENT"), 2)
        self.assertIn("Multi (Day 1)", content)
        self.assertIn("Multi (Day 2)", content)
        self.assertNotIn("Past day", content)
        self.assertIn("LOCATION:Main field", content)
        self.assertIn("LOCATION:Other field", content)
        self.assertNotIn("Secret", content)


class EventDatesMigrationTest(TransactionTestCase):
    """The old start and end date of an event become its first date."""

    before = [("events", "0016_alter_event_form_link")]
    after = [("events", "0017_event_dates")]

    def test_dates_are_copied(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.before)
        old_apps = executor.loader.project_state(self.before).apps
        OldEvent = old_apps.get_model("events", "Event")
        now = timezone.now()
        old = OldEvent.objects.create(
            name_en="Old",
            name_nl="Oud",
            location="Here",
            start_date=now,
            end_date=now + timedelta(hours=2),
            show_end_date=False,
        )

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.after)
        new_apps = executor.loader.project_state(self.after).apps
        NewEventDate = new_apps.get_model("events", "EventDate")
        date = NewEventDate.objects.get(event_id=old.pk)
        self.assertEqual(date.start, now)
        self.assertEqual(date.end, now + timedelta(hours=2))
        self.assertFalse(date.show_end)

        # Back to the latest state for the other tests
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())
