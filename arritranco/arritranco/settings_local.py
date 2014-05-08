# Django settings for arritranco project.


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',      #'django.db.backends.sqlite3',           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'arritranco',             # Or path to database file if using sqlite3.
        'USER': 'root',             # Not used with sqlite3.
        'PASSWORD': 'toor',         # Not used with sqlite3.
        'HOST': '127.0.0.1',        # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                 # Set to empty string for default. Not used with sqlite3.
    }
}
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',      #'django.db.backends.sqlite3',           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'devdb',             # Or path to database file if using sqlite3.
        'USER': '',             # Not used with sqlite3.
        'PASSWORD': '',         # Not used with sqlite3.
        'HOST': '',        # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                 # Set to empty string for default. Not used with sqlite3.
    }
}
"""
SECRET_KEY = '9u)uyfcmr*p9m6d=km@r@(0bzvoi*nt^_9*yy)-h)+-o&$6z=5'

# Celery settings

BROKER_URL = 'amqp://localhost//'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']

DEBUG = True
