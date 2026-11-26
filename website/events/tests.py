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


class RegistrationExportTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "pw")
        self.event = make_event(name_en="Hat tournament", cost_en="10", cost_nl="10")
        self.other = make_event(name_en="Pub quiz")
        for i, event in enumerate([self.event, self.event, self.other]):
            user = User.objects.create_user(
                f"user{i}", f"user{i}@example.com", "pw", first_name=f"Name{i}"
            )
            Registration.objects.create(event=event, user=user, has_payed=i == 0)

    def rows(self, response):
        import csv
        import io

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        content = response.content.decode("utf-8-sig")
        return list(csv.reader(io.StringIO(content)))

    def test_export_button(self):
        self.client.force_login(self.admin)
        change = self.client.get(
            reverse("admin:events_event_change", args=[self.event.pk])
        )
        url = reverse("admin:events_event_registrations_csv", args=[self.event.pk])
        self.assertContains(change, url)
        rows = self.rows(self.client.get(url))
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            rows[1][:4], ["Hat tournament", "Name0", "", "user0@example.com"]
        )
        self.assertEqual(rows[1][6], "yes")
        self.assertEqual(rows[2][6], "no")

    def test_export_action(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("admin:events_event_changelist"),
            {
                "action": "export_registrations",
                "_selected_action": [self.event.pk, self.other.pk],
            },
        )
        rows = self.rows(response)
        self.assertEqual(
            [row[0] for row in rows[1:]], ["Hat tournament"] * 2 + ["Pub quiz"]
        )

    def test_export_requires_permission(self):
        staff = User.objects.create_user("staff", "s@example.com", "pw", is_staff=True)
        self.client.force_login(staff)
        url = reverse("admin:events_event_registrations_csv", args=[self.event.pk])
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 302)


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


class FakeGoogleForms:
    """In memory replacement of GoogleFormsClient."""

    def __init__(self):
        self.forms = {}  # published id -> {"id", "question", "codes"}
        self.calls = 0

    def add_form(self, published, form_id="form-1", question=None):
        self.forms[published] = {"id": form_id, "question": question, "codes": set()}
        return self.forms[published]

    def find_form(self, link):
        from events.google_forms import published_id

        self.calls += 1
        form = self.forms.get(published_id(link))
        return form["id"] if form else None

    def _by_id(self, form_id):
        return next(f for f in self.forms.values() if f["id"] == form_id)

    def ensure_code_question(self, form_id):
        self.calls += 1
        form = self._by_id(form_id)
        form["question"] = form["question"] or "00a1b2c3"
        return form["question"]

    def submitted_codes(self, form_id, question_id):
        self.calls += 1
        return set(self._by_id(form_id)["codes"])


FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSdemo/viewform?embedded=true"


class GoogleFormsTestMixin:
    """Enable the Google Forms connection with a fake client."""

    def setUp(self):
        super().setUp()
        from unittest import mock

        self.google = FakeGoogleForms()
        settings = override_settings(GOOGLE_SERVICE_ACCOUNT_FILE="/fake/key.json")
        settings.enable()
        self.addCleanup(settings.disable)
        patches = [
            mock.patch("events.google_forms.get_client", return_value=self.google),
            mock.patch(
                "events.google_forms.service_account_email",
                return_value="website@bf2.iam.gserviceaccount.com",
            ),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)


class GoogleFormsHelpersTest(TestCase):
    def test_published_id(self):
        from events.google_forms import published_id

        self.assertEqual(published_id(FORM_LINK), "1FAIpQLSdemo")
        self.assertIsNone(published_id("https://example.com/form"))

    def test_prefilled_link(self):
        from events.google_forms import entry_id, prefilled_link

        self.assertEqual(entry_id("00a1b2c3"), str(0xA1B2C3))
        link = prefilled_link(FORM_LINK, entry_id("00a1b2c3"), "ABCD-EFGH")
        self.assertTrue(
            link.startswith("https://docs.google.com/forms/d/e/1FAIpQLSdemo/viewform?")
        )
        self.assertIn(f"entry.{0xA1B2C3}=ABCD-EFGH", link)
        self.assertIn("usp=pp_url", link)
        self.assertIn("embedded=true", link)

    def test_registration_codes(self):
        import re

        from events.models import make_registration_code

        codes = {make_registration_code() for _ in range(200)}
        self.assertEqual(len(codes), 200)
        for code in codes:
            self.assertRegex(code, r"^[A-Z2-9]{4}-[A-Z2-9]{4}$")
            self.assertIsNone(re.search(r"[01IO]", code))


class GoogleFormsClientTest(TestCase):
    """The parsing of the API responses, with recorded example responses."""

    def client_with(self, responses):
        from unittest import mock

        from events.google_forms import GoogleFormsClient

        client = GoogleFormsClient()
        client._request = mock.Mock(side_effect=responses)
        return client

    def test_find_form_over_pages(self):
        client = self.client_with(
            [
                {"files": [{"id": "a"}], "nextPageToken": "next"},
                {"responderUri": "https://docs.google.com/forms/d/e/other/viewform"},
                {"files": [{"id": "b"}]},
                {
                    "responderUri": "https://docs.google.com/forms/d/e/1FAIpQLSdemo/viewform"
                },
            ]
        )
        self.assertEqual(client.find_form(FORM_LINK), "b")

    def test_find_form_not_shared(self):
        client = self.client_with([{"files": []}])
        self.assertIsNone(client.find_form(FORM_LINK))

    def test_ensure_code_question_adds_question(self):
        question = {
            "title": "Registration code",
            "questionItem": {"question": {"questionId": "0abc1234"}},
        }
        client = self.client_with(
            [
                {"items": [{"title": "Name", "questionItem": {"question": {}}}]},
                {},  # batchUpdate
                {"items": [question]},
            ]
        )
        self.assertEqual(client.ensure_code_question("form"), "0abc1234")
        method, url = client._request.call_args_list[1].args
        self.assertEqual(method, "POST")
        self.assertTrue(url.endswith(":batchUpdate"))

    def test_ensure_code_question_existing(self):
        client = self.client_with(
            [
                {
                    "items": [
                        {
                            "title": "Registration code",
                            "questionItem": {"question": {"questionId": "0abc1234"}},
                        }
                    ]
                }
            ]
        )
        self.assertEqual(client.ensure_code_question("form"), "0abc1234")
        self.assertEqual(client._request.call_count, 1)

    def test_submitted_codes(self):
        client = self.client_with(
            [
                {
                    "responses": [
                        {
                            "answers": {
                                "0abc1234": {
                                    "textAnswers": {
                                        "answers": [{"value": " abcd-efgh "}]
                                    }
                                }
                            }
                        },
                        {"answers": {}},
                    ],
                    "nextPageToken": "next",
                },
                {
                    "responses": [
                        {
                            "answers": {
                                "0abc1234": {
                                    "textAnswers": {"answers": [{"value": "JKLM-NPQR"}]}
                                }
                            }
                        }
                    ]
                },
            ]
        )
        self.assertEqual(
            client.submitted_codes("form", "0abc1234"), {"ABCD-EFGH", "JKLM-NPQR"}
        )

    def test_not_configured(self):
        from events.google_forms import GoogleFormsClient, GoogleFormsError

        with self.assertRaises(GoogleFormsError):
            GoogleFormsClient().find_form(FORM_LINK)


class FormSyncTest(GoogleFormsTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.event = make_event(form_link=FORM_LINK)
        self.user = User.objects.create_user("user", "user@example.com", "pw")
        self.registration = Registration.objects.create(
            event=self.event, user=self.user
        )

    def test_not_shared(self):
        from events.form_sync import connect_form, form_status_text

        connect_form(self.event)
        self.assertFalse(self.event.form_connected)
        self.assertIn(
            "website@bf2.iam.gserviceaccount.com", self.event.google_form_error
        )
        self.assertIn("Not connected", form_status_text(self.event))

    def test_connect_adds_question_and_prefills_code(self):
        from events.form_sync import connect_form

        self.google.add_form("1FAIpQLSdemo")
        connect_form(self.event)
        self.assertTrue(self.event.form_connected)
        link = self.event.form_link_for(self.registration)
        self.assertIn(f"={self.registration.code}", link)

    def test_sync_marks_submitted_registrations(self):
        from events.form_sync import sync_form

        form = self.google.add_form("1FAIpQLSdemo")
        other = Registration.objects.create(
            event=self.event, user=User.objects.create_user("other")
        )
        form["codes"].add(self.registration.code)
        sync_form(self.event, force=True)
        self.registration.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(self.registration.form_status, Registration.FORM_VERIFIED)
        self.assertIsNotNone(self.registration.form_completed_at)
        self.assertTrue(other.form_pending)

    def test_sync_is_throttled(self):
        from events.form_sync import sync_form

        self.google.add_form("1FAIpQLSdemo")
        sync_form(self.event)
        calls = self.google.calls
        sync_form(self.event)
        self.assertEqual(self.google.calls, calls)
        sync_form(self.event, force=True)
        self.assertGreater(self.google.calls, calls)

    def test_sync_without_configuration(self):
        from events.form_sync import sync_form

        with override_settings(GOOGLE_SERVICE_ACCOUNT_FILE=""):
            sync_form(self.event, force=True)
        self.assertEqual(self.google.calls, 0)

    def test_event_without_form(self):
        event = make_event()
        registration = Registration.objects.create(event=event, user=self.user)
        self.assertFalse(registration.form_pending)


class FormAdminTest(GoogleFormsTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "pw")
        self.client.force_login(self.admin)
        self.event = make_event(form_link=FORM_LINK)

    def test_status_shown_in_admin(self):
        response = self.client.get(
            reverse("admin:events_event_change", args=[self.event.pk])
        )
        self.assertContains(response, "Google Form connection")
        self.assertContains(response, "website@bf2.iam.gserviceaccount.com")

    def test_status_below_form_link(self):
        response = self.client.get(
            reverse("admin:events_event_change", args=[self.event.pk])
        )
        content = response.content.decode()
        link = content.index('name="form_link"')
        status = content.index("Google Form connection")
        self.assertLess(link, status)
        # No other field in between
        self.assertNotIn('name="', content[link + 20 : status])

    def test_form_link_help_shows_share_address(self):
        response = self.client.get(reverse("admin:events_event_add"))
        self.assertContains(response, "Add collaborators")
        self.assertContains(
            response, "<strong>website@bf2.iam.gserviceaccount.com</strong>", html=True
        )

    @override_settings(GOOGLE_SERVICE_ACCOUNT_FILE="")
    def test_form_link_help_without_connection(self):
        from unittest import mock

        with mock.patch("events.google_forms.service_account_email", return_value=None):
            response = self.client.get(reverse("admin:events_event_add"))
        self.assertContains(response, "Paste the share link of the form")
        self.assertNotContains(response, "Add collaborators")

    def test_csv_has_form_status_and_code(self):
        import csv
        import io

        form = self.google.add_form("1FAIpQLSdemo")
        done = Registration.objects.create(
            event=self.event, user=User.objects.create_user("a", first_name="Done")
        )
        Registration.objects.create(
            event=self.event, user=User.objects.create_user("b", first_name="Todo")
        )
        form["codes"].add(done.code)
        response = self.client.get(
            reverse("admin:events_event_registrations_csv", args=[self.event.pk])
        )
        rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
        by_name = {row[1]: row for row in rows[1:]}
        self.assertEqual(by_name["Done"][7], "filled in (checked with Google)")
        self.assertEqual(by_name["Done"][8], done.code)
        self.assertEqual(by_name["Todo"][7], "not filled in")
