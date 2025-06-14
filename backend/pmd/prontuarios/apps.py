from django.apps import AppConfig

class ProntuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prontuarios'

    def ready(self):
        from trackapi.signals import registrar_sinais
        registrar_sinais()