from locust import HttpLocust, TaskSet, between

def index(l):
    l.client.get("/")

def load_gifs(l):
    l.client.get("/collection/")

def exhibit(l):
    l.client.get("/longavida/")

class UserBehavior(TaskSet):
    tasks = {exhibit:1}

    # def on_start(self):
    #     login(self)

    # def on_stop(self):
    #     logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(3,5)