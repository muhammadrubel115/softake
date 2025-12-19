import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "softake.settings.dev")
django.setup()
