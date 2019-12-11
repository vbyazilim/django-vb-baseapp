Let’s build a basic blog with categories and tags! First, create a virtual
environment:

```bash
# via builtin
$ python -m venv my_env
$ source my_env/bin/activate

# or via virtualenvwrapper
$ mkvirtualenv my_env
```

Now, create a postgresql database;

```bash
$ createdb my_project_dev
```

Now set your environment variables:

```bash
$ export DJANGO_SECRET=$(head -c 75 /dev/random | base64 | tr -dc 'a-zA-Z0-9' | head -c 50)
$ export DATABASE_URL="postgres://localhost:5432/my_project_dev"
```

Edit `my_env/bin/activate` or `~/.virtualenvs/my_env/bin/postactivate`
(*according to your virtualenv creation procedure*) and put these export
variables in it. Will be handy next time you activate the environment. Now;

```bash
$ pip install django-vb-admin
$ cd /path/to/my-django-project
$ django-vb-admin startproject
# or
$ django-vb-admin startproject --target="/path/to/folder"
```

You’ll see:

```bash
Setup completed...
Now, create your virtual environment and run

	pip install -r requirements/development.pip

```

message. Now;

```bash
$ pip install -r requirements/development.pip
$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying sessions.0001_initial... OK
```

Now, we have a ready Django project. Let’s check;

```bash
$ python manage.py runserver_plus

# or

$ rake

INFO |  * Running on http://127.0.0.1:8000/ (Press CTRL+C to quit)
INFO |  * Restarting with stat
Performing system checks...

System check identified no issues (0 silenced).

Django version X.X.X, using settings 'config.settings.development'
Development server is running at http://[127.0.0.1]:8000/
Using the Werkzeug debugger (http://werkzeug.pocoo.org/)
Quit the server with CONTROL-C.
WARNING |  * Debugger is active!
WARNING |  * Debugger PIN disabled. DEBUGGER UNSECURED!
```

## Blog Application

Let’s create a **blog** app!

```bash
$ python manage.py create_app blog

# or

$ rake new:application[blog]

"blog" application created.


    - Do not forget to add your `blog` to `INSTALLED_APPS` under `config/settings/base.py`:

    INSTALLED_APPS += [
        'django_extensions',
        'blog.apps.BlogConfig', # <-- add this
    ]

    - Do not forget to fix your `config/urls.py`:

    # ...
    # add your newly created app's urls here!
    urlpatterns += [
        # ...
        # this is just an example!
        path('__blog__/', include('blog.urls', namespace='blog')),
        # ..
    ]
    # ...
```

You can follow the instructions, fix your `config/settings/base.py` and
`config/urls.py` as seen on the command output. Now run development server
and call the url:

```bash
$ python manage.py runserver_plus
```

Open `http://127.0.0.1:8000/__blog__/`. Also, another builtin app is running;
`http://127.0.0.1:8000/__vb_baseapp__/`. You can remove `__vb_baseapp__`
config from `config/urls.py`.

Now let’s add some models. We have 3 choices as parameters:

1. `django`: Uses Django’s `models.Model`
1. `basemodel`: Uses `CustomBaseModel` (which inherits from `models.Model`)
1. `softdelete`: Uses `CustomBaseModelWithSoftDelete`

We’ll use soft-deletable model to demonstrate soft-delete features. Let’s
create `Post`, `Category` and `Tag` models:

```bash
$ python manage.py create_model blog post softdelete

# or

$ rake new:model[blog,post,softdelete]

models/post.py created.
admin/post.py created.
post model added to models/__init__.py
post model added to admin/__init__.py


    `post` related files created successfully:

    - `blog/models/post.py`
    - `blog/admin/post.py`

    Please check your models before running `makemigrations` ok?

$ python manage.py create_model blog category softdelete

# or

$ rake new:model[blog,category,softdelete]

models/category.py created.
admin/category.py created.
category model added to models/__init__.py
category model added to admin/__init__.py


    `category` related files created successfully:

    - `blog/models/category.py`
    - `blog/admin/category.py`

    Please check your models before running `makemigrations` ok?

$ python manage.py create_model blog tag softdelete

# or

$ rake new:model[blog,tag,softdelete]

models/tag.py created.
admin/tag.py created.
tag model added to models/__init__.py
tag model added to admin/__init__.py


    `tag` related files created successfully:

    - `blog/models/tag.py`
    - `blog/admin/tag.py`

    Please check your models before running `makemigrations` ok?
```

Let’s fix models before creating and executing migrations:

```python
# blog/models/post.py

import logging

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from console import console
from vb_baseapp.models import CustomBaseModelWithSoftDelete

__all__ = ['Post']

logger = logging.getLogger('app')
console = console(source=__name__)


class Post(CustomBaseModelWithSoftDelete):
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', verbose_name=_('author')
    )
    category = models.ForeignKey(
        to='Category', on_delete=models.CASCADE, related_name='posts', verbose_name=_('category')
    )
    title = models.CharField(max_length=255, verbose_name=_('title'))
    body = models.TextField(verbose_name=_('body'))
    tags = models.ManyToManyField(to='Tag', related_name='posts', blank=True)

    class Meta:
        app_label = 'blog'
        verbose_name = _('post')
        verbose_name_plural = _('posts')  # check pluralization

    def __str__(self):
        return self.title
```

and `Category` model:

```python
# blog/models/category.py

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from console import console
from vb_baseapp.models import CustomBaseModelWithSoftDelete

__all__ = ['Category']

logger = logging.getLogger('app')
console = console(source=__name__)


class Category(CustomBaseModelWithSoftDelete):
    title = models.CharField(max_length=255, verbose_name=_('title'))

    class Meta:
        app_label = 'blog'
        verbose_name = _('category')
        verbose_name_plural = _('categories')  # check pluralization

    def __str__(self):
        return self.title
```

and `Tag` model:

```python
# blog/models/tag.py

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from console import console
from vb_baseapp.models import CustomBaseModelWithSoftDelete

__all__ = ['Tag']

logger = logging.getLogger('app')
console = console(source=__name__)


class Tag(CustomBaseModelWithSoftDelete):
    name = models.CharField(max_length=255, verbose_name=_('name'))

    class Meta:
        app_label = 'blog'

    def __str__(self):
        return self.name
```

Let’s create and run migration file:

```bash
$ python manage.py makemigrations --name create_post_category_and_tag

# or

$ rake db:update[blog,create_post_category_and_tag]

Migrations for 'blog':
  applications/blog/migrations/0001_create_post_category_and_tag.py
    - Create model Category
    - Create model Tag
    - Create model Post

$ python manage.py migrate

# or

$ rake db:migrate

Operations to perform:
  Apply all migrations: admin, auth, blog, contenttypes, sessions
Running migrations:
  Applying blog.0001_create_post_category_and_tag... OK
```

Now we have a model which has relations to other models via `ForeignKey` and
`ManyToMany` level. Let’s tweak `blog/admin/post.py`:

```python
# blog/admin/post.py

import logging

from django.contrib import admin

from console import console
from vb_baseapp.admin import (
    CustomBaseModelAdminWithSoftDelete,
)

from ..models import Post

__all__ = ['PostAdmin']

logger = logging.getLogger('app')
console = console(source=__name__)


@admin.register(Post)
class PostAdmin(CustomBaseModelAdminWithSoftDelete):
    list_filter = ('category', 'tags', 'author')
    list_display = ('__str__', 'author')
    ordering = ('title',)
    # hide_deleted_at = False
```

Let’s create a super user and jump in to admin pages. `AUTH_PASSWORD_VALIDATORS`
is removed from **development** settings, you can type any password :)

```bash
$ python manage.py createsuperuser --username="${USER}" --email="your@email.com"
$ python manage.py runserver_plus

# or

$ rake

INFO |  * Running on http://127.0.0.1:8000/ (Press CTRL+C to quit)
INFO |  * Restarting with stat
Performing system checks...

System check identified no issues (0 silenced).

Django version X.X.X, using settings 'config.settings.development'
Development server is running at http://[127.0.0.1]:8000/
Using the Werkzeug debugger (http://werkzeug.pocoo.org/)
Quit the server with CONTROL-C.
WARNING |  * Debugger is active!
WARNING |  * Debugger PIN disabled. DEBUGGER UNSECURED!
INFO | GET | 302 | /admin/
INFO | GET | 200 | /admin/login/?next=/admin/
INFO | GET | 404 | /favicon.ico
:
:
```

Now open `http://127.0.0.1:8000/admin/` and add a new blog post! 
Create different categories and tags. Then open 
`http://127.0.0.1:8000/admin/blog/category/` page. 

In the Action menu, you’ll have couple extra options:

- Delete selected categories
- Recover selected categories (*Appears if you are filtering inactive records*)
- Hard delete selected categories

Now, delete one or more categories or tags. Check **activity state** filter
for post, category and tag models. You can recover deleted items from the
action menu too.
