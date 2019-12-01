from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

__all__ = ['set_label_prefix_for_related_fields']


def set_label_prefix_for_related_fields(field, obj):
    label = field.label_from_instance(obj)
    if obj.is_deleted:
        label = f'[{capfirst(_("deleted"))}]: {label}'
    return label
