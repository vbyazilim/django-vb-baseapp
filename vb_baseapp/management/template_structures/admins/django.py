"""
Django Model template for model generator
"""

TEMPLATE_ADMIN_DJANGO = """import logging

from django.contrib import admin

from console import console

from ..models import {model_name_for_class}

__all__ = ['{model_name_for_class}Admin']

logger = logging.getLogger('app')
console = console(source=__name__)


@admin.register({model_name_for_class})
class {model_name_for_class}Admin(admin.ModelAdmin):
    pass

"""


__all__ = ['TEMPLATE_ADMIN_DJANGO']
