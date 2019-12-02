# pylint: disable=C0301

"""
Custom User Model forms template
"""

TEMPLATE_CUSTOM_USER_ADMIN_FORMS = """from django import forms
from django.contrib.auth import (
    get_user_model,
    password_validation,
)
from django.contrib.auth.forms import (
    ReadOnlyPasswordHashField,
)
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from console import console

__all__ = ['{model_name_for_class}ChangeForm', '{model_name_for_class}CreationForm']

console = console(source=__name__)


CUSTOM_USER = get_user_model()


class {model_name_for_class}ChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=capfirst(_('password')),
        help_text=_(
            'Raw passwords are not stored, so there is no way to see this '
            "user's password, but you can change the password using "
            '<a href="{{0}}">this form</a>.'
        ),
    )

    class Meta:
        model = CUSTOM_USER
        fields = ('email', 'first_name', 'last_name', 'password', 'is_active', 'is_staff', 'is_superuser')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('password')
        if password:
            password.help_text = password.help_text.format('../password/')
        user_permissions = self.fields.get('user_permissions')
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related('content_type')

    def clean_password(self):
        return self.initial['password']


class {model_name_for_class}CreationForm(forms.ModelForm):

    password1 = forms.CharField(
        label=capfirst(_('password')),
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(label=capfirst(_('password confirmation')), widget=forms.PasswordInput)

    class Meta:
        model = CUSTOM_USER
        fields = ('first_name', 'last_name')

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("passwords don't match"))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

"""

__all__ = ['TEMPLATE_CUSTOM_USER_ADMIN_FORMS']
