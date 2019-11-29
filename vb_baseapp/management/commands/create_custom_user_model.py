import os
from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.core.management.base import CommandError

from ..base import CustomBaseCommand, get_need_model_names
from ..template_structures.models import custom_user

# TEMPLATE_CLASS_HEADERS = {
#     'django': custom_user.TEMPLATE_CUSTOM_USER_MODEL_DJANGO_CLASS_HEADER,
#     'basemodel': custom_user.TEMPLATE_CUSTOM_USER_MODEL_BASEMODEL_CLASS_HEADER,
#     'softdelete': custom_user.TEMPLATE_CUSTOM_USER_MODEL_SOFTDELETE_BASEMODEL_CLASS_HEADER,
# }


class Command(CustomBaseCommand):
    help = 'Creates custom User model with given model name'  # noqa: A003

    MODEL_TYPE_CHOISES = ['django', 'basemodel', 'softdelete']

    def add_arguments(self, parser):
        parser.add_argument('app_name', nargs=1, type=str, help='Name of your application')
        parser.add_argument('model_name', nargs=1, type=str, help='Name of your model')
        parser.add_argument(
            'model_type', nargs='?', default='django', choices=self.MODEL_TYPE_CHOISES, help='Type of your model'
        )

    def handle(self, *args, **options):
        app_name = options.pop('app_name')[0]
        model_name = options.pop('model_name')[0]
        model_type = options.pop('model_type')

        model_name_for_file, model_name_for_class, model_name_for_verbose_name = get_need_model_names(model_name)

        # self.out(app_name)
        # self.out(model_name)
        # self.out(model_type)
        # self.out(model_name_for_file)
        # self.out(model_name_for_class)
        # self.out(model_name_for_verbose_name)

        try:
            import_module(app_name)
        except ImportError:
            raise CommandError('%s does not exists. Please pass existing application name.' % app_name)

        if model_name_for_file in [model.__name__.lower() for model in apps.get_app_config(app_name).get_models()]:
            raise CommandError(
                '%s model is already exists in %s. Please try non-existing model name.' % (model_name, app_name)
            )

        app_dir = os.path.join(settings.BASE_DIR, 'applications', app_name)

        selected_model_class_name = ''
        selected_model_class_name_for_import = ''
        created_at_and_updated_at = f'    {custom_user.TEMPLATE_CUSTOM_USER_MODEL_DJANGO_CREATED_AT}'
        required_class_header = custom_user.TEMPLATE_CUSTOM_USER_MODEL_DJANGO_CLASS_HEADER.format(
            model_name_for_class=model_name_for_class
        )
        if model_type in ['basemodel', 'softdelete']:
            created_at_and_updated_at = ''
            if model_type == 'basemodel':
                selected_model_class_name = 'CustomBaseModel'
            else:
                selected_model_class_name = 'CustomBaseModelWithSoftDelete'
            selected_model_class_name_for_import = f'\nfrom vb_baseapp.models import {selected_model_class_name}'
            required_class_header = custom_user.TEMPLATE_CUSTOM_USER_MODEL_CUSTOM_CLASS_HEADER.format(
                model_name_for_class=model_name_for_class, selected_model_class_name=selected_model_class_name
            )

        content_model_file = custom_user.TEMPLATE_CUSTOM_USER_MODEL.format(
            selected_model_class_name_for_import=selected_model_class_name_for_import,
            model_name_for_class=model_name_for_class,
            model_manager=custom_user.TEMPLATE_CUSTOM_USER_MODEL_MANAGER.format(
                model_name_for_class=model_name_for_class
            ),
            class_header=required_class_header,
            created_at_and_updated_at=created_at_and_updated_at,
            app_name=app_name,
            model_name_for_verbose_name=model_name_for_verbose_name,
        )
        self.out(content_model_file)

        # content_model_file = custom_user.TEMPLATE_CUSTOM_USER_MODEL.format(
        #
        # )
        # self.out(TEMPLATE_CLASS_HEADERS[model_type])
