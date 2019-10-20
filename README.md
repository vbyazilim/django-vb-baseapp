![Python](https://img.shields.io/badge/python-3.7.4-green.svg)
![Django](https://img.shields.io/badge/django-2.2.6-green.svg)
![Version](https://img.shields.io/badge/version-1.0.1-orange.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4c6aa76f09fd437eb3888855fccc9604)](https://www.codacy.com/manual/vigo/django-vb-baseapp?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=vbyazilim/django-vb-baseapp&amp;utm_campaign=Badge_Grade)

# django-vb-baseapp

This is a helper app for https://github.com/vbyazilim/django-vb-admin

## Features

- 2 custom base models: `BaseModel` and `BaseModelWithSoftDelete`
- 2 custom base model admins: `CustomBaseModelAdmin` and `CustomBaseModelAdminWithSoftDelete`
- Soft deletion feature for model and model admin and admin actions
- `pre_undelete` and `post_undelete` signals for soft delete operation
- Pre enabled models admin site: `ContentTypeAdmin`, `LogEntryAdmin`, `PermissionAdmin`, `UserAdmin`
- Timezone and locale middlewares
- View level on screen debug feature
- Handy utils: `console`, `console.dir()`, `numerify`, `save_file`, `SlackExceptionHandler`
- File widget for Django Admin: `AdminImageFileWidget`
- `OverwriteStorage` for overwriting file uploads
- Custom file storage for missing files for development environment: `FileNotFoundFileSystemStorage`
- Custom and configurable error page views for: `400`, `403`, `404`, `500`
- Custom management command with basic output feature `CustomBaseCommand`

---

## License

This project is licensed under MIT

---

## Contributer(s)

* [Uğur "vigo" Özyılmazel](https://github.com/vigo) - Creator, maintainer

---

## Contribute

All PR’s are welcome!

1. `fork` (https://github.com/vbyazilim/django-vb-baseapp/fork)
1. Create your `branch` (`git checkout -b my-features`)
1. `commit` yours (`git commit -am 'Add killer features'`)
1. `push` your `branch` (`git push origin my-features`)
1. Than create a new **Pull Request**!

---

## Change Log

**2019-08-07**

- Initial Beta relase: 1.0.0

---
