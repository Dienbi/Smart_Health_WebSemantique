from django.apps import AppConfig


class DefisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.defis'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.defis.signals
