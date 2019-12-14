## `HtmlDebugMixin`

`self.hdbg(arg, arg, arg, ...)` method helps you to output/debug some data
in view layer.

```python
# example view: index.py

import logging

from django.views.generic.base import TemplateView

from console import console
from vb_baseapp.mixins import HtmlDebugMixin

__all__ = ['BlogView']

logger = logging.getLogger('app')
console = console(source=__name__)


class BlogView(HtmlDebugMixin, TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        self.hdbg('Hello from hdbg')
        kwargs = super().get_context_data(**kwargs)
        console.dir(self.request.user)
        return kwargs
```

`{% hdbg %}` tag is added by default in to your `templates/base.html` and works
only if the settings `DEBUG` is set to `True`.

```django
{% load static i18n %}

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}{% endblock %}</title>
    {% if DJANGO_ENV == 'development' %}
    <link rel="stylesheet" href="{% static 'css/bulma.min.0.8.0.css' %}">
    <script defer src="{% static 'js/fontawesome.5.3.1.all.js' %}"></script>
    {% else %}
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.0/css/bulma.min.css">
    <script defer src="https://use.fontawesome.com/releases/v5.3.1/js/all.js"></script>
    {% endif %}
    <link rel="stylesheet" href="{% static 'css/vb-baseapp.css' %}">
    <link rel="stylesheet" href="{% static 'css/application.css' %}">
    {% block extra_css %}{% endblock %}
    <script defer src="{% static 'js/application.js' %}"></script>
</head>
<body>
    {% hdbg %}
    {% block body %}{% endblock %}
    {% block extra_js %}{% endblock %}
</body>
</html>
```

If you don’t want to extend from `templates/base.html` you can use your
own template. You just need to add `{% hdbg %}` tag in to your template if
you still want to enable this feature.

We have some mini helpers and tools shipped with `vb_baseapp`.

## `console`

This little tool helps you to output anything to console. This works only
in test and development mode. If you forget console declarations in your
code, do not worry... console checks `DJANGO_ENV` environment variable...

```python
from console import console

console = console(source=__name__)

console('hello', 'world')
```

You can inspect python object via `.dir()` method:

```python
console.dir([])

p = Post.objects.actives().first()
console.dir(p)
```

More information is available [here][vb-console]

## `vb_baseapp.utils.numerify`

Little helper for catching **QUERY_STRING** parameters for numerical values:

```python
from vb_baseapp.utils import numerify

>>> numerify("1")
1
>>> numerify("1a")
-1
>>> numerify("ab")
-1
>>> numerify("abc", default=44)
44
```

## `vb_baseapp.utils.save_file`

While using `FileField`, sometimes you need to handle uploaded files. In this
case, you need to use `upload_to` attribute. Take a look at the example:

```python
from vb_baseapp.utils import save_file as custom_save_file
:
:
:
class User(AbstractBaseUser, PermissionsMixin):
    :
    :
    avatar = models.FileField(
        upload_to=save_user_avatar,
        verbose_name=_('Profile Image'),
        null=True,
        blank=True,
    )
    :
    :
```

`save_user_avatar` returns `custom_save_file`’s return value. Default
configuration of for `custom_save_file` is 
`save_file(instance, filename, upload_to='upload/%Y/%m/%d/')`. Uploads are go to
such as `MEDIA_ROOT/upload/2017/09/21/`...

Make your custom uploads like:

```python
from vb_baseapp.utils import save_file as custom_save_file

def my_custom_uploader(instance, filename):
    # do your stuff
    # at the end, call:
    return custom_save_file(instance, filename, upload_to='images/%Y/')


class MyModel(models.Model):
    image = models.FileField(
        upload_to='my_custom_uploader',
        verbose_name=_('Profile Image'),
    )
```

## SlackExceptionHandler

`vb_baseapp.utils.log.SlackExceptionHandler`

You can send errors/exceptions to [slack](https://api.slack.com) channel.
Just create a slack app, get the webhook URL and set as `SLACK_HOOK`
environment variable. Due to slack message size limitation, `traceback`
is disabled.

Example message contains:

- http status
- error message
- exception message
- user.id or None
- full path

```bash
http status: 500
ERROR (internal IP): Internal Server Error: /__vb_baseapp__/
Exception: User matching query does not exist.
user_id: anonymous (None)
full path: /__vb_baseapp__/?foo=!
```

You can enable/disable in `config/settings/production.py` / `config/settings/heroku.py`:

```python
:
:
    'loggers': {
        'django.request': {'handlers': ['mail_admins', 'slack'], 'level': 'ERROR', 'propagate': False},  # remove 'slack'
    }
:
:
```

## `vb_baseapp.storage`

### `FileNotFoundFileSystemStorage`

After shipping/deploying Django app, users start to upload files, right ?
Then you need to implement new features etc. You can get the dump of the
database but what about uploaded files ? Sometimes files are too much or
too big. If you call, let’s say, a model’s `ImageField`’s `url` property,
local dev server logs lot’s of **file not found** errors to console.

Also breaks the look of application via broken image signs in browser.

Now, you won’t see any errors... `FileNotFoundFileSystemStorage` is a
fake storage that handles non existing files. Returns `file-not-found.jpg`
from `static/images/` folder.

This is **development purposes** only! Do not use in the production!

You don’t need to change/add anything to your code... It’s embeded to
`config/settings/development.py`:

```python
:
:
DEFAULT_FILE_STORAGE = 'vb_baseapp.storage.FileNotFoundFileSystemStorage'
:
```

You can disable if you like to...

### `OverwriteStorage`

`OverwriteStorage` helps you to overwrite file when uploading from django
admin. Example usage:

```python
# in a model
from vb_baseapp.storage import OverwriteStorage

class MyModel(models.Model):
    :
    :
    photo = models.ImageField(
        upload_to=save_media_photo,
        storage=OverwriteStorage(),
    )
    :
    :
```

Add `storage` option in your file related fields.

## `AdminImageFileWidget`

Use this widget in your admin forms. By default, It’s already enabled in
`CustomBaseModelAdmin`. You can also inject this to Django’s default `ModelAdmin`
via example:

```python
from vb_baseapp.admin.widgets import AdminImageFileWidget

class MyAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.FileField: {'widget': AdminImageFileWidget},
    }
```

This widget uses `Pillow` (*Python Image Library*) which ships with your `base.pip`
requirements file. Show image preview, width x height if the file is image.

## `context_processors.py`

By default, `vb_baseapp` injects few variables to you context:

- `DJANGO_ENV`
- `IS_DEBUG`
- `LANGUAGE_CODE`
- `CURRENT_GIT_TAG`
- `CURRENT_PYTHON_VERSION`
- `CURRENT_DJANGO_VERSION`

## Timezone

Default timezone is set to `UTC`, please change this or use according to your
needs.

```python
# config/settings/base.py
# ...
TIME_ZONE = 'UTC'
# ...
```

[vb-console]: https://github.com/vbyazilim/vb-console