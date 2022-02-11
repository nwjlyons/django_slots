SECRET_KEY = 'secret'

INSTALLED_APPS=[
    'tests.app',
    'django_template_component'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]
