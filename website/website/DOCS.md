# Core app
This is the core app of the website. It describes the settings, the templates and the main static files.

### Settings
The settings are build up of four files, `base.py`, `development.py`, `production.py` and `__init.py`. The `base.py` file
describes settings that are the same during development and on production. Most of these options are either from django
itself or from django-cms.

#### Production
Most of the settings in the production settings are set using environment variables. These are again set in the 
`config/secrets.env` file on the server. It allows us to have secret variables that only people that have access to the
server can see.

Also whenever an error occurs there should be an error send to `ADMINS` variable.

##### Adding an app
When adding an app, remember to also add it to the `INSTALLED_APPS` in `base.py`
