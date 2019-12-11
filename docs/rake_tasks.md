You have some handy rake tasks if you like to use `ruby` :)

```bash
$ rake -T

rake db:migrate[database]                                        # Run migration for given database (default: 'default')
rake db:roll_back[name_of_application,name_of_migration]         # Roll-back (name of application, name of migration)
rake db:shell                                                    # run database shell ..
rake db:show[name_of_application]                                # Show migrations for an application (default: 'all')
rake db:update[name_of_application,name_of_migration,is_empty]   # Update migration (name of application, name of migration?, is empty?)
rake default                                                     # Default task: runserver_plus (Werkzeug)
rake locale:compile                                              # Compile locale dictionary
rake locale:update                                               # Update locale dictionary
rake new:application[name_of_application]                        # Create new Django application
rake new:model[name_of_application,name_of_model,type_of_model]  # Create new Model for given application: django,basemodel,softdelete
rake runserver:default                                           # Run: runserver (Django's default server)
rake runserver:default_ipdb                                      # Run: runserver (Django's default server) + ipdb debug support
rake runserver:plus                                              # Run: runserver_plus (Werkzeug)
rake runserver:plus_ipdb                                         # Run: runserver_plus (Werkzeug) + ipdb debug support
rake shell[repl]                                                 # Run shell+ avail: ptpython,ipython,bpython default: ptpython
rake test:browse_coverage[port]                                  # Browse test coverage
rake test:coverage[cli_args]                                     # Show test coverage (default: '--show-missing --ignore-errors --skip-covered')
rake test:run[name_of_application,verbose]                       # Run tests for given application
```

Default task is `runserver:plus`. Just type `rake` that’s it! `runserver:plus` uses
`runserver_plus`. This means you have lots of debugging options!

## `runserver` based tasks

- `rake runserver:default`: runs `python manage.py runserver`
- `rake runserver:default_ipdb`: runs Django’s default server with debugging
  feature. You can inject `breakpoint()` in your code! Debugger kicks in!
- `rake runserver:plus`: runs `python manage.py runserver_plus --nothreading`
- `rake runserver:plus_ipdb`: runs `runserver:plus` with debugging!

## `rake db:migrate[database]`

Migrates database with given database name. Default is `default`. If you like
to work multiple databases:

```python
# example configuration

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db', 'development.sqlite3'),
    },
    'my_database': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db', 'my_database.sqlite3'),
    }
}
```

You can just call `rake db:migrate` or specify different database like: 
`rake db:migrate[my_database]` :)

## `rake db:show[name_of_application]`

Show migration information:

```bash
$ rake db:show[blog]
blog
 [X] 0001_create_post_category_and_tag
 [ ] 0002_add_spot_field_to_post

$ rake db:migrate
Running migration for: default database...
Operations to perform:
  Apply all migrations: admin, auth, blog, contenttypes, sessions
Running migrations:
  Applying blog.0002_add_spot_field_to_post... OK
```

## `rake db:roll_back[name_of_application,name_of_migration]`

Your database must be rollable :) To see available migrations: 
`rake db:roll_back[NAME_OF_YOUR_APPLICATION]`. Look at the list and choose your
target migration. You can use just the number as shortcut. In this example,
we’ll roll back to migration number 1, which has a name: `0001_create_post_category_and_tag`

```bash
$ rake db:roll_back[blog]
Please select your migration:
blog
 [X] 0001_create_post_category_and_tag
 [X] 0002_add_spot_field_to_post

$ rake db:roll_back[blog,1]
Operations to perform:
  Target specific migration: 0001_create_post_category_and_tag, from blog
Running migrations:
  Rendering model states... DONE
  Unapplying blog.0002_add_spot_field_to_post... OK

$ rake db:show[blog]
blog
 [X] 0001_create_post_category_and_tag
 [ ] 0002_add_spot_field_to_post
```

## `rake db:update[name_of_application,name_of_migration,is_empty]`

When you add/change something in your model, you need to create migrations.
Let’s say you have added new field to `Post` model in your `blog` app:

If you don’t provide `name_of_migration` param, you’ll endup with auto
generated name such as `000X_auto_YYYMMDD_HHMM`. You can also create
empty migration via 3^rd parameter: `yes`

```bash
$ rake db:update[blog,add_spot_field_to_post]
Migrations for 'blog':
  applications/blog/migrations/0002_add_spot_field_to_post.py
    - Add field spot to post

$ rake db:update[blog,add_new_field_to_post,yes]  # empty migration example
Migrations for 'blog':
  applications/blog/migrations/0003_add_new_field_to_post.py

$ cat applications/blog/migrations/0003_add_new_field_to_post.py
```

empty migration output:

```python
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_add_spot_field_to_post'),
    ]

    operations = [
    ]
```

## `rake db:shell`

Runs default database client.

## `rake new:application[name_of_application]`

Creates new application with given application name!

```bash
$ rake new:application[blog]
```

## `rake new:model[name_of_application,name_of_model,type_of_model]`

Creates new model! Available model types are:

- `django` (default),
- `basemodel`
- `softdelete`

```bash
$ rake new:model[blog,Post]                # will create model using Django’s `models.Model`
$ rake new:model[blog,Post,basemodel]      # will create model using our `CustomBaseModel`
$ rake new:model[blog,Post,softdelete]     # will create model using our `CustomBaseModelWithSoftDelete`
```

## `rake locale:compile` and `rake locale:update`

When you make changes in your application related to locales, run: `rake locale:update`.
When you finish editing your `django.po` file, run `rake locale:compile`.

## `rake shell[repl]`

Runs Django repl/shell with use `shell_plus` of [django-extensions][01].
 `rake shell`. This loads everything to your shell! Also you can see the
SQL statements while playing in shell. We have couple different repls:

1. `ptpython`
1. `bpython`
1. `ipython`

Default repl is: `ptpython`

```bash
$ rake shell
$ rake shell[bpython]
$ rake shell[ipython]
```

## `rake test:run[name_of_application,verbose]`

If you don’t provide `name_of_application` default value will be `applications`. 
`verbose` is `1` by default.

Examples:

```bash
$ rake test:run
$ rake test:run[vb_baseapp,2]
```

## `rake test:coverage[cli_args]`

Get the test report. Default is `--show-missing --ignore-errors --skip-covered` for
`cli_args` parameter.

```bash
$ rake test:coverage
```

## `rake test:browse_coverage[port]`

Serves generated html coverages under `htmlcov` folder via `python`. Default port
is `9001`

---

### Run Tests Manually

```bash
$ DJANGO_ENV=test python manage.py test vb_baseapp -v 2                                 # or
$ DJANGO_ENV=test python manage.py test vb_baseapp.tests.test_user.CustomUserTestCase   # run single unit
$ rake test:run[vb_baseapp]
```
