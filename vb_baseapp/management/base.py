# pylint: disable=W0223,R0201

import errno
import os
import re
import time

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

__all__ = ['CustomBaseCommand', 'CustomBaseCommandWithFileTools', 'get_need_model_names']


def get_need_model_names(name):
    """
    returns filename,ClassName,verbose name in a tuple

    >>> get_need_model_names('CustomUser')
    ('custom_user', 'CustomUser', 'custom user')
    >>> get_need_model_names('user')
    ('user', 'User', 'user')
    >>> get_need_model_names('custom_user')
    ('custom_user', 'CustomUser', 'custom user')
    >>> get_need_model_names('User')
    ('user', 'User', 'user')
    >>> get_need_model_names('Custom_User')
    ('custom_user', 'CustomUser', 'custom user')
    """

    def has_any_upper_case_letter(name):
        return not all([letter.islower() for letter in name if letter.isalpha()])

    if has_any_upper_case_letter(name):
        if '_' in name:
            lower_letters = [word.lower() for word in name.split('_')]
            need_filename = '_'.join(lower_letters)
            need_class_name = name.replace('_', '')
            need_verbose_name = ' '.join(lower_letters)
            return need_filename, need_class_name, need_verbose_name

        lower_letters = [word.lower() for word in re.findall('[A-Z][^A-Z]*', name)]
        need_filename = '_'.join(lower_letters)
        need_class_name = name
        need_verbose_name = ' '.join(lower_letters)
        return need_filename, need_class_name, need_verbose_name

    if '_' in name:
        need_filename = name
        need_class_name = ''.join([word.title() for word in name.split('_')])
        need_verbose_name = ' '.join(name.split('_'))
        return need_filename, need_class_name, need_verbose_name

    need_filename = name.lower()
    need_class_name = name.title()
    need_verbose_name = need_filename
    return need_filename, need_class_name, need_verbose_name


class CustomBaseCommand(BaseCommand):
    """

    CustomBaseCommand comes with a small method. `.out()` is a helper.

    Usage:

        class Command(CustomBaseCommand):
            def handle(self, *args, **options):
                self.out('hello')       # INFO
                self.out('hello', 'w')  # WARNING
                self.out('hello', 'e')  # ERROR
                self.out('hello', 'n')  # NOTICE

    """

    def out(self, text, style='s'):
        switcher = {'s': 'SUCCESS', 'w': 'WARNING', 'e': 'ERROR', 'n': 'NOTICE'}.get(style, 's')
        writer = getattr(self.style, switcher)
        self.stdout.write(writer(text))


class CustomBaseCommandWithFileTools(CustomBaseCommand):
    def create_or_modify_file(self, filename, content, mode='w'):
        with open(filename, mode) as file_pointer:
            file_pointer.write(content)

    def make_directory(self, dirname):
        try:
            os.mkdir(dirname)
        except OSError as err:
            if err.errno == errno.EEXIST:
                message = '"%s" already exists' % dirname
            else:
                message = err
            exception_obj = CommandError(message)
            exception_obj.errno = err.errno
            raise exception_obj

    def create_file_with_content(self, filename, content):
        """
        Create/write a file with content.
        """
        with open(filename, 'w') as file_pointer:
            file_pointer.write(content)

    def touch(self, filename):
        am_time = time.mktime(time.localtime())
        with open(filename, 'a'):
            os.utime(filename, (am_time, am_time))
