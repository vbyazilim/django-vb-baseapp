# flake8: noqa: E501

"""
Custom User Model Admin temolate
"""

TEMPLATE_ADMIN_CUSTOM_USER_MODEL_ADMIN_IMPORT = """\nfrom vb_baseapp.admin import (
    {model_based_model_admin},
)"""

TEMPLATE_ADMIN_CUSTOM_USER_MODEL_DJANGO_CLASS_HEADER = """class {model_name_for_class}Admin(BaseUserAdmin):"""
TEMPLATE_ADMIN_CUSTOM_USER_MODEL_CUSTOM_CLASS_HEADER = (
    """class {model_name_for_class}Admin(BaseUserAdmin, {model_based_model_admin}):"""
)


TEMPLATE_ADMIN_CUSTOM_USER_MODEL = """from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
)
from django.db import models
from django.utils.translation import ugettext_lazy as _

from console import console
{selected_model_admin_class_import}
from vb_baseapp.admin.widgets import AdminImageFileWidget

from .forms import (
    {model_name_for_class}ChangeForm,
    {model_name_for_class}CreationForm,
)

__all__ = ['{model_name_for_class}Admin']

console = console(source=__name__)


CUSTOM_USER = get_user_model()


@admin.register(CUSTOM_USER)
{class_header}

    form = {model_name_for_class}ChangeForm
    add_form = {model_name_for_class}CreationForm
    autocomplete_fields = ['groups', 'user_permissions']
    list_display = ('email', 'first_name', 'last_name')
    list_display_links = ('email',)
    search_fields = ('email', 'first_name', 'middle_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (_('user information'), {{'fields': ('email', 'password', 'first_name', 'middle_name', 'last_name', 'profile_image')}}),
        (_('permissions'), {{'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}}),
    )
    add_fieldsets = (
        (None, {{'classes': ('wide',), 'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}}),
    )
    formfield_overrides = {{models.FileField: {{'widget': AdminImageFileWidget}}}}

"""

__all__ = [
    'TEMPLATE_ADMIN_CUSTOM_USER_MODEL_ADMIN_IMPORT',
    'TEMPLATE_ADMIN_CUSTOM_USER_MODEL_DJANGO_CLASS_HEADER',
    'TEMPLATE_ADMIN_CUSTOM_USER_MODEL_CUSTOM_CLASS_HEADER',
    'TEMPLATE_ADMIN_CUSTOM_USER_MODEL',
]
