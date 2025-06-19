
from django.urls import path
from . import views 

urlpatterns = [
    path('prontuario/', views.buscarProntuario),
    path('prontuario/exportar/csv/', views.exportarProntuariosCSV, name='exportar_prontuarios_csv'),
    # path('prontuario/cadastrar/criptografado/', views.cadastrarProntuarioCriptografado, name='cadastrar_prontuario_criptografado'),
    # path('prontuario/visualizar/prescricao/<int:prontuario_id>/', views.visualizarPrescricaoDescriptografada, name='visualizar_prescricao_descriptografada'),
    # path('prontuario/visualizar/mascarado/<int:prontuario_id>/', views.visualizarProntuarioMascarado, name='visualizar_prontuario_mascarado'),
    path('eventos/auditados/', views.listarEventosAuditados, name='listar_eventos_auditados'),
    # path('eventos/anomalia/', views.detectarAnomalia, name='detectar_anomalia'),
    # path('eventos/exportar/csv/', views.exportarEventosCsv, name='exportar_eventos_csv'),
]
