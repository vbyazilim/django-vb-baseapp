`vb_baseapp` ships with three managements commands;

## `create_app`

```bash
$ python manage.py create_app NAME_OF_APP
```

Creates new Django application under `applications/` and provides application
folder structure:

    applications/NAME_OF_APP/
    ├── admin
    ├── management
    ├── migrations
    ├── models
    ├── tests
    ├── views
    ├── __init__.py
    ├── apps.py
    └── urls.py

## `create_model`

```bash
$ python manage.py create_model NAME_OF_APP NAME_OF_MODEL STYLE_OF_MODEL
```

Creates Django model. You have three different model style;

1. `django`: Uses Django’s `models.Model`
1. `basemodel`: Uses `CustomBaseModel` (which inherits from `models.Model`)
1. `softdelete`: Uses `CustomBaseModelWithSoftDelete`

According to your model choice, related files will be generated.

## `create_custom_user_model`

```bash
$ python manage.py create_custom_user_model NAME_OF_APP NAME_OF_MODEL STYLE_OF_MODEL 
```

This command will work only in the beginning state of development. Creating
a custom user model is prohibited in the middle of the development. You
must decide before you create other models or run initial migrations for
Django’s default.

This command creates;

- Admin files
- Model manager files
- Model admin form files
- Model files

for given argumens. Let’s say you’ll start a fresh project and want to use
custom user model. First, you need to create an app:

```bash
$ python manage.py create_app blog
# follow the instructions
$ python manage.py create_custom_user_model blog CustomUser softdelete

Set AUTH_USER_MODEL in config file
models/custom_user.py created.
admin/custom_user.py created.
CustomUser model added to models/__init__.py
CustomUser model added to admin/__init__.py
CustomUser forms added to admin/forms/__init__.py
admin/forms/custom_user.py created.

Custom user installation completed. Now please check your;

    - blog/models/custom_user.py
    - blog/admin/custom_user.py
    - blog/admin/forms/custom_user.py

Also;

    - `email` field is set to `USERNAME_FIELD`
    - `first_name` and `last_name` are set as `REQUIRED_FIELDS`
    - `middle_name`, `profile_image` are optionals

Make sure if all ok? Make your changes before running migrations:

    $ python manage.py makemigrations --name create_custom_users
```

We’ve created `CustomUser` model from softdeletable object. Default fields
are:

- `email`: `EmailField`
- `first_name`: `CharField`
- `middle_name`: (optional) `CharField`
- `last_name`: `CharField`
- `profile_image`: (optional) `FileField`
- `is_active`: (optional) `BooleanField`
- `is_staff`: (optional) `BooleanField`

and other fields inherited from `AbstractBaseUser`:

- `password`
- `last_login`

and other properties from `PermissionsMixin`. You can add/change or remove
fields before creating migrations. Do not forget to check these files for
`CustomUser` for the sake of this example:

- `admin/custom_user.py`
- `admin/forms/custom_user.py`
- `models/custom_user.py`

Also, this management commands sets `AUTH_USER_MODEL` value in `config/base.py`.
You’ll see;

```python
AUTH_USER_MODEL = 'blog.CustomUser'
```

since you’ve named the custom model as `CustomUser`.
