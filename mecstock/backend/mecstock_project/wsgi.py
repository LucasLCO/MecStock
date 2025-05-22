"""
WSGI config for mecstock_project.

This module contains the WSGI application used by Django's runserver.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mecstock_project.settings')

application = get_wsgi_application()