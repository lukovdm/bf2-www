"""Keep the form status of registrations in sync with the Google Form.

See google_forms.py for how the website talks to Google. Without a configured
service account, or for forms that are not shared with it, members confirm
themselves that they filled in the form.
"""

import logging
from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext as _

from events import google_forms
from events.models import Registration

logger = logging.getLogger(__name__)

# How often the responses of a form are checked when pages are viewed
CHECK_INTERVAL = timedelta(minutes=5)


def connect_form(event):
    """Find the Google Form of the event and add the registration code question.

    Stores the result (or the problem) on the event.
    """
    event.google_form_id = ""
    event.google_form_question = ""
    event.google_form_error = ""
    if event.form_link and google_forms.is_configured():
        client = google_forms.get_client()
        try:
            form_id = client.find_form(event.form_link)
            if form_id:
                event.google_form_question = client.ensure_code_question(form_id)
                event.google_form_id = form_id
            else:
                event.google_form_error = _(
                    "The website cannot find the form, it is not shared with "
                    "%(email)s as editor. Note that adding the address as "
                    "responder is not enough. In Google Forms click the person "
                    "with a plus icon at the top right, add the address under "
                    "editors and save the event again."
                ) % {"email": google_forms.service_account_email()}
        except google_forms.GoogleFormsError as error:
            logger.warning("Cannot connect the form of %s: %s", event, error)
            event.google_form_error = str(error)
    event.google_form_checked_at = timezone.now()
    event.save(
        update_fields=[
            "google_form_id",
            "google_form_question",
            "google_form_error",
            "google_form_checked_at",
        ]
    )


def sync_form(event, force=False):
    """Mark the registrations whose code is in the form responses as filled in.

    Without ``force`` Google is only asked every CHECK_INTERVAL. A form that is
    not connected yet (e.g. shared after saving the event) is connected first.
    """
    if not event.form_link or not google_forms.is_configured():
        return
    checked = event.google_form_checked_at
    if not force and checked and timezone.now() - checked < CHECK_INTERVAL:
        return
    if not event.form_connected:
        connect_form(event)
        if not event.form_connected:
            return

    try:
        codes = google_forms.get_client().submitted_codes(
            event.google_form_id, event.google_form_question
        )
    except google_forms.GoogleFormsError as error:
        logger.warning("Cannot check the form of %s: %s", event, error)
        event.google_form_error = str(error)
        event.google_form_checked_at = timezone.now()
        event.save(update_fields=["google_form_error", "google_form_checked_at"])
        return

    # Also upgrade registrations the member confirmed themselves, e.g. when
    # the response reached Google later
    event.registration_set.filter(
        code__in=codes,
        form_status__in=[
            Registration.FORM_NOT_DONE,
            Registration.FORM_SELF_REPORTED,
            Registration.FORM_NOT_FOUND,
        ],
    ).update(form_status=Registration.FORM_VERIFIED, form_completed_at=timezone.now())
    event.google_form_error = ""
    event.google_form_checked_at = timezone.now()
    event.save(update_fields=["google_form_error", "google_form_checked_at"])


def form_status_text(event):
    """A description of the connection of the form, for the admin."""
    if not event.form_link:
        return _("This event has no form.")
    if not google_forms.is_configured():
        return _(
            "The Google Forms connection of the website is not set up, members "
            "confirm themselves that they filled in the form."
        )
    if event.form_connected:
        text = _("Connected: the website checks which members filled in the form.")
        if event.google_form_error:
            text += " " + _("Last check failed: %(error)s") % {
                "error": event.google_form_error
            }
        return text
    if event.google_form_error:
        return _("Not connected: %(error)s") % {"error": event.google_form_error}
    return _(
        "Not connected yet. Share the form with %(email)s as editor (not as "
        "responder) in Google Forms and save the event again."
    ) % {"email": google_forms.service_account_email()}
