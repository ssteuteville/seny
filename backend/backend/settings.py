from django.conf import settings
"""
Django settings for backend project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#04-85seq5w3#jomn713nr14v+)(kr@k$l%$9i@i9$+br*3na*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#
TEMPLATE_DEBUG = DEBUG

TEMPLATE_CONTEXT_PROCESSORS = (
 'django.core.context_processors.request',
 'django.contrib.auth.context_processors.auth'

)

ALLOWED_HOSTS = [
    '52.10.64.129',
]
 

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rentlist',
    'rest_framework',
    'oauth2_provider'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}

# SWAGGER_SETTINGS = {
#     'is_authenticated': True,
#     'is_superuser': True
# }
ROOT_URLCONF = 'backend.urls'

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rentlist',
        'USER': 'root',
        'PASSWORD': '56Fuck89',
        'HOST': '127.0.0.1',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

AUTH_PROFILE_MODULE = 'rentlist.models.UserProfile'

if settings.DEBUG:
    MEDIA_ROOT = "C:/Users/shane/Documents/GitHub/senior_project/backend/media/"

    STATIC_ROOT = "C:/Users/shane/Documents/GitHub/senior_project/backend/static/"
else:
   #MEDIA_ROOT = "~/seny.com/seny/backend/media"
   #STATIC_ROOT = "~/seny.com/seny/backend/static"
    pass

STATIC_URL = r'/static/'
MEDIA_URL = r'/media/'
