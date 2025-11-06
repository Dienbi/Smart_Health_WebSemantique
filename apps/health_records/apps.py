from django.apps import AppConfig


class HealthRecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.health_records'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.health_records.signals  # noqa