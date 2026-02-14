from django.apps import AppConfig


class RetailCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'retail_core'
    verbose_name = 'Retail Core'

    def ready(self):
        import retail_core.signals
