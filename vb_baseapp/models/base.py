# pylint: disable=W0212,W0143,R0201,R0912,E1101

import logging
from collections import Counter

from django.db import models, router, transaction
from django.db.models.deletion import Collector
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from console import console

from .managers import CustomBaseModelWithSoftDeleteManager
from .signals import post_undelete, pre_undelete

__all__ = ['CustomBaseModel', 'CustomBaseModelWithSoftDelete']

console = console(source=__name__)
logger = logging.getLogger('app')


class CustomBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:  # pylint: disable=R0903
        abstract = True


class CustomBaseModelWithSoftDelete(CustomBaseModel):
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Deleted At'))

    objects = CustomBaseModelWithSoftDeleteManager()

    class Meta:  # pylint: disable=R0903
        abstract = True

    @property
    def is_deleted(self):
        return bool(self.deleted_at)

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def delete(self, using=None, keep_parents=False):
        using = using or router.db_for_write(self.__class__, instance=self)
        return self._soft_delete(using=using, keep_parents=keep_parents)

    def undelete(self, using=None, keep_parents=False):
        using = using or router.db_for_write(self.__class__, instance=self)
        return self._undelete(using=using, keep_parents=keep_parents)

    def _collect_related(self, using=None, keep_parents=False):
        collector = Collector(using=using)
        collector.collect([self], keep_parents=keep_parents)
        fast_deletes = []
        for queryset in collector.fast_deletes:
            if queryset.count() > 0:
                fast_deletes.append(queryset)

        return dict(
            instances_with_model=collector.instances_with_model(), fast_deletes=fast_deletes, data=collector.data
        )

    def _undelete(self, using=None, keep_parents=False):
        return self._soft_delete(using=using, keep_parents=keep_parents, undelete=True)

    def _soft_delete(self, using=None, keep_parents=False, undelete=False):  # pylint: disable=R0914
        items = self._collect_related(using=using, keep_parents=keep_parents)
        deleted_counter = Counter()

        required_pre_signal = models.signals.pre_delete
        required_post_signal = models.signals.post_delete
        required_deleted_at = timezone.now()

        if undelete:
            required_pre_signal = pre_undelete
            required_post_signal = post_undelete
            required_deleted_at = None
        with transaction.atomic(using=using, savepoint=False):

            # pre signal...
            for model, obj in items.get('instances_with_model'):
                if not model._meta.auto_created:
                    required_pre_signal.send(sender=model, instance=obj, using=using)

            # fast deletes-ish
            for queryset in items.get('fast_deletes'):
                count = queryset.count()

                if issubclass(queryset.model, CustomBaseModelWithSoftDelete):
                    # this happens in database layer...
                    # try to mark as deleted if the model is inherited from
                    # CustomBaseModelWithSoftDelete
                    count = queryset.update(deleted_at=required_deleted_at)
                else:
                    skip_raw_delete = False
                    for field in queryset.model._meta.fields:
                        if (
                            hasattr(field, 'related_model')
                            and field.related_model
                            and field.related_model != self._meta.model
                            and hasattr(field.related_model, 'mro')
                            and CustomBaseModelWithSoftDelete in field.related_model.mro()
                        ):
                            skip_raw_delete = True
                            break
                    if not skip_raw_delete:
                        count = queryset._raw_delete(using=using)

                deleted_counter[queryset.model._meta.label] += count

            for model, instances in items.get('data').items():
                pk_list = [obj.pk for obj in instances]
                queryset = model.objects.filter(id__in=pk_list)
                count = queryset.count()

                if issubclass(model, CustomBaseModelWithSoftDelete):
                    count = queryset.update(deleted_at=required_deleted_at)

                deleted_counter[model._meta.label] += count

                if not model._meta.auto_created:
                    for obj in instances:
                        required_post_signal.send(sender=model, instance=obj, using=using)

        return sum(deleted_counter.values()), dict(deleted_counter)
