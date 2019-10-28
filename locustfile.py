from locust import HttpLocust, TaskSet

def index(l):
    l.client.get("/")

def collection(l):
    l.client.get("/collection/")

class UserBehavior(TaskSet):
    tasks = {index: 2, collection: 1}

    # def on_start(self):
    #     login(self)

    # def on_stop(self):
    #     logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000