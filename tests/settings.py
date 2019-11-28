SECRET_KEY = 'fake-key'  # # noqa: S105

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'test.db'}}

ROOT_URLCONF = 'tests.urls'

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'builtins': ['vb_baseapp.templatetags.html_debug'],
            'context_processors': ['vb_baseapp.context_processors.common_environment_variables'],
        },
    }
]


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'vb_baseapp.apps.VbBaseappConfig',
    'tests.apps.TestAppConfig',
]
