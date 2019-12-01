import logging

from django import forms
from django.contrib.admin.widgets import AutocompleteMixin

from console import console

from ..utils import set_label_prefix_for_related_fields

__all__ = ['AdminAutocompleteSelect', 'AdminAutocompleteSelectMultiple']

console = console(source=__name__)
logger = logging.getLogger('app')


class CustomAutocompleteMixin(AutocompleteMixin):
    def optgroups(self, name, value, attr=None):
        default = (None, [], 0)
        groups = [default]
        has_selected = False
        selected_choices = {str(v) for v in value if str(v) not in self.choices.field.empty_values}

        if not self.is_required and not self.allow_multiple_selected:
            default[1].append(self.create_option(name, '', '', False, 0))
        choices = (
            (obj.pk, set_label_prefix_for_related_fields(self.choices.field, obj))
            for obj in self.choices.queryset.using(self.db).filter(pk__in=selected_choices)
        )

        for option_value, option_label in choices:
            selected = str(option_value) in value and (has_selected is False or self.allow_multiple_selected)
            has_selected |= selected
            index = len(default[1])
            subgroup = default[1]
            subgroup.append(self.create_option(name, option_value, option_label, selected_choices, index))
        return groups


class AdminAutocompleteSelect(CustomAutocompleteMixin, forms.Select):
    pass


class AdminAutocompleteSelectMultiple(CustomAutocompleteMixin, forms.SelectMultiple):
    pass
