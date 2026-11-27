# Core app
This is the core app of the website. It describes the settings, the templates and the main static files.

## Settings
The settings are build up of four files, `base.py`, `development.py`, `production.py` and `__init.py`. The `base.py` file
describes settings that are the same during development and on production. Most of these options are either from django itself or from django-cms.

### Production
Most of the settings in the production settings are set using environment variables. These are again set in the `config/secrets.env` file on the server. It allows us to have secret variables that only people that have access to the server can see.

Also, whenever an error occurs there should be an error send to `ADMINS` variable.

### Adding an app
When adding an app, remember to also add it to the `INSTALLED_APPS` in `base.py`

## Templates
The website has two main templates that pages are based of off. We have the `fullpage` template, which contains the template for the front page. And we have the `page` template, for all other pages.

All pages are base on one template, `base.html`. This template loads in any necessary css and js, adds messages, the footer and the easter egg. It also defines two blocks in which other templates can place content to load it onto the page. These are the `header` and `middle` block. The footer is build by adding 3 static placeholders such that they can be edited in the cms and are the same on every page.

Next we have the `base_contained.html` template. This template just adds the white container to a page and makes a new block for content called `pagecontent`. This between template has been added since the member list page does not have a white container and we thus needed a base without. But, all other pages do need a white container. The members list does not directly use `base.html`, instead it uses `page_empty.html` as it also includes the default header and menu bar.

Both the `page` and `fullpage` templates have two version, one for the cms and one not for the cms. The page for the cms has placeholder tags where content can be added. The non cms pages don't have these placeholders and can be use by the apps we make.

The menu is a separate template as it is the same in both `fullpage` and `page`, but included differently. It is based upon the django cms menu template.

## Slideshows
The full page template makes use of random images for the frontpage every time you open the website. These images can be added in the django admin in the slideshow admin. This also means that we have a slideshow model in our website. This model is located in the website app. Not the nicest place but it works. To add the slideshow image to the context of a template we use a context processor to add a slideshow iamge to the context of every page. This is context processor can be found in `website/website/context_processors.py` and the setting to add it is in the base settings file.

## Menu
The menu uses the django cms menu system. We only change one thing, when creating the menu structure we add a property `is_home` to every node, to determine if a node is the home page. When rendering the menu in the template we use this `is_home` property to make it blue to highlight the home page. For further information look at the [django cms menu docs](https://docs.django-cms.org/en/latest/reference/navigation.html).
