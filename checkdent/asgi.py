"""
ASGI config for checkdent project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkdent.settings')

application = get_asgi_application()

