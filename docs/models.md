## `CustomBaseModel`

This is a common model. By default, `CustomBaseModel` contains these fields:

- `created_at`
- `updated_at`

Almost a default `models.Model` with two extra fields.

## `CustomBaseModelWithSoftDelete`

This model inherits from `CustomBaseModel` and provides fake deletion which is
probably called **SOFT DELETE**. This means, when you call model’s `delete()`
method or QuerySet’s `delete()` method, it acts like delete action but never
deletes the data.

Just sets the `deleted_at` field to **NOW**.

This works exactly like Django’s `delete()`. Broadcasts `pre_delete` and
`post_delete` signals and returns the number of objects marked as deleted and
a dictionary with the number of deletion-marks per object type.

You can call `hard_delete()` method to delete an instance or a queryset
actually.

This model uses `CustomBaseModelWithSoftDeleteManager` as default manager.

### How soft-delete works?

When you call `.delete()` method of a model instance or queryset, model manager
sets `deleted_at` attribute to **NOW** all the way down through related
`ForeignKey` and `ManyToMany` fields. This means, you still keep everything.

Nothing is actually deleted, therefore your database constraints are still
work fine. When you access deleted (*inactive*) object from admin site, you’ll
see "deleted" text prefix in your related form fields if your related objects
are `CustomBaseModelWithSoftDelete` instances.

When you click **recover** button in the same page, all related and soft-deleted
objects’ `deleted_at` value will set to `NULL` and available again.

Please use `.actives()` queryset method instead of `.all()`. Why? `.all()`
method is untouched and works as default. When `all()` called, returning
queryset set contains everything event if the `deleted_at` is NULL or not...

## Examples

```python
>>> Post.objects.all()

SELECT "blog_post"."id",
       "blog_post"."created_at",
       "blog_post"."updated_at",
       "blog_post"."deleted_at",
       "blog_post"."author_id",
       "blog_post"."category_id",
       "blog_post"."title",
       "blog_post"."body"
  FROM "blog_post"
 LIMIT 21


Execution time: 0.000950s [Database: default]

<CustomBaseModelWithSoftDeleteQuerySet [
    <Post: Python post 1>, 
    <Post: Python post 2>, 
    <Post: Python post 3>, 
    <Post: Python post 4>,
    :
    :
    :
    <Post: Golang post 4>
]>

>>> Category.objects.all()

SELECT "blog_category"."id",
       "blog_category"."created_at",
       "blog_category"."updated_at",
       "blog_category"."deleted_at",
       "blog_category"."title"
  FROM "blog_category"
 LIMIT 21


Execution time: 0.000643s [Database: default]

<CustomBaseModelWithSoftDeleteQuerySet [<Category: Python>, <Category: Ruby>, <Category: Bash>, <Category: Golang>]>

>>> Tag.objects.all()

SELECT "blog_tag"."id",
       "blog_tag"."created_at",
       "blog_tag"."updated_at",
       "blog_tag"."deleted_at",
       "blog_tag"."name"
  FROM "blog_tag"
 LIMIT 21


Execution time: 0.000519s [Database: default]

<CustomBaseModelWithSoftDeleteQuerySet [<Tag: textmate>, <Tag: pyc>, <Tag: irb>, <Tag: ipython>, <Tag: lock>, <Tag: environment>]>

>>> Category.objects.get(title='Bash').delete()
(9, {'blog.Post_tags': 4, 'blog.Category': 1, 'blog.Post': 4})

>>> Category.objects.delete()
(11, {'blog.Post_tags': 4, 'blog.Category': 3, 'blog.Post': 4})

>>> Category.objects.inactives()

SELECT "blog_category"."id",
       "blog_category"."created_at",
       "blog_category"."updated_at",
       "blog_category"."deleted_at",
       "blog_category"."title"
  FROM "blog_category"
 WHERE "blog_category"."deleted_at" IS NOT NULL
 LIMIT 21


Execution time: 0.000337s [Database: default]

<CustomBaseModelWithSoftDeleteQuerySet [<Category: Bash>]>

>>> Post.objects.inactives()

SELECT "blog_post"."id",
       "blog_post"."created_at",
       "blog_post"."updated_at",
       "blog_post"."deleted_at",
       "blog_post"."author_id",
       "blog_post"."category_id",
       "blog_post"."title",
       "blog_post"."body"
  FROM "blog_post"
 WHERE "blog_post"."deleted_at" IS NOT NULL
 LIMIT 21


Execution time: 0.000387s [Database: default]

<CustomBaseModelWithSoftDeleteQuerySet [<Post: Bash post 1>, <Post: Bash post 2>, <Post: Bash post 3>, <Post: Bash post 4>]>

>>> Category.objects.inactives().undelete()
(9, {'blog.Post_tags': 4, 'blog.Category': 1, 'blog.Post': 4})

>>> Category.objects.inactives()
<CustomBaseModelWithSoftDeleteQuerySet []>

>>> Post.objects.inactives()
<CustomBaseModelWithSoftDeleteQuerySet []>
```

`CustomBaseModelWithSoftDeleteQuerySet` has these query options:

- `.actives()` : filters if `CustomBaseModelWithSoftDelete.deleted_at` is set to `NULL`
- `.inactives()` : filters if `CustomBaseModelWithSoftDelete.deleted_at` is not set to `NULL`
- `.delete()` : soft delete on given object/queryset.
- `.undelete()` : recover soft deleted on given object/queryset.
- `.hard_delete()` : this is real delete. this method erases given object/queryset and there is no turning back!.

When soft-delete enabled (*during model creation*), Django admin will
automatically use `CustomBaseModelAdminWithSoftDelete` which is inherited from:
 `CustomBaseModelAdmin` <- `admin.ModelAdmin`.
