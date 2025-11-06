from django.apps import AppConfig


class ActivitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.activities'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.activities.signals
