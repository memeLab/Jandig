from locust import HttpLocust, TaskSet

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
    min_wait = 5000
    max_wait = 9000