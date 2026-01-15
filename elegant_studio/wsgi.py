"""
WSGI config for elegant_studio project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elegant_studio.settings')

application = get_wsgi_application()
