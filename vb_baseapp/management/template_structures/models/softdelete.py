"""
CustomBaseModelWithSoftDelete template for model generator
"""

TEMPLATE_MODEL_SOFTDELETEMODEL = """import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from console import console
from vb_baseapp.models import CustomBaseModelWithSoftDelete

__all__ = ['{model_name_for_class}']

logger = logging.getLogger('app')
console = console(source=__name__)


class {model_name_for_class}(CustomBaseModelWithSoftDelete):
    title = models.CharField(max_length=255, verbose_name=_('title'))

    class Meta:
        app_label = '{app_name}'
        verbose_name = _('{model_name_for_verbose_name}')
        verbose_name_plural = _('{model_name_for_verbose_name}s')  # check pluralization

    def __str__(self):
        return self.title

"""


__all__ = ['TEMPLATE_MODEL_SOFTDELETEMODEL']
