# Copy to local_settings.py and modify

import os.path
ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('your_name', 'your_email'),
)

# Use a local SQLite3 database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path('ttg.sqlite'),       # create in this folder
    }
}
