from django.apps import AppConfig


class ConfiguracionConfig(AppConfig):
    name = 'configuracion'

    def ready(self) -> None:
        import configuracion.signals

        return super().ready()