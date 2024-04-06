"""
Django settings for RenukaSoft project.

Generated by 'django-admin startproject' using Django 3.2.19.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^i1$(h65ncls7s__k36@kl$k86%8i1l*hgng&ynu$#_)oj!dy)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://0.0.0.0:3000',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'estimation',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    # 'django.contrib.staticfiles',  # required for serving swagger ui's css/js files
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'RenukaSoft.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'RenukaSoft.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

APPEND_SLASH = False




AUTH_USER_MODEL = 'accounts.CustomUser'

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'spmis2223yrk',     # Your database name
#         'USER': 'manish',           # Your database user
#         'PASSWORD': 'manish',       # Your database password
#         #'HOST': '103.170.114.33',        # Hostname for your MySQL server
#         #'PORT': '33063',             # MySQL default port
#         # 'HOST': '127.0.0.1',        # Hostname for your MySQL server
#         # 'PORT': '3306',             # MySQL default port
#         'HOST': '103.170.114.33',        # Hostname for your MySQL server
#         'PORT': '33063',             # MySQL default port
    # },
    #     'kld': {
    #         'ENGINE': 'django.db.backends.mysql',
    #         'NAME': 'spmis1819kld',     # Your database name
    #         'USER': 'manish',           # Your database user
    #         'PASSWORD': 'manish',       # Your database password
    #         #'HOST': '103.170.114.33',        # Hostname for your MySQL server
    #         #'PORT': '33063',             # MySQL default port
    #         # 'HOST': '127.0.0.1',        # Hostname for your MySQL server
    #         # 'PORT': '3306',             # MySQL default port
    #         'HOST': '103.170.114.33',        # Hostname for your MySQL server
    #         'PORT': '33063',             # MySQL default port
    # },
    #     'kld2': {
    #         'ENGINE': 'django.db.backends.mysql',
    #         'NAME': 'spmis1516aam',     # Your database name
    #         'USER': 'manish',           # Your database user
    #         'PASSWORD': 'manish',       # Your database password
    #         #'HOST': '103.170.114.33',        # Hostname for your MySQL server
    #         #'PORT': '33063',             # MySQL default port
    #         # 'HOST': '127.0.0.1',        # Hostname for your MySQL server
    #         # 'PORT': '3306',             # MySQL default port
    #         'HOST': '103.170.114.33',        # Hostname for your MySQL server
    #         'PORT': '33063',             # MySQL default port
    # },
#     }
# }

#python manage.py inspectdb usermaster > models.py to fetch all the tables into model
# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}



SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),  # Set access token expiration time
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # Set refresh token expiration time
}



MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Disable "Django Login" page when trying to access swagger api in browser.
# SWAGGER_SETTINGS = {
#    'USE_SESSION_AUTH': False
# }

# Include this in the each Application  for Customize Django Admin View
# ADMIN_SITE_HEADER = "Renuka Softech Admin"
# ADMIN_SITE_TITLE = "SmartMIS Admin Panel"
# ADMIN_INDEX_TITLE = "Welcome to SmartMIS Admin"
