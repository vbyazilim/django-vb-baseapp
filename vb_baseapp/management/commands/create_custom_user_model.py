# pylint: disable=R0914, R0915, E1101

import errno
import os
from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.core.management.base import (
    CommandError,
    no_translations,
)
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor

from console import console

from ..base import (
    CustomBaseCommandWithFileTools,
    get_need_model_names,
)
from ..template_structures.admins import (
    custom_user as custom_user_admin_template,
)
from ..template_structures.forms import (
    custom_user as custom_user_admin_form_template,
)
from ..template_structures.models import (
    custom_user as custom_user_model_template,
)

console = console(source=__name__)


def is_database_synchronized(database):
    connection = connections[database]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return not executor.migration_plan(targets)


COMMAND_SUCCESS_MESSAGE = """
Custom user installation completed. Now please check your;

    - {app_name}/models/{model_name_for_file}.py
    - {app_name}/admin/{model_name_for_file}.py
    - {app_name}/admin/forms/{model_name_for_file}.py

Also;

    - `email` field is set to `USERNAME_FIELD`
    - `first_name` and `last_name` are set as `REQUIRED_FIELDS`
    - `middle_name`, `profile_image` are optionals

Make sure if all ok? Make your changes before running migrations:

    $ python manage.py makemigrations --name create_custom_users

"""


class Command(CustomBaseCommandWithFileTools):
    help = 'Creates custom User model with given model name'  # noqa: A003

    MODEL_TYPE_CHOISES = ['django', 'basemodel', 'softdelete']

    def add_arguments(self, parser):
        parser.add_argument('app_name', nargs=1, type=str, help='Name of your application')
        parser.add_argument('model_name', nargs=1, type=str, help='Name of your model')
        parser.add_argument(
            'model_type', nargs='?', default='django', choices=self.MODEL_TYPE_CHOISES, help='Type of your model'
        )

    @no_translations
    def handle(self, *args, **options):
        if is_database_synchronized(DEFAULT_DB_ALIAS):
            raise CommandError('sorry, you are in the middle of the project, this command works only in fresh start')

        app_name = options.pop('app_name')[0]
        model_name = options.pop('model_name')[0]
        model_type = options.pop('model_type')

        model_name_for_file, model_name_for_class, model_name_for_verbose_name = get_need_model_names(model_name)

        try:
            import_module(app_name)
        except ImportError:
            raise CommandError('%s does not exists. Please pass existing application name.' % app_name)

        if model_name_for_file in [model.__name__.lower() for model in apps.get_app_config(app_name).get_models()]:
            raise CommandError(
                '%s model is already exists in %s. Please try non-existing model name.' % (model_name, app_name)
            )

        app_dir = os.path.join(settings.BASE_DIR, 'applications', app_name)
        config_file = os.path.join(settings.BASE_DIR, 'config', 'settings', 'base.py')

        selected_model_class_name = ''
        selected_model_class_name_for_import = ''
        created_at_and_updated_at = f'    {custom_user_model_template.TEMPLATE_CUSTOM_USER_MODEL_DJANGO_CREATED_AT}'
        required_class_header = custom_user_model_template.TEMPLATE_CUSTOM_USER_MODEL_DJANGO_CLASS_HEADER.format(
            model_name_for_class=model_name_for_class
        )
        softdelete_manager_name = ''
        softdelete_manager_import = ''
        comma_prefix = ''
        if model_type in ['basemodel', 'softdelete']:
            created_at_and_updated_at = ''
            comma_prefix = ', '
            if model_type == 'basemodel':
                selected_model_class_name = 'CustomBaseModel'
            else:
                selected_model_class_name = 'CustomBaseModelWithSoftDelete'
                softdelete_manager_name = 'CustomBaseModelWithSoftDeleteManager'
                softdelete_manager_import = (
                    f'\nfrom vb_baseapp.models.managers import (\n    {softdelete_manager_name},\n)'
                )
            selected_model_class_name_for_import = f'\nfrom vb_baseapp.models import {selected_model_class_name}'
            required_class_header = custom_user_model_template.TEMPLATE_CUSTOM_USER_MODEL_CUSTOM_CLASS_HEADER.format(
                model_name_for_class=model_name_for_class, selected_model_class_name=selected_model_class_name
            )

        content_model_file = custom_user_model_template.TEMPLATE_CUSTOM_USER_MODEL.format(
            selected_model_class_name_for_import=selected_model_class_name_for_import,
            model_name_for_class=model_name_for_class,
            model_manager=custom_user_model_template.TEMPLATE_CUSTOM_USER_MODEL_MANAGER.format(
                model_name_for_class=model_name_for_class,
                softdelete_manager_name=f'{comma_prefix}{softdelete_manager_name}',
            ),
            class_header=required_class_header,
            created_at_and_updated_at=created_at_and_updated_at,
            app_name=app_name,
            model_name_for_verbose_name=model_name_for_verbose_name,
            softdelete_manager_import=softdelete_manager_import,
        )

        model_file = os.path.join(app_dir, 'models', f'{model_name_for_file}.py')
        model_init_file = os.path.join(app_dir, 'models', '__init__.py')
        content_init_file = f'from .{model_name_for_file} import *\n'

        admin_file = os.path.join(app_dir, 'admin', f'{model_name_for_file}.py')
        admin_init_file = os.path.join(app_dir, 'admin', '__init__.py')

        admin_forms_folder = os.path.join(app_dir, 'admin', 'forms')
        admin_forms_folder_init_file = os.path.join(app_dir, 'admin', 'forms', '__init__.py')

        required_class_header_for_admin = custom_user_admin_template.TEMPLATE_ADMIN_CUSTOM_USER_MODEL_DJANGO_CLASS_HEADER.format(  # noqa: E501 pylint: disable=C0301
            model_name_for_class=model_name_for_class
        )
        selected_model_admin_class_name_for_import = ''
        selected_model_admin_class_import = ''

        if model_type in ['basemodel', 'softdelete']:
            if model_type == 'basemodel':
                selected_model_admin_class_name_for_import = 'CustomBaseModelAdmin'
            else:
                selected_model_admin_class_name_for_import = 'CustomBaseModelAdminWithSoftDelete'
            selected_model_admin_class_import = custom_user_admin_template.TEMPLATE_ADMIN_CUSTOM_USER_MODEL_ADMIN_IMPORT.format(  # noqa: E501 pylint: disable=C0301
                model_based_model_admin=selected_model_admin_class_name_for_import
            )
            required_class_header_for_admin = custom_user_admin_template.TEMPLATE_ADMIN_CUSTOM_USER_MODEL_CUSTOM_CLASS_HEADER.format(  # noqa: E501 pylint: disable=C0301
                model_name_for_class=model_name_for_class,
                model_based_model_admin=selected_model_admin_class_name_for_import,
            )

        content_model_admin_file = custom_user_admin_template.TEMPLATE_ADMIN_CUSTOM_USER_MODEL.format(
            selected_model_admin_class_import=selected_model_admin_class_import,
            model_name_for_class=model_name_for_class,
            class_header=required_class_header_for_admin,
        )

        content_admin_form_file = custom_user_admin_form_template.TEMPLATE_CUSTOM_USER_ADMIN_FORMS.format(
            model_name_for_class=model_name_for_class
        )

        config_file_content = None
        with open(config_file, 'r') as file_pointer:
            config_file_content = file_pointer.readlines()

        if not config_file_content:
            raise CommandError("Couldn't open config file...")

        found_index = -1
        for index, line in enumerate(config_file_content):
            if 'AUTH_USER_MODEL' in line:
                found_index = index
        if found_index < 0:
            raise CommandError(
                "Couldn't find required line in config. Config should contain:\n\n# AUTH_USER_MODEL = ..."
            )

        config_file_content[found_index] = f"AUTH_USER_MODEL = '{app_name}.{model_name_for_class}'\n"

        self.create_file_with_content(config_file, ''.join(config_file_content))
        self.out('Set AUTH_USER_MODEL in config file')

        self.create_or_modify_file(model_file, content_model_file)
        self.out(f'models/{os.path.basename(model_file)} created.')

        self.create_or_modify_file(admin_file, content_model_admin_file)
        self.out(f'admin/{os.path.basename(admin_file)} created.')

        self.create_or_modify_file(model_init_file, content_init_file, 'a')
        self.out(f'{model_name_for_class} model added to models/__init__.py', 'n')

        self.create_or_modify_file(admin_init_file, content_init_file, 'a')
        self.out(f'{model_name_for_class} model added to admin/__init__.py', 'n')

        try:
            self.make_directory(admin_forms_folder)
        except CommandError as e:  # pylint: disable=C0103
            if e.errno != errno.EEXIST:
                raise e

        self.create_or_modify_file(admin_forms_folder_init_file, content_init_file, 'a')
        self.out(f'{model_name_for_class} forms added to admin/forms/__init__.py', 'n')

        admin_form_file = os.path.join(app_dir, 'admin', 'forms', f'{model_name_for_file}.py')
        self.create_or_modify_file(admin_form_file, content_admin_form_file)
        self.out(f'admin/forms/{os.path.basename(admin_form_file)} created.')
        self.out(COMMAND_SUCCESS_MESSAGE.format(app_name=app_name, model_name_for_file=model_name_for_file))
