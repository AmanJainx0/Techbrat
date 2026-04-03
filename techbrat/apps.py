from django.apps import AppConfig


class TechbratConfig(AppConfig):
    name = 'techbrat'
    
    def ready(self):
        import techbrat.signals
