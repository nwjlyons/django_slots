SECRET_KEY = "secret"

INSTALLED_APPS = ["tests.app", "django_slots"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test.sqlite3",
    }
}
