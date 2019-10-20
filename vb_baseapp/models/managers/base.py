import logging

from django.db import models

from console import console

from ..querysets import (
    CustomBaseModelWithSoftDeleteQuerySet,
)

__all__ = ['CustomBaseModelWithSoftDeleteManager']

console = console(source=__name__)
logger = logging.getLogger('app')


class CustomBaseModelWithSoftDeleteManager(models.Manager):
    def get_queryset(self):
        return CustomBaseModelWithSoftDeleteQuerySet(self.model, using=self._db)

    def inactives(self):
        return self.get_queryset().inactives()

    def actives(self):
        return self.get_queryset().actives()

    def delete(self):
        return self.get_queryset().delete()

    def undelete(self):
        return self.inactives().undelete()

    def hard_delete(self):
        return self.get_queryset().hard_delete()
