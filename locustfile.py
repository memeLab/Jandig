from locust import HttpLocust, Set, between

def index(l):
    l.client.get("/")

def load_gifs(l):
    l.client.get("/collection/")

def exhibit(l):
    l.client.get("/longavida/")

class UserBehavior(Set):
    s = {exhibit:1}

class WebsiteUser(HttpLocust):
    _set = UserBehavior
    wait_time = between(3,5)