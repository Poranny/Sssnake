from collections import defaultdict

class EnvEngine:

    def __init__(self):
        self.observers = list()

    def setup_env(self, env_params) :

        envdata = env_params

        self.notify_observers(envdata)

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, data=None):
        for callback in self.observers:
            callback(data)