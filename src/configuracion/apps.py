from django.apps import AppConfig


class ConfiguracionConfig(AppConfig):
    name = 'configuracion'

    def ready(self):
        import configuracion.signals
