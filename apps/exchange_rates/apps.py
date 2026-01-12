from django.apps import AppConfig


class ExchangeRatesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.exchange_rates"
    verbose_name = "환율 정보"
