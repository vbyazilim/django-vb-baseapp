# pylint: disable=C0301

"""
Custom User Model template
"""

TEMPLATE_CUSTOM_USER_MODEL_MANAGER = """class {model_name_for_class}Manager(BaseUserManager{softdelete_manager_name}):
    use_in_migrations = True

    def create_user(self, email, first_name, last_name, middle_name=None, password=None):
        if not email:
            raise ValueError(_('user must have an email address'))

        user_create_fields = {{'email': email, 'first_name': first_name, 'last_name': last_name}}

        if middle_name:
            user_create_fields['middle_name'] = middle_name

        user = self.model(**user_create_fields)
        user.set_password(password)
        user.save(using=self._db)
        logger.info('%s created successfully. PK: %d', user.get_full_name(), user.pk)
        return user

    def create_superuser(self, email, first_name, last_name, middle_name=None, password=None):
        user = self.create_user(email, first_name, last_name, middle_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        logger.info('%s is set to superuser. PK: %d', user.get_full_name(), user.pk)
        return user
"""

TEMPLATE_CUSTOM_USER_MODEL_DJANGO_CLASS_HEADER = (
    """class {model_name_for_class}(AbstractBaseUser, PermissionsMixin):"""
)
TEMPLATE_CUSTOM_USER_MODEL_CUSTOM_CLASS_HEADER = (
    """class {model_name_for_class}(AbstractBaseUser, PermissionsMixin, {selected_model_class_name}):"""
)

TEMPLATE_CUSTOM_USER_MODEL_DJANGO_CREATED_AT = """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('updated at'))"""

TEMPLATE_CUSTOM_USER_MODEL = """# pylint: disable=R0913

import logging

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import ugettext_lazy as _

from console import console
{selected_model_class_name_for_import}{softdelete_manager_import}
from vb_baseapp.utils import save_file as custom_save_file

__all__ = ['{model_name_for_class}']

logger = logging.getLogger('app')
console = console(source=__name__)


{model_manager}

def save_user_profile_image(instance, filename):
    return custom_save_file(instance, filename, upload_to='profile_images/')


{class_header}

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
{created_at_and_updated_at}
    email = models.EmailField(unique=True, verbose_name=_('email address'))
    first_name = models.CharField(max_length=255, verbose_name=_('first name'))
    middle_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('middle name'))
    last_name = models.CharField(max_length=255, verbose_name=_('last name'))
    profile_image = models.FileField(
        upload_to=save_user_profile_image, verbose_name=_('profile image'), null=True, blank=True
    )
    is_active = models.BooleanField(default=True, verbose_name=_('active'))
    is_staff = models.BooleanField(default=False, verbose_name=_('staff status'))

    objects = {model_name_for_class}Manager()

    class Meta:
        app_label = '{app_name}'
        verbose_name = _('{model_name_for_verbose_name}')
        verbose_name_plural = _('{model_name_for_verbose_name}s')  # check pluralization

    def __str__(self):
        return self.get_full_name()

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        params = {{'first_name': self.first_name, 'middle_name': ' ', 'last_name': self.last_name}}
        if self.middle_name:
            params['middle_name'] = ' {{middle_name}} '.format(middle_name=self.middle_name)
        full_name = '{{first_name}}{{middle_name}}{{last_name}}'.format(**params)
        return full_name.strip()

"""

__all__ = [
    'TEMPLATE_CUSTOM_USER_MODEL_MANAGER',
    'TEMPLATE_CUSTOM_USER_MODEL_DJANGO_CLASS_HEADER',
    'TEMPLATE_CUSTOM_USER_MODEL_CUSTOM_CLASS_HEADER',
    'TEMPLATE_CUSTOM_USER_MODEL_DJANGO_CREATED_AT',
    'TEMPLATE_CUSTOM_USER_MODEL',
]
