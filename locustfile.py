from locust import HttpLocust, Set, between


def index(load):
    load.client.get("/")


def load_gifs(load):
    load.client.get("/collection/")


def exhibit(load):
    load.client.get("/longavida/")


class UserBehavior(Set):
    s = {exhibit: 1}


class WebsiteUser(HttpLocust):
    _set = UserBehavior
    wait_time = between(3, 5)
