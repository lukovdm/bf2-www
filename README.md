# bf2-www

The new website for the BFrisBee2's. Written with django-cms.

Structure
----------

The website is structured around a core of django-cms, with a few specific apps written for various purposes.
The core of the website can be found in /website/website/
All other apps can found in the /website/ folder with fairly descriptive names. Only utils is no app and contains 
general utilities that are needed for the other apps.

Every app and the core will have documentation written in them to explain how they work. This is still WIP and thus
not everything is yet documented.

Setup
----------

To setup the website you can follow these general steps:

First make sure you have python 3.11 installed and [poetry](https://python-poetry.org/)

This tutorial is made for linux like systems, when using windows commands might be a bit different. But I think when installing the software correctly it should be not to different.

For more information on poetry look at the [docs](https://python-poetry.org/docs/basic-usage/)

1. Clone the repo
2. Open a terminal in the repo
3. run  `poetry install` to install all the python dependecies
4. run `poetry shell` to enter the virtual env
5. go to the website folder
6. run first start of the server according to django docs
  a. Run `./manage.py migrate` to create the db and apply migrations
  b. Run `./manage.py makesuperuser` to add a user to the server
7. Run `./manage.py runserver` to start the server
8. Open the website in you browser and do the first setup
9. Make sure to give yourself a member in the admin panel under users
10. Setup you editor such that it works nice :)

Hope this helps a bit
