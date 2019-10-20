import logging

from django.contrib import admin
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import models
# from django.forms import TextInput
# from django.shortcuts import redirect
from django.template.defaultfilters import capfirst
from django.utils.translation import ngettext_lazy
from django.utils.translation import ugettext_lazy as _

from console import console

from ..models import CustomBaseModelWithSoftDelete
from ..widgets import AdminImageFileWidget
from .actions import hard_delete_selected, recover_selected

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
        if request.GET:
            return queryset
        return queryset.actives()

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_goback'] = getattr(self, 'show_goback_button', True)
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_goback'] = getattr(self, 'show_goback_button', True)
        current_instance = self.get_object(request, object_id)
        if current_instance.is_deleted:
            extra_context['show_softdeleted_object_message'] = True
            extra_context['show_save_and_continue'] = False
            extra_context['show_save_and_add_another'] = False
            extra_context['show_hard_delete'] = True
            extra_context['show_recover'] = True

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

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
        custom_list_filters.append(ActiveInactiveFilter)
        for list_filter in list_filters:
            new_filter = list_filter
            if isinstance(list_filter, str):
                new_filter = (list_filter, list_filter_wrapper())
            custom_list_filters.append(new_filter)
        return custom_list_filters

    def get_actions(self, request):
        existing_actions = super().get_actions(request)

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

    def fix_formfield_choices_for_foreignkey_and_manytomany(self, queryset, empty_label):  # pylint: disable=R0201
        if empty_label is not None:
            yield '', empty_label
        for item in queryset:
            choice_id = item.id
            choice_label = str(item)
            if item.is_deleted:
                choice_label = f'[{capfirst(_("deleted"))}]: {choice_label}'
            yield choice_id, choice_label

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if issubclass(formfield.queryset.model, CustomBaseModelWithSoftDelete):
            formfield.choices = self.fix_formfield_choices_for_foreignkey_and_manytomany(
                formfield.queryset, formfield.empty_label
            )
        return formfield

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
        if issubclass(formfield.queryset.model, CustomBaseModelWithSoftDelete):
            formfield.choices = self.fix_formfield_choices_for_foreignkey_and_manytomany(
                formfield.queryset, formfield.empty_label
            )
        return formfield

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if obj.is_deleted:
                return False
        return True
