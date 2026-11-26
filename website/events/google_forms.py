"""Read Google Form responses, to check if members filled in the form of an event.

A committee shares their Google Form with the service account of the website
(as editor). The website then:

- finds the form by its share link, through the Drive API;
- adds a "Registration code" question to the form if it is not there yet;
- sends members a prefilled link with their registration code;
- reads the responses to see which registration codes submitted the form.

Configure it with the ``GOOGLE_SERVICE_ACCOUNT_FILE`` setting (path to the
json key of the service account). Without it the integration is disabled and
members confirm themselves that they submitted the form.
See the README for the setup.
"""

import json
import logging
import re
from functools import cache
from urllib.parse import urlencode

from django.conf import settings

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]
FORMS_API = "https://forms.googleapis.com/v1/forms"
DRIVE_API = "https://www.googleapis.com/drive/v3/files"
CODE_QUESTION_TITLE = "Registration code"
CODE_QUESTION_DESCRIPTION = (
    "Filled in by the website, do not change this. / "
    "Ingevuld door de website, verander dit niet."
)

PUBLISHED_ID = re.compile(r"/forms/d/e/([\w-]+)/")


class GoogleFormsError(Exception):
    """Something is wrong with the form or the connection to Google."""


def published_id(link):
    """The published id of a form share link (.../forms/d/e/<id>/viewform)."""
    match = PUBLISHED_ID.search(link or "")
    return match.group(1) if match else None


def prefilled_link(link, entry_id, code):
    """The share link of the form with the registration code filled in."""
    form = published_id(link)
    query = {"usp": "pp_url", f"entry.{entry_id}": code, "embedded": "true"}
    return f"https://docs.google.com/forms/d/e/{form}/viewform?{urlencode(query)}"


def entry_id(question_id):
    """The entry id used in prefilled links for a question id of the API."""
    return str(int(question_id, 16))


def is_configured():
    return bool(getattr(settings, "GOOGLE_SERVICE_ACCOUNT_FILE", None))


def service_account_email():
    if not is_configured():
        return None
    try:
        with open(settings.GOOGLE_SERVICE_ACCOUNT_FILE) as f:
            return json.load(f).get("client_email")
    except (OSError, ValueError):
        logger.exception("Cannot read the Google service account file")
        return None


@cache
def _session():
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return AuthorizedSession(credentials)


class GoogleFormsClient:
    """Small wrapper around the parts of the Forms and Drive APIs we use."""

    timeout = 10

    def _request(self, method, url, **kwargs):
        if not is_configured():
            raise GoogleFormsError("The Google forms integration is not configured.")
        try:
            response = _session().request(method, url, timeout=self.timeout, **kwargs)
        except Exception as error:
            raise GoogleFormsError(f"Cannot reach Google: {error}") from error
        if response.status_code >= 400:
            raise GoogleFormsError(
                f"Google returned {response.status_code}: {response.text[:200]}"
            )
        return response.json() if response.content else {}

    def find_form(self, link):
        """The form id of the form with this share link.

        Only forms that are shared with the service account can be found.
        """
        wanted = published_id(link)
        if not wanted:
            raise GoogleFormsError("This is not a Google Forms share link.")
        page_token = None
        while True:
            params = {
                "q": "mimeType='application/vnd.google-apps.form' and trashed=false",
                "fields": "nextPageToken, files(id)",
                "pageSize": 100,
            }
            if page_token:
                params["pageToken"] = page_token
            result = self._request("GET", DRIVE_API, params=params)
            for file in result.get("files", []):
                form = self._request(
                    "GET",
                    f"{FORMS_API}/{file['id']}",
                    params={"fields": "responderUri"},
                )
                if published_id(form.get("responderUri", "")) == wanted:
                    return file["id"]
            page_token = result.get("nextPageToken")
            if not page_token:
                return None

    def ensure_code_question(self, form_id):
        """Add the registration code question if needed, return its question id."""
        form = self._request("GET", f"{FORMS_API}/{form_id}")
        for item in form.get("items", []):
            if item.get("title") == CODE_QUESTION_TITLE and "questionItem" in item:
                return item["questionItem"]["question"]["questionId"]
        self._request(
            "POST",
            f"{FORMS_API}/{form_id}:batchUpdate",
            json={
                "requests": [
                    {
                        "createItem": {
                            "item": {
                                "title": CODE_QUESTION_TITLE,
                                "description": CODE_QUESTION_DESCRIPTION,
                                "questionItem": {
                                    "question": {
                                        "required": True,
                                        "textQuestion": {"paragraph": False},
                                    }
                                },
                            },
                            "location": {"index": 0},
                        }
                    }
                ]
            },
        )
        return self.ensure_code_question(form_id)

    def submitted_codes(self, form_id, question_id):
        """The registration codes in the responses of the form."""
        codes = set()
        page_token = None
        while True:
            params = {"pageSize": 5000}
            if page_token:
                params["pageToken"] = page_token
            result = self._request(
                "GET", f"{FORMS_API}/{form_id}/responses", params=params
            )
            for response in result.get("responses", []):
                answer = response.get("answers", {}).get(question_id, {})
                for value in answer.get("textAnswers", {}).get("answers", []):
                    codes.add(value.get("value", "").strip().upper())
            page_token = result.get("nextPageToken")
            if not page_token:
                return codes


def get_client():
    """The client to use, replaced by a fake in the tests."""
    return GoogleFormsClient()
