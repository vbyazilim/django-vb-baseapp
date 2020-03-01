import logging

from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.admin.widgets import (
    AutocompleteSelectMultiple,
)
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import models
from django.forms import models as form_models
from django.forms.widgets import (
    CheckboxSelectMultiple,
    SelectMultiple,
)
from django.utils.text import capfirst, format_lazy
from django.utils.translation import ngettext_lazy
from django.utils.translation import ugettext_lazy as _

from console import console

from ..models import CustomBaseModelWithSoftDelete
from .actions import hard_delete_selected, recover_selected
from .autocomplete_view import (
    SoftDeleteAutocompleteJsonView,
)
from .utils import set_label_prefix_for_related_fields
from .widgets import (
    AdminAutocompleteSelect,
    AdminAutocompleteSelectMultiple,
    AdminImageFileWidget,
)

__all__ = ['CustomBaseModelAdmin', 'CustomBaseModelAdminWithSoftDelete']

console = console(source=__name__)
logger = logging.getLogger('app')


class CachingPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._count = None

    def _get_count(self):
        if self._count is None:
            try:
                key = 'adm:{0}:count'.format(hash(self.object_list.query.__str__()))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key, self._count, 3600)
            except (TypeError, ValueError):
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)


class ActiveInactiveFilter(admin.SimpleListFilter):
    title = _('activity state')
    parameter_name = 'inactives'

    def lookups(self, request, model_admin):
        return (('true', _('inactives')),)

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.inactives()
        return queryset


class CustomBaseModelAdmin(admin.ModelAdmin):
    """

    Base model admin for CustomBaseModel

    """

    show_full_result_count = False
    paginator = CachingPaginator
    formfield_overrides = {models.ImageField: {'widget': AdminImageFileWidget}}

    class Media:
        css = {'all': ['admin/css/vb-baseapp-admin.css']}


def list_filter_wrapper():
    class ListFilterWrapper(admin.FieldListFilter):  # pylint: disable=W0223
        def __new__(cls, *args, **kwargs):
            list_filter_instance = admin.FieldListFilter.create(*args, **kwargs)
            if isinstance(list_filter_instance, admin.filters.RelatedFieldListFilter):
                if issubclass(list_filter_instance.field.related_model, CustomBaseModelWithSoftDelete):
                    field = list_filter_instance.field
                    deleted_items_queryset = field.related_model._default_manager.inactives().values_list(
                        'id', flat=True
                    )
                    new_lookup_choices = []
                    for item_id, item_str in list_filter_instance.lookup_choices:
                        if item_id in deleted_items_queryset:
                            item_str = f'[{capfirst(_("deleted"))}]: {item_str}'
                        new_lookup_choices.append((item_id, item_str))

                    list_filter_instance.lookup_choices = new_lookup_choices
            return list_filter_instance

    return ListFilterWrapper


MESSAGE_UNDELETED_OBJECT_INFO = _('"%(obj)s (ID: %(id)d)" recovered successfully.')
MESSAGE_UNDELETED_OBJECTS_REPORT = ngettext_lazy(
    '%(num)d object is recovered in total.', '%(num)d objects are recovered in total.', 'num'
)
MESSAGE_HARDDELETED_OBJECT_INFO = _('"%(obj)s" is really deleted.')
MESSAGE_HARDDELETED_OBJECTS_REPORT = ngettext_lazy(
    '%(num)d object is wiped in total.', '%(num)d objects are wiped in total.', 'num'
)


class SoftDeleteModelChoiceIterator(form_models.ModelChoiceIterator):
    def choice(self, obj):
        return (self.field.prepare_value(obj), set_label_prefix_for_related_fields(self.field, obj))


def set_model_choice_iterator(formfield):
    if issubclass(formfield.queryset.model, CustomBaseModelWithSoftDelete):
        return SoftDeleteModelChoiceIterator
    return formfield.iterator


class CustomBaseModelAdminWithSoftDelete(CustomBaseModelAdmin):

    hide_deleted_at = True
    change_form_template = 'admin/vb_baseapp/change_form.html'
    show_goback_button = True

    def response_change(self, request, obj):
        """
        Need to refactor this method...
        """

        if '_recoverdeleted' in request.POST:
            number_of_rows_undeleted, __ = obj.undelete()
            messages = [
                MESSAGE_UNDELETED_OBJECT_INFO % dict(obj=str(obj), id=obj.id),
                MESSAGE_UNDELETED_OBJECTS_REPORT % dict(num=number_of_rows_undeleted),
            ]
            self.message_user(request, ''.join(messages))
            return self.response_post_save_change(request, obj)

        if '_harddelete' in request.POST:
            number_of_rows_wiped, __ = obj.hard_delete()
            messages = [
                MESSAGE_HARDDELETED_OBJECT_INFO % dict(obj=str(obj)),
                MESSAGE_HARDDELETED_OBJECTS_REPORT % dict(num=number_of_rows_wiped),
            ]
            self.message_user(request, ''.join(messages))
            return self.response_post_save_change(request, obj)

        return super().response_change(request, obj)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.GET or request.is_ajax():
            return queryset
        return queryset.actives()

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_goback'] = getattr(self, 'show_goback_button', True)
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_goback'] = getattr(self, 'show_goback_button', True)
        _change_view = super().change_view(request, object_id, form_url, extra_context=extra_context)

        if hasattr(_change_view, 'context_data'):
            current_instance = _change_view.context_data['original']
            if current_instance.is_deleted:
                _change_view.context_data['show_softdeleted_object_message'] = True
                _change_view.context_data['show_save_and_continue'] = False
                _change_view.context_data['show_save_and_add_another'] = False
                _change_view.context_data['show_hard_delete'] = True
                _change_view.context_data['show_recover'] = True
        return _change_view

    def autocomplete_view(self, request):
        return SoftDeleteAutocompleteJsonView.as_view(model_admin=self)(request)

    def get_exclude(self, request, obj=None):
        is_obj_deleted = getattr(obj, 'is_deleted', False)
        excluded = super().get_exclude(request, obj=obj)
        exclude = [] if excluded is None else list(excluded)
        if self.hide_deleted_at and not is_obj_deleted:
            exclude.append('deleted_at')
        return exclude

    def get_list_filter(self, request):
        list_filters = list(super().get_list_filter(request))
        custom_list_filters = []

        user_has_delete_perm = request.user.has_perm(f'{self.model._meta.model_name}_delete')  # pylint: disable=W0212
        if user_has_delete_perm:
            custom_list_filters.append(ActiveInactiveFilter)

        for list_filter in list_filters:
            new_filter = list_filter
            if isinstance(list_filter, str):
                new_filter = (list_filter, list_filter_wrapper())
            custom_list_filters.append(new_filter)
        return custom_list_filters

    def get_actions(self, request):
        user_has_delete_perm = request.user.has_perm(f'{self.model._meta.model_name}_delete')  # pylint: disable=W0212
        existing_actions = super().get_actions(request)

        if user_has_delete_perm:
            if request.GET.get('inactives', None) and 'delete_selected' in existing_actions:
                existing_actions.pop('delete_selected', None)
                existing_actions.update(
                    dict(
                        recover_selected=(
                            recover_selected,
                            'recover_selected',
                            _('Recover selected %(verbose_name_plural)s'),
                        )
                    )
                )
            existing_actions.update(
                dict(
                    hard_delete_selected=(
                        hard_delete_selected,
                        'hard_delete_selected',
                        _('Hard delete selected %(verbose_name_plural)s'),
                    )
                )
            )
        return existing_actions

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        related_field_is_subclass_of_softdelete = issubclass(db_field.related_model, CustomBaseModelWithSoftDelete)
        if db_field.name in self.get_autocomplete_fields(request) and related_field_is_subclass_of_softdelete:
            db = kwargs.get('using')  # pylint: disable=C0103
            kwargs['widget'] = AdminAutocompleteSelect(db_field.remote_field, self.admin_site, using=db)

        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if related_field_is_subclass_of_softdelete:
            formfield.iterator = set_model_choice_iterator(formfield)
        return formfield

    def formfield_for_manytomany_modified(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # If it uses an intermediary model that isn't auto created, don't show
        # a field in admin.
        if not db_field.remote_field.through._meta.auto_created:  # pylint: disable=W0212
            return None
        db = kwargs.get('using')  # pylint: disable=C0103

        autocomplete_fields = self.get_autocomplete_fields(request)
        # just added this line...
        if 'widget' not in kwargs:
            if db_field.name in autocomplete_fields:
                kwargs['widget'] = AutocompleteSelectMultiple(db_field.remote_field, self.admin_site, using=db)
            elif db_field.name in self.raw_id_fields:
                kwargs['widget'] = widgets.ManyToManyRawIdWidget(db_field.remote_field, self.admin_site, using=db)
            elif db_field.name in [*self.filter_vertical, *self.filter_horizontal]:
                kwargs['widget'] = widgets.FilteredSelectMultiple(
                    db_field.verbose_name, db_field.name in self.filter_vertical
                )

        if 'queryset' not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs['queryset'] = queryset

        form_field = db_field.formfield(**kwargs)
        if isinstance(form_field.widget, SelectMultiple) and not isinstance(
            form_field.widget, (CheckboxSelectMultiple, AutocompleteSelectMultiple)
        ):
            msg = _('Hold down "Control", or "Command" on a Mac, to select more than one.')
            help_text = form_field.help_text
            form_field.help_text = format_lazy('{0} {1}', help_text, msg) if help_text else msg
        return form_field

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        related_field_is_subclass_of_softdelete = issubclass(db_field.related_model, CustomBaseModelWithSoftDelete)
        if db_field.name in self.get_autocomplete_fields(request) and related_field_is_subclass_of_softdelete:
            db = kwargs.get('using')  # pylint: disable=C0103
            kwargs['widget'] = AdminAutocompleteSelectMultiple(db_field.remote_field, self.admin_site, using=db)

        formfield = self.formfield_for_manytomany_modified(db_field, request, **kwargs)
        if formfield and related_field_is_subclass_of_softdelete:
            formfield.iterator = set_model_choice_iterator(formfield)
        return formfield

    def has_delete_permission(self, request, obj=None):
        has_delete = super().has_delete_permission(request, obj)
        return has_delete
