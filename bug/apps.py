from django.apps import AppConfig


class bugConfig(AppConfig):
    name = 'bug'

    def ready(self):
        from bug import signals
