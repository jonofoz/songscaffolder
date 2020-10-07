import environ

from SongScaffolder.settings.base import *

env = environ.Env(
    DEBUG=(bool, False)
)

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': env.db(),
}