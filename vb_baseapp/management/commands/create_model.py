# pylint: disable=R0201,R0914

import os
from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.core.management.base import (
    CommandError,
    no_translations,
)

from ..base import (
    CustomBaseCommandWithFileTools,
    get_need_model_names,
)
from ..template_structures import admins as admin_templates
from ..template_structures import models as model_templates

TEMPLATE_MODELS = {
    'django': model_templates.TEMPLATE_MODEL_DJANGO,
    'basemodel': model_templates.TEMPLATE_MODEL_BASEMODEL,
    'softdelete': model_templates.TEMPLATE_MODEL_SOFTDELETEMODEL,
}

TEMPLATE_ADMINS = {
    'django': admin_templates.TEMPLATE_ADMIN_DJANGO,
    'basemodel': admin_templates.TEMPLATE_ADMIN_BASEMODEL,
    'softdelete': admin_templates.TEMPLATE_ADMIN_SOFTDELETEMODEL,
}

USER_REMINDER = """

    `{model_name_for_class}` related files created successfully:

    - `{app_name}/models/{model_name_for_file}.py`
    - `{app_name}/admin/{model_name_for_file}.py`

    Please check your models before running `makemigrations` ok?

"""


class Command(CustomBaseCommandWithFileTools):
    help = 'Creates models/MODEL.py, admin/MODEL.py for given application'  # noqa: A003

    MODEL_TYPE_CHOISES = ['django', 'basemodel', 'softdelete']

    def add_arguments(self, parser):
        parser.add_argument('app_name', nargs=1, type=str, help='Name of your application')
        parser.add_argument('model_name', nargs=1, type=str, help='Name of your model')
        parser.add_argument(
            'model_type', nargs='?', default='django', choices=self.MODEL_TYPE_CHOISES, help='Type of your model'
        )

    @no_translations
    def handle(self, *args, **options):
        app_name = options.pop('app_name')[0]
        model_name = options.pop('model_name')[0]
        model_type = options.pop('model_type')

        model_name_for_file, model_name_for_class, model_name_for_verbose_name = get_need_model_names(model_name)

        try:
            import_module(app_name)
        except ImportError:
            raise CommandError('%s does not exists. Please pass existing application name.' % app_name)

        if model_name.lower() in [model.__name__.lower() for model in apps.get_app_config(app_name).get_models()]:
            raise CommandError(
                '%s model is already exists in %s. Please try non-existing model name.' % (model_name, app_name)
            )

        app_dir = os.path.join(settings.BASE_DIR, 'applications', app_name)

        model_file = os.path.join(app_dir, 'models', f'{model_name_for_file}.py')
        model_init_file = os.path.join(app_dir, 'models', '__init__.py')

        admin_file = os.path.join(app_dir, 'admin', f'{model_name_for_file}.py')
        admin_init_file = os.path.join(app_dir, 'admin', '__init__.py')

        content_model_file = TEMPLATE_MODELS[model_type].format(
            model_name_for_class=model_name_for_class,
            app_name=app_name,
            model_name_for_verbose_name=model_name_for_verbose_name,
        )
        content_init_file = f'from .{model_name_for_file} import *\n'
        content_admin_file = TEMPLATE_ADMINS[model_type].format(model_name_for_class=model_name_for_class)

        self.create_or_modify_file(model_file, content_model_file)
        self.out(f'models/{os.path.basename(model_file)} created.')

        self.create_or_modify_file(admin_file, content_admin_file)
        self.out(f'admin/{os.path.basename(admin_file)} created.')

        self.create_or_modify_file(model_init_file, content_init_file, 'a')
        self.out(f'{model_name} model added to models/__init__.py')

        self.create_or_modify_file(admin_init_file, content_init_file, 'a')
        self.out(f'{model_name} model added to admin/__init__.py')

        self.out(
            USER_REMINDER.format(
                app_name=app_name, model_name_for_class=model_name_for_class, model_name_for_file=model_name_for_file
            ),
            'n',
        )
