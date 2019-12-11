## `CustomBaseModelAdmin`, `CustomBaseModelAdminWithSoftDelete`

Inherits from `admin.ModelAdmin`. When model is created via `rake new:model...` 
or via management command, admin file is generated automatically.

This model admin overrides `models.ImageField` form field and displays fancy
thumbnail for images. By default, uses cached paginator and sets `show_full_result_count`
to `False` for performance improvements.

## Model Admin Properties

`show_goback_button` is set to `True` by default. You can disable via;

```python
class ExampleAdmin(CustomBaseModelAdminWithSoftDelete):
    # ...
    show_goback_button = False
    # ...
```

- `show_full_result_count` is set to `False` by default.
- `hide_deleted_at` is set to `True` by default. This means, you will not see
that field while editing the instance.

Example for `Post` model admin (*auto generated*).

```python
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
    # hide_deleted_at = False
```

By default, `deleted_at` excluded from admin form like `created_at` and
`updated_at` fields. You can also override this via `hide_deleted_at`
attribute. Comment/Uncomment lines according to your needs! This works only in
`CustomBaseModelAdminWithSoftDelete`.

`CustomBaseModelAdminWithSoftDelete` also comes with special admin action. You can
recover/make active (*undelete*) multiple objects like deleting feature of
Django’s default.

## Extra Features

When you’re dealing with soft-deleted objects, you’ll see **HARD DELETE** and 
**RECOVER** buttons in the change form. Hard delete really wipes the items
from database. Recover, recovers/undeletes object and related elements.

You’ll also have **GO BACK** button too :)
