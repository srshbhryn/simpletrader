from django.apps import AppConfig


class TraderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'simpletrader.trader'

    # def ready(self) -> None:
        # from . import config
