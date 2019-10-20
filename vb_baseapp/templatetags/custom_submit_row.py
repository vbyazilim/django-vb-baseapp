from django import template
from django.contrib.admin.templatetags.admin_modify import (
    submit_row as original_submit_row,
)

register = template.Library()


@register.inclusion_tag('admin/vb_baseapp/submit_line.html', takes_context=True)
def custom_submit_row(context):
    ctx = original_submit_row(context)

    if 'show_save_and_add_another' in context:
        ctx.update({'show_save_and_add_another': context.get('show_save_and_add_another')})
    if 'show_hard_delete' in context:
        ctx.update({'show_hard_delete': context.get('show_hard_delete')})
    if 'show_recover' in context:
        ctx.update({'show_recover': context.get('show_recover')})
    if 'show_goback' in context:
        ctx.update({'show_goback': context.get('show_goback')})
    return ctx
