"""Integration tests for the whole site.

These tests exercise the CMS, the apphooks, the admin and the third party
packages together. They are meant to catch breakage when upgrading Django,
django CMS or any of the other dependencies.
"""

import csv
import datetime
import io
import re
from datetime import timedelta

from cms.api import add_plugin, create_page, create_page_content
from cms.utils.apphook_reload import reload_urlconf
from cms.utils.permissions import set_current_user
from cms.models import PageContent, Placeholder
from django.contrib import admin
from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse, NoReverseMatch
from django.utils import timezone, translation
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_mail_template.models import Configuration, MailTemplate
from djangocms_versioning.models import Version

from boards.models import Board, BoardMembership
from committees.models import Committee, CommitteeMembership
from events.models import Event, EventDate, Registration
from members.models import Member, MemberSettings
from members.tokens import default_activate_token_generator
from website.models import Slideshow

STATIC_SETTINGS = dict(
    # Do not compile sass during tests, it is slow and not what we test here
    SASS_PROCESSOR_ENABLED=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
    # The CMS caches rendered placeholders, which leaks between tests
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}},
)


def make_member(username, email=None, active=True, **kwargs):
    user = User.objects.create_user(
        username,
        email or f"{username}@example.com",
        "a-Strong-passw0rd",
        first_name=username.capitalize(),
        last_name="Tester",
        is_active=active,
    )
    defaults = dict(
        birthday=datetime.date(2000, 1, 1),
        gender=Member.OTHER,
        phone_number="0612345678",
        street_address="Street 1",
        postcode="1234 AB",
        city="Nijmegen",
        student_type=Member.RU,
        sports_card_number="s1234567",
        other_club=False,
        google_email=f"{username}@gmail.com",
        preferred_language="en",
    )
    defaults.update(kwargs)
    Member.objects.create(user=user, **defaults)
    return user


def make_mail_templates(*processes):
    for process in processes:
        template = MailTemplate.objects.create(
            title=process,
            to="secretary@example.com",
            from_email="no-reply@example.com",
            subject=f"{process} {{name}}",
            body="<p>Hello {name} {link}</p>",
        )
        Configuration.objects.update_or_create(
            process=process, defaults={"mail_template": template}
        )


def make_event(**kwargs):
    now = timezone.now()
    defaults = dict(
        name_en="Tournament",
        name_nl="Toernooi",
        location="Nijmegen",
        cost_en="5 euro",
        cost_nl="5 euro",
        registration_start=now - timedelta(days=1),
        registration_end=now + timedelta(days=1),
    )
    defaults.update(kwargs)
    start = defaults.pop("start_date", now + timedelta(days=7))
    end = defaults.pop("end_date", now + timedelta(days=8))
    event = Event.objects.create(**defaults)
    EventDate.objects.create(event=event, start=start, end=end)
    return event


@override_settings(**STATIC_SETTINGS)
class SiteTestCase(TestCase):
    """Sets up a small CMS site with all apphooks attached."""

    @classmethod
    def setUpTestData(cls):
        set_current_user(None)
        cls.admin = User.objects.create_superuser(
            "admin", "admin@example.com", "a-Strong-passw0rd"
        )
        MemberSettings.objects.create()

        cls.home = cls.create_published_page("Home", "fullpage_cms.html")
        cls.home.set_as_homepage()
        cls.add_text(cls.home, "content top", "<p>Welcome to the frisbee club</p>")

        cls.about = cls.create_published_page(
            "About", "page_cms.html", in_navigation=True
        )
        cls.add_text(cls.about, "content", "<p>About our club</p>")

        cls.events_page = cls.create_published_page(
            "Events",
            "page_cms.html",
            apphook="EventApphook",
            apphook_namespace="events",
        )
        cls.publish_translation(cls.events_page, "nl", "Evenementen")
        cls.committees_page = cls.create_published_page(
            "Committees",
            "page_cms.html",
            apphook="CommitteeApphook",
            apphook_namespace="committees",
        )
        cls.members_page = cls.create_published_page(
            "Members",
            "page_cms.html",
            apphook="MemberApphook",
            apphook_namespace="members",
        )

    @classmethod
    def create_published_page(cls, title, template, **kwargs):
        page = create_page(
            title,
            template,
            "en",
            created_by=cls.admin,
            parent=getattr(cls, "home", None),
            **kwargs,
        )
        content = PageContent.admin_manager.get(page=page, language="en")
        Version.objects.get_for_content(content).publish(cls.admin)
        return page

    @classmethod
    def publish_translation(cls, page, language, title):
        content = create_page_content(language, title, page, created_by=cls.admin)
        Version.objects.get_for_content(content).publish(cls.admin)

    @classmethod
    def placeholder(cls, page, slot):
        content = PageContent.admin_manager.get(page=page, language="en")
        placeholder = content.get_placeholders().filter(slot=slot).first()
        if placeholder is None:
            placeholder = Placeholder.objects.create(slot=slot, source=content)
        return placeholder

    @classmethod
    def add_text(cls, page, slot, body):
        return add_plugin(cls.placeholder(page, slot), "TextPlugin", "en", body=body)

    def setUp(self):
        # The CMS keeps the current user in a thread local, reset it so users
        # from previous tests do not leak into signals of this test
        set_current_user(None)
        # Make sure the apphook urls are (re)loaded for the pages above
        reload_urlconf()
        translation.activate("en")

    def tearDown(self):
        translation.deactivate()


class CMSPageTest(SiteTestCase):
    def test_home_page(self):
        response = self.client.get("/en/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to the frisbee club")

    def test_root_redirects_to_language(self):
        response = self.client.get("/")
        self.assertIn(response.status_code, (200, 302))

    def test_text_page(self):
        response = self.client.get(self.about.get_absolute_url("en"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About our club")

    def test_menu_shows_page(self):
        response = self.client.get("/en/")
        self.assertContains(response, self.about.get_absolute_url("en"))

    def test_page_as_admin_with_toolbar(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.about.get_absolute_url("en") + "?toolbar_on")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cms-toolbar")

    def test_edit_mode(self):
        self.client.force_login(self.admin)
        content = PageContent.admin_manager.get(page=self.about, language="en")
        from cms.toolbar.utils import get_object_edit_url

        # Editing a published version first creates a draft, then redirects
        response = self.client.get(get_object_edit_url(content), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About our club")

    def test_dutch_fallback(self):
        response = self.client.get("/nl/")
        self.assertIn(response.status_code, (200, 302))

    def test_404(self):
        response = self.client.get("/en/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)

    def test_sitemap(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "become-a-member")

    def test_slideshow_context(self):
        response = self.client.get("/en/")
        self.assertEqual(response.context["active_index"], 0)
        self.assertEqual(list(response.context["slideshow"]), [])


class StaticAliasTest(SiteTestCase):
    """The footers are static aliases since django CMS 5."""

    def make_footer(self):
        from djangocms_alias.models import Alias, AliasContent, Category

        category = Category.objects.create(name="Static Alias")
        alias = Alias.objects.create(
            category=category,
            static_code="footer 1",
            creation_method=Alias.CREATION_BY_TEMPLATE,
        )
        content = AliasContent.objects.with_user(self.admin).create(
            alias=alias, name="footer 1", language="en"
        )
        add_plugin(content.placeholder, "TextPlugin", "en", body="<p>Footer text</p>")
        Version.objects.get_for_content(content).publish(self.admin)
        return content

    def test_footer_on_pages(self):
        self.make_footer()
        self.assertContains(self.client.get("/en/"), "Footer text")

    def test_edit_view(self):
        # The alias edit view renders the alias in the site template, which
        # was empty because the template block did not exist (see
        # website/templates/djangocms_alias/base.html)
        from cms.toolbar.utils import get_object_edit_url

        content = self.make_footer()
        self.client.force_login(self.admin)
        response = self.client.get(get_object_edit_url(content), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cms-aliases-detail")
        self.assertContains(response, "Footer text")


class PluginTest(SiteTestCase):
    def test_current_board_plugin(self):
        board = Board.objects.create(
            start=datetime.date.today() - timedelta(days=10),
            end=datetime.date.today() + timedelta(days=300),
        )
        BoardMembership.objects.create(
            board=board,
            member=make_member("chair").member,
            function_en="Chair",
            function_nl="Voorzitter",
        )
        add_plugin(self.placeholder(self.about, "content"), "CurrentBoardPlugin", "en")
        response = self.client.get(self.about.get_absolute_url("en"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chair")

    def test_only_logged_in_plugin(self):
        parent = add_plugin(
            self.placeholder(self.about, "content"), "OnlyLoggedInPlugin", "en"
        )
        add_plugin(
            self.placeholder(self.about, "content"),
            "TextPlugin",
            "en",
            target=parent,
            body="<p>Secret members info</p>",
        )
        url = self.about.get_absolute_url("en")
        self.assertNotContains(self.client.get(url), "Secret members info")
        self.client.force_login(make_member("someone"))
        self.assertContains(self.client.get(url), "Secret members info")

    def test_frontend_plugins_render(self):
        placeholder = self.placeholder(self.about, "content")
        add_plugin(
            placeholder,
            "AlertPlugin",
            "en",
            config={
                "alert_context": "info",
                "alert_dismissible": False,
                "attributes": {},
                "tag_type": "div",
            },
        )

        response = self.client.get(self.about.get_absolute_url("en"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "alert-info")


class EventPagesTest(SiteTestCase):
    def setUp(self):
        super().setUp()
        self.event = make_event()
        self.user = make_member("player")

    def test_event_list(self):
        response = self.client.get(reverse("events:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tournament")

    def test_event_list_logged_in(self):
        Registration.objects.create(event=self.event, user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(reverse("events:list"))
        self.assertEqual(response.status_code, 200)

    def test_event_detail(self):
        response = self.client.get(self.event.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nijmegen")
        self.assertContains(response, "5 euro")

    def test_event_detail_dutch(self):
        with translation.override("nl"):
            url = self.event.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toernooi")

    def test_event_detail_as_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.event.get_absolute_url() + "?toolbar_on")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cms-toolbar")

    def test_register_and_unregister(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("events:register", args=[self.event.pk]))
        self.assertRedirects(
            response, self.event.get_absolute_url(), fetch_redirect_response=False
        )
        registration = Registration.objects.get(event=self.event, user=self.user)
        self.assertIs(registration.has_payed, False)

        detail = self.client.get(self.event.get_absolute_url())
        self.assertContains(detail, "Player")

        self.client.post(reverse("events:unregister", args=[self.event.pk]))
        self.assertFalse(Registration.objects.filter(user=self.user).exists())

    def test_register_requires_login(self):
        response = self.client.post(reverse("events:register", args=[self.event.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response["Location"])
        self.assertFalse(Registration.objects.exists())

    def test_register_with_form_redirects_to_form(self):
        self.event.form_link = "https://docs.google.com/forms/d/e/abc/viewform?"
        self.event.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse("events:register", args=[self.event.pk]))
        self.assertRedirects(
            response,
            reverse("events:form", args=[self.event.pk]),
            fetch_redirect_response=False,
        )
        form = self.client.get(reverse("events:form", args=[self.event.pk]))
        self.assertEqual(form.status_code, 200)
        self.assertContains(form, "embedded=true")

    def test_form_view_without_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("events:form", args=[self.event.pk]))
        self.assertEqual(response.status_code, 404)

    def test_ics(self):
        response = self.client.get(reverse("events:ics"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/calendar")
        self.assertIn(b"BEGIN:VCALENDAR", response.content)
        self.assertIn(b"Tournament", response.content)

    def test_event_with_multiple_dates(self):
        now = timezone.now()
        event = make_event(name_en="Weekend tournament", location="Main field")
        EventDate.objects.create(
            event=event,
            start=now + timedelta(days=9),
            end=now + timedelta(days=9, hours=8),
            label_en="Finals",
            label_nl="Finales",
            location="Stadium",
        )
        response = self.client.get(self.event.get_absolute_url())
        self.assertNotContains(response, "event-date-card")
        response = self.client.get(event.get_absolute_url())
        self.assertContains(response, "event-date-card", count=2)
        self.assertContains(response, "Finals")
        self.assertContains(response, "Stadium")
        self.assertContains(response, "2 dates")
        listing = self.client.get(reverse("events:list"))
        self.assertContains(listing, "+1 more date")

    def test_past_events_hidden(self):
        make_event(
            name_en="Old event",
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=9),
        )
        response = self.client.get(reverse("events:list"))
        self.assertNotContains(response, "Old event")


class HiddenEventTest(SiteTestCase):
    def setUp(self):
        super().setUp()
        self.event = make_event(name_en="Secret meeting", hidden=True)
        self.member = make_member("member")
        self.staff = make_member("staffmember")
        self.staff.is_staff = True
        self.staff.save()

    def test_not_shown_to_visitors_and_members(self):
        for user in (None, self.member):
            if user:
                self.client.force_login(user)
            self.assertNotContains(
                self.client.get(reverse("events:list")), "Secret meeting"
            )
            self.assertEqual(
                self.client.get(self.event.get_absolute_url()).status_code, 404
            )
            response = self.client.post(
                reverse("events:register", args=[self.event.pk])
            )
            self.assertIn(response.status_code, (302, 404))
        self.assertFalse(Registration.objects.exists())

    def test_shown_greyed_out_to_staff(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("events:list"))
        self.assertContains(response, "Secret meeting")
        self.assertContains(response, "event-hidden")
        self.assertContains(response, "Hidden")
        response = self.client.get(self.event.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This event is hidden")

    def test_not_in_ics(self):
        self.assertNotIn(
            b"Secret meeting", self.client.get(reverse("events:ics")).content
        )


class CommitteePagesTest(SiteTestCase):
    def setUp(self):
        super().setUp()
        self.committee = Committee.objects.create(
            name_en="Tournament committee",
            name_nl="Toernooicommissie",
            email="toco@example.com",
        )
        self.inactive = Committee.objects.create(
            name_en="Old committee",
            name_nl="Oude commissie",
            email="old@example.com",
            active=False,
        )
        CommitteeMembership.objects.create(
            user=make_member("toco"), committee=self.committee, chair=True
        )

    def test_list(self):
        response = self.client.get(reverse("committees:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tournament committee")
        self.assertNotContains(response, "Old committee")

    def test_detail(self):
        response = self.client.get(self.committee.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tournament committee")
        self.assertNotContains(response, "toco@example.com")

        self.client.force_login(make_member("visitor"))
        response = self.client.get(self.committee.get_absolute_url())
        self.assertContains(response, "toco@example.com")

    def test_detail_as_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.committee.get_absolute_url() + "?toolbar_on")
        self.assertEqual(response.status_code, 200)


class MemberPagesTest(SiteTestCase):
    def setUp(self):
        super().setUp()
        self.user = make_member("alice", nickname="Ace")
        self.inactive = make_member("bob", active=False)

    def test_list_requires_login(self):
        response = self.client.get(reverse("members:list"))
        self.assertEqual(response.status_code, 302)

    def test_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("members:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertNotContains(response, "Bob")

    def test_search(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("members:list") + "?q=ali")
        self.assertContains(response, "Alice")

    def test_detail(self):
        committee = Committee.objects.create(
            name_en="Fun", name_nl="Plezier", email="fun@example.com"
        )
        CommitteeMembership.objects.create(user=self.user, committee=committee)
        self.client.force_login(self.user)
        response = self.client.get(self.user.member.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")

    def test_edit(self):
        self.client.force_login(self.user)
        url = reverse("members:edit")
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(
            url,
            {
                "nickname": "Flash",
                "display_name": Member.FIRST_NAME_NICKNAME,
                "bio": "I like frisbee",
                "gender": Member.OTHER,
                "pronouns": "they/them",
                "preferred_language": "nl",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.member.refresh_from_db()
        self.assertEqual(self.user.member.nickname, "Flash")
        self.assertEqual(self.user.member.name(), 'Alice "Flash"')


class AuthTest(SiteTestCase):
    def test_login_page(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_and_logout(self):
        make_member("carol")
        response = self.client.post(
            reverse("login"),
            {"username": "carol", "password": "a-Strong-passw0rd"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)
        self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_sign_out_from_menu(self):
        self.client.force_login(make_member("erik"))
        page = self.client.get("/en/").content.decode()
        logout = reverse("logout")
        # Since Django 5 the logout view only accepts POST, so it must be a form
        self.assertNotIn(f'href="{logout}"', page)
        self.assertRegex(page, rf'<form[^>]*method="post"[^>]*action="{logout}"')
        response = self.client.post(logout)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_password_reset(self):
        make_member("dave")
        self.assertEqual(self.client.get(reverse("password_reset")).status_code, 200)
        response = self.client.post(
            reverse("password_reset"), {"email": "dave@example.com"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

    def test_set_language(self):
        response = self.client.post(
            reverse("set_language"), {"language": "nl", "next": "/en/"}
        )
        self.assertEqual(response.status_code, 302)


class BecomeAMemberTest(SiteTestCase):
    data = {
        "firstname": "Eve",
        "lastname": "Thrower",
        "birthday": "01/02/2001",
        "gender": Member.WOMAN,
        "pronouns": "",
        "phone_number": "0612345678",
        "street_address": "Street 2",
        "postcode": "1234 AB",
        "city": "Nijmegen",
        "student_type": Member.HAN,
        "sports_card_number": "S12345678",
        "preferred_language": "en",
        "other_club": "false",
        "email": "eve@example.com",
        "google_email": "eve@gmail.com",
        "password": "a-Strong-passw0rd",
        "data_registration": "on",
        "remarks": "",
    }

    def test_page(self):
        response = self.client.get(reverse("become-a-member"))
        self.assertEqual(response.status_code, 200)

    def test_sign_up(self):
        make_mail_templates(
            "new_member", "new_member_confirmation_en", "new_member_confirmation_nl"
        )
        response = self.client.post(reverse("become-a-member"), self.data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email="eve@example.com")
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password("a-Strong-passw0rd"))
        self.assertEqual(user.member.sports_card_number, "s12345678")
        self.assertEqual(user.member.birthday, datetime.date(2001, 2, 1))
        self.assertIs(user.member.other_club, False)

        recipients = [m.to for m in mail.outbox]
        self.assertIn(["secretary@example.com"], recipients)
        self.assertIn(["eve@example.com"], recipients)

    def test_sign_up_without_templates_mails_admins(self):
        with self.settings(ADMINS=[("Web", "web@example.com")]):
            self.client.post(reverse("become-a-member"), self.data)
        self.assertTrue(User.objects.filter(email="eve@example.com").exists())
        self.assertTrue(Configuration.objects.filter(process="new_member").exists())
        self.assertTrue(any("web@example.com" in m.to for m in mail.outbox))

    def test_existing_email(self):
        make_member("eve", email="eve@example.com")
        response = self.client.post(reverse("become-a-member"), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)

    def test_weak_password(self):
        response = self.client.post(
            reverse("become-a-member"), {**self.data, "password": "123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("password", response.context["form"].errors)

    def test_birthday_in_future(self):
        response = self.client.post(
            reverse("become-a-member"), {**self.data, "birthday": "01/01/2999"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("birthday", response.context["form"].errors)


class AccountActivationTest(SiteTestCase):
    def setUp(self):
        super().setUp()
        self.user = make_member("frank", active=False)

    def activation_url(self, token=None):
        return reverse(
            "activate-account",
            kwargs={
                "uidb64": urlsafe_base64_encode(force_bytes(self.user.pk)),
                "token": token
                or default_activate_token_generator.make_token(self.user),
            },
        )

    def test_token(self):
        token = default_activate_token_generator.make_token(self.user)
        self.assertTrue(default_activate_token_generator.check_token(self.user, token))
        self.assertFalse(
            default_activate_token_generator.check_token(self.user, "abc-def")
        )

    def test_activate_account(self):
        response = self.client.get(self.activation_url())
        self.assertEqual(response.status_code, 302)
        set_password_url = response["Location"]
        self.assertEqual(self.client.get(set_password_url).status_code, 200)
        response = self.client.post(
            set_password_url,
            {
                "new_password1": "an-Other-passw0rd",
                "new_password2": "an-Other-passw0rd",
                "data_registration": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("an-Other-passw0rd"))

    def test_invalid_token(self):
        response = self.client.get(self.activation_url("abc-def"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["validlink"])


class AdminTest(SiteTestCase):
    """Smoke test every admin page, these break easily on upgrades."""

    def setUp(self):
        super().setUp()
        self.client.force_login(self.admin)
        member = make_member("grace")
        event = make_event()
        Registration.objects.create(event=event, user=member)
        committee = Committee.objects.create(
            name_en="Admin committee", name_nl="Admin commissie", email="a@example.com"
        )
        CommitteeMembership.objects.create(user=member, committee=committee)
        board = Board.objects.create(
            start=datetime.date(2020, 9, 1), end=datetime.date(2021, 9, 1)
        )
        BoardMembership.objects.create(
            board=board, member=member.member, function_en="Chair", function_nl="Voorz"
        )
        make_mail_templates("accept_account_en", "accept_account_nl")

    def test_admin_index(self):
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)

    def test_all_changelists_and_add_views(self):
        for model, model_admin in admin.site._registry.items():
            opts = model._meta
            with self.subTest(model=opts.label):
                for view in ("changelist", "add"):
                    try:
                        url = reverse(
                            f"admin:{opts.app_label}_{opts.model_name}_{view}"
                        )
                    except NoReverseMatch:
                        # Some CMS models only register a subset of the views
                        continue
                    response = self.client.get(url)
                    # Some CMS models redirect or forbid direct access
                    self.assertIn(response.status_code, (200, 302, 403), url)

    def test_change_views_of_our_models(self):
        for model in (
            User,
            Event,
            Committee,
            Board,
            Slideshow,
            MemberSettings,
            Configuration,
            MailTemplate,
        ):
            for obj in model.objects.all()[:3]:
                opts = model._meta
                with self.subTest(model=opts.label, pk=obj.pk):
                    url = reverse(
                        f"admin:{opts.app_label}_{opts.model_name}_change",
                        args=[obj.pk],
                    )
                    self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_add_event_through_admin(self):
        now = timezone.localtime()
        response = self.client.post(
            reverse("admin:events_event_add"),
            {
                "name_en": "Admin event",
                "name_nl": "Admin evenement",
                "location": "Sportcentrum",
                "cost_en": "free",
                "cost_nl": "gratis",
                "dates-TOTAL_FORMS": "1",
                "dates-INITIAL_FORMS": "0",
                "dates-0-start_0": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "dates-0-start_1": "10:00:00",
                "dates-0-end_0": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "dates-0-end_1": "12:00:00",
                "dates-0-show_end": "on",
                "registration_set-TOTAL_FORMS": "0",
                "registration_set-INITIAL_FORMS": "0",
            },
        )
        errors = response.context and response.context["adminform"].form.errors
        self.assertEqual(response.status_code, 302, errors)
        self.assertTrue(Event.objects.filter(name_en="Admin event").exists())

    def test_accept_user(self):
        user = make_member("henk", active=False)
        url = reverse("admin:auth_user_change", args=[user.pk])
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)

        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "date_joined_0": "2020-01-01",
            "date_joined_1": "10:00:00",
            "member-TOTAL_FORMS": "1",
            "member-INITIAL_FORMS": "1",
            "member-MIN_NUM_FORMS": "0",
            "member-MAX_NUM_FORMS": "1",
            "member-0-id": user.member.pk,
            "member-0-user": user.pk,
            "member-0-birthday": "2000-01-01",
            "member-0-gender": Member.OTHER,
            "member-0-phone_number": "0612345678",
            "member-0-street_address": "Street 1",
            "member-0-postcode": "1234AB",
            "member-0-city": "Nijmegen",
            "member-0-student_type": Member.RU,
            "member-0-sports_card_number": "s1234567",
            "member-0-preferred_language": "en",
            "member-0-google_email": "henk@gmail.com",
            "member-0-display_name": Member.FIRST_NAME,
            "_accept": "accept",
        }
        response = self.client.post(url, data)
        self.assertEqual(
            response.status_code,
            302,
            response.context
            and (
                response.context["adminform"].form.errors,
                [
                    f.errors
                    for f in response.context["inline_admin_formsets"][0].formset
                ],
            ),
        )
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_password_email_action(self):
        make_mail_templates("activate_account_en", "activate_account_nl")
        user = make_member("ivo", active=False)
        response = self.client.post(
            reverse("admin:auth_user_changelist"),
            {"action": "send_password_email", "_selected_action": [user.pk]},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/activate-account/", mail.outbox[0].body)

    def test_export_users(self):
        response = self.client.get(reverse("admin:auth_user_export"))
        self.assertEqual(response.status_code, 200)

    def test_import_users(self):
        from members.admin import UserResource
        import tablib

        output = io.StringIO()
        writer = csv.writer(output)
        header = [
            "first_name",
            "last_name",
            "email",
            "member__birthday",
            "member__gender",
            "member__pronouns",
            "member__phone_number",
            "member__street_address",
            "member__postcode",
            "member__city",
            "member__student_type",
            "member__sports_card_number",
            "member__preferred_language",
            "member__google_email",
        ]
        writer.writerow(header)
        writer.writerow(
            [
                "Jan",
                "Import",
                "jan@example.com",
                "2000-05-05",
                Member.MAN,
                "",
                "0687654321",
                "Road 3",
                "4321 BA",
                "Arnhem",
                Member.NOSTUDENT,
                "1234567",
                "nl",
                "jan@gmail.com",
            ]
        )
        dataset = tablib.Dataset().load(output.getvalue(), format="csv")
        result = UserResource().import_data(dataset, dry_run=False, raise_errors=True)
        self.assertFalse(result.has_errors())
        user = User.objects.get(email="jan@example.com")
        self.assertEqual(user.first_name, "Jan")
        self.assertEqual(user.member.city, "Arnhem")
        self.assertFalse(user.is_active)


class ProjectHealthTest(TestCase):
    def test_no_missing_migrations(self):
        out = io.StringIO()
        call_command(
            "makemigrations",
            "events",
            "committees",
            "members",
            "boards",
            "website",
            check=True,
            dry_run=True,
            stdout=out,
        )

    def test_system_checks(self):
        call_command("check")

    def test_templatetags(self):
        from events.templatetags.events_datetimerange import daterange, datetimerange

        start = timezone.make_aware(datetime.datetime(2025, 5, 1, 10, 0))
        self.assertEqual(daterange(start, start + timedelta(hours=2)), "01 May")
        self.assertEqual(daterange(start, start + timedelta(days=2)), "01 May - 03 May")
        self.assertIn("10:00", datetimerange(start, start + timedelta(hours=2)))
