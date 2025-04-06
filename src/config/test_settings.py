from config.settings import *  # noqa F403 F401


STORAGES = {
    "default": {
        "BACKEND": "inmemorystorage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "inmemorystorage.InMemoryStorage",
    },
}