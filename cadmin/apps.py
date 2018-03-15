from django.apps import AppConfig

# Load the cadmin first.
class CadminConfig(AppConfig):
    name = 'cadmin'

    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('cadmin')