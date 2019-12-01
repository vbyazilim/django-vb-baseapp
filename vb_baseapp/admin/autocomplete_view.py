import logging

from django.contrib.admin.views.autocomplete import (
    AutocompleteJsonView,
)
from django.http import Http404, JsonResponse
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from console import console

__all__ = ['SoftDeleteAutocompleteJsonView']

console = console(source=__name__)
logger = logging.getLogger('app')


class SoftDeleteAutocompleteJsonView(AutocompleteJsonView):
    def get(self, request, *args, **kwargs):
        if not self.model_admin.get_search_fields(request):
            raise Http404('%s must have search_fields for the autocomplete_view.' % type(self.model_admin).__name__)
        if not self.has_perm(request):
            return JsonResponse({'error': '403 Forbidden'}, status=403)

        self.term = request.GET.get('term', '')  # pylint: disable=W0201
        self.paginator_class = self.model_admin.paginator
        self.object_list = self.get_queryset()  # pylint: disable=W0201
        context = self.get_context_data()
        response_data = {'results': [], 'pagination': {'more': context['page_obj'].has_next()}}

        for obj in context['object_list']:
            payload = dict(id=str(obj.pk))
            text = str(obj)
            if obj.is_deleted:
                text = f'[{capfirst(_("deleted"))}]: {text}'
            payload.update(text=text)
            response_data['results'].append(payload)
        return JsonResponse(response_data)
