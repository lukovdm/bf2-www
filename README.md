# bf2-www

The new website for the BFrisBee2's. Written with django-cms.

Setup
----------

First make sure you have [uv](https://docs.astral.sh/uv/) installed (or use `nix develop`, which provides it). uv installs the right Python version (3.13) for you.

This tutorial is made for linux like systems, when using windows commands might be a bit different. But I think when installing the software correctly it should be not to different.

For more information on uv look at the [docs](https://docs.astral.sh/uv/getting-started/)

This is a bit hasty but should give the mayor steps
1. Clone the repo
2. Open a terminal in the repo
3. run `uv sync` to install all the python dependencies
4. run `source .venv/bin/activate` to enter the virtual env (or prefix commands with `uv run`)
5. go to the website folder
6. run first start of the server according to django docs
  a. Run `./manage.py migrate` to create the db and apply migrations
  b. Run `./manage.py createsuperuser` to add a user to the server
7. Run `./manage.py runserver` to start the server
   Run `./manage.py test` to run the tests
8. Open the website in you browser and do the first setup
9. Make sure to give yourself a memeber in the admin panel under users
10. Setup you editor such that it works nice :)

Hope this helps a bit

Google Forms for events
----------

Events can have a Google Form that members fill in after registering. The website checks which members filled in the form, so their registration is only complete after they did. Without this setup the website still works, members then confirm themselves that they filled in the form.

### For committees

1. Make the form in Google Forms and copy the share link ("Send" > link icon) into the "Google form link" of the event.
2. Share the form with the email address of the website as **editor** (the person with a plus icon at the top right of Google Forms). The admin page of the event shows this address below the "Google form link" field.
3. Save the event. The website adds a "Registration code" question at the top of the form, do not remove it. Members get the form with their code filled in.

The registrations in the admin and the csv export show who filled in the form. You can also mark a registration as filled in by hand.

### One time setup (webmasters)

1. Go to https://console.cloud.google.com, create a project (e.g. "bf2-website") and enable the "Google Forms API" and the "Google Drive API" for it.
2. Go to "IAM & Admin" > "Service Accounts", create a service account (no roles needed) and open it. Under "Keys" add a key of type JSON and download it.
3. Put the key on the server as `config/google-service-account.json` (it is in `.gitignore`, never commit it) and mount it in the `web` service of `docker-compose.yaml`:
   ```yaml
   volumes:
     - ./config/google-service-account.json:/bf2-www/google-service-account.json:ro
   ```
4. Add `GOOGLE_SERVICE_ACCOUNT_FILE=/bf2-www/google-service-account.json` to `config/secrets.env` and restart.
5. Tell the committees the email address of the service account (the `client_email` in the key, also shown in the admin of every event with a form).

For local development put the key at `config/google-service-account.json`, it is used when `GOOGLE_SERVICE_ACCOUNT_FILE` is not set.
