import environ

from SongScaffolder.settings.base import *

env = environ.Env(
    DEBUG=(bool, False)
)

SECURE_SSL_REDIRECT = True

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': env.db(),
}