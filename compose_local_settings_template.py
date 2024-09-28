# Local settings for deployment with Docker Compose

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "DO_NOT_USE_IN_PRODUCTION_u8E8grGoEMNxwisg5z3cSx7d7zy1mkudDmAAxv9xq1DeoGpDNo1Jujgm1C0wc2cI"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "postgres",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "CONN_MAX_AGE": 3600,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

RUNNING_IN_DOCKER = True
