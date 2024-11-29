from django.apps import AppConfig


class AdminSideConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_side'


    def ready(self):
        # Import and connect the signal when the app is ready
        import admin_side.signals
