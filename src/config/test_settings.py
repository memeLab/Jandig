from config.settings import *  # noqa F403 F401


STORAGES = {
    "default": {
        "BACKEND": "inmemorystorage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "inmemorystorage.InMemoryStorage",
    },
}

# Set MEDIA_URL to include the test server URL
MEDIA_URL = "http://testserver"

# Set up SQLite in-memory database for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_DIR = env("ROOT_DIR", default="/jandig/")
