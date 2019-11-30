import logging

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import (
    UserAdmin as DjangoUserAdmin,
)

from console import console

__all__ = ['UserAdmin']

console = console(source=__name__)
logger = logging.getLogger('app')

USER = get_user_model()


class UserAdmin(DjangoUserAdmin):
    list_filter = ['is_staff', 'is_superuser']
    autocomplete_fields = ['groups', 'user_permissions']


if USER._meta.label_lower == 'auth.user':  # pylint: disable=W0212
    admin.site.unregister(USER)
    admin.site.register(USER, UserAdmin)
