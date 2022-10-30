import importlib
import os
import time
import logging
import psycopg2

SERVICES_STARTED = False

log = logging.getLogger("ej")


def start_services():
    global SERVICES_STARTED

    if SERVICES_STARTED:
        return

    start_postgres()

    SERVICES_STARTED = True


log = logging.getLogger("ej")


def start_postgres():
    settings_path = os.environ["DJANGO_SETTINGS_MODULE"]
    settings = importlib.import_module(settings_path)

    db = settings.DATABASES["default"]
    dbname = db["NAME"]
    user = db["USER"]
    password = db["PASSWORD"]
    host = db["HOST"]

    for _ in range(100):
        if can_connect(dbname, user, password, host):
            log.info("Postgres is available. Continuing...")
            return
        log.warning("Postgres is unavailable. Retrying in 0.5 seconds")
        time.sleep(0.5)

    log.critical("Maximum number of attempts connecting to postgres database")
    raise RuntimeError("could not connect to database")


def can_connect(dbname, user, password, host):
    try:
        psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    except psycopg2.OperationalError:
        return False
    return True
