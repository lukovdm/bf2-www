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
