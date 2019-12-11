# django-vb-baseapp

This is a helper app for [django-vb-admin][django-vb-admin]
and ships with while installation:

```bash
$ pip install django-vb-admin
$ django-vb-admin -h
```

It’s also available on PyPI and available via:

```bash
$ pip install django-vb-baseapp
```

## Features

- Two abstract custom base models: `CustomBaseModel` and `CustomBaseModelWithSoftDelete`
- Two custom base model admins: `CustomBaseModelAdmin` and `CustomBaseModelAdminWithSoftDelete`
- Soft deletion feature and admin actions for `CustomBaseModelAdminWithSoftDelete`
- `pre_undelete` and `post_undelete` signals for **soft delete** operation
- Pre enabled models admin site: `ContentTypeAdmin`, `LogEntryAdmin`, `PermissionAdmin`, `UserAdmin`
- Timezone and locale middlewares
- Onscreen debugging feature for views! (Template layer...)
- Handy utils: `numerify`, `save_file`, `SlackExceptionHandler`
- Fancy file widget: `AdminImageFileWidget` for `ImageField` on admin by default
- `OverwriteStorage` for overwriting file uploads
- Custom file storage for missing files for development environment: `FileNotFoundFileSystemStorage`
- Custom and configurable error page views for: `400`, `403`, `404`, `500`
- Custom management command with basic output feature `CustomBaseCommand`
- Builtin `console`, `console.dir()` via `vb-console` [package][vb-console]
- Simpler server logging for `runserver_plus`
- This project uses [bulma.io][bulma.io] as HTML/CSS framework, ships with **jQuery** and **Fontawesome**


[django-vb-admin]: https://github.com/vbyazilim/django-vb-admin
[vb-console]: https://github.com/vbyazilim/vb-console
[bulma.io]: https://bulma.io