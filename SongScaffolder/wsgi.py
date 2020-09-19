"""
WSGI config for SongScaffolder project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv
from . import BASE_DIR

load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))
try:
    os.environ["DB_USER"]
except KeyError:
    # Handled by Travis for testing purposes.
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SongScaffolder.settings')

application = get_wsgi_application()
