from django.apps import AppConfig


class HabitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.habits'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.habits.signals
