# General things to do
In this file we will document general things that have to be done for all apps.

## Translations
The entire website is written in English. All code is English, all comments are English and all strings are English. For us to still have Dutch text on the website we thus make use of the [i18n tools of django](https://docs.djangoproject.com/en/4.2/topics/i18n/).

### Mark as translatable
Thus, to mark a string as to translate we wrap the `_( )` function around it. This function is imported using the following line: 
```python 
from django.utils.translation import gettext_lazy as _
```
For any more advanced translation things, look at the documentation. You can have separate singular and plural translations and many more options if needed.

### Do translations
To now translate any strings that need translating follow the following steps:
1. cd to the folder of the app you want to translate
2. Run `../manage.py makemessages -a --no-obsolete`, this adds any new lines to translate to the `locale/nl/LC_MESSAGES/django.po` file.
3. Use the [poedit](https://poedit.net/) program to open the `django.po` file and edit any translation necessary.
4. Save the file.
5. Profit

##### Remarks
Poedit sometimes throws random errors, these can usually be ignored.

## Multilingual Field
TODO
