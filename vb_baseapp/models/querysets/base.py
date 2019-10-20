import logging

from django.db import models

from console import console

__all__ = ['CustomBaseModelWithSoftDeleteQuerySet']

console = console(source=__name__)
logger = logging.getLogger('app')


class CustomBaseModelWithSoftDeleteQuerySet(models.QuerySet):
    def actives(self):
        return self.filter(deleted_at__isnull=True)

    def inactives(self):
        return self.filter(deleted_at__isnull=False)

    def delete(self):
        return self._delete_or_undelete()

    def hard_delete(self):
        return super().delete()

    def undelete(self):
        return self._delete_or_undelete(undelete=True)

    def _delete_or_undelete(self, undelete=False):
        processed_instances = {}
        call_method = 'undelete' if undelete else 'delete'

        for model_instance in self:
            _count, model_information = getattr(model_instance, call_method)()
            for (app_label, row_amount) in model_information.items():
                processed_instances.setdefault(app_label, 0)
                processed_instances[app_label] = processed_instances[app_label] + row_amount
        return (sum(processed_instances.values()), processed_instances)
