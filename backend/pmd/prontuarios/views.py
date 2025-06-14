from .models import Prontuario
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, time

from trackapi.audit.decorators import auditar_evento
from trackapi.metrics.metrics import contabilizar_evento, observar_tempo
from trackapi.reports.reports import export_csv
from trackapi.crypto.masking import mascarar_texto
from trackapi.crypto.encryption import Encryptor
from trackapi.audit.models import EventoAuditavel
# from trackapi.notifiers.base_notifier import detectar_anomalia

encryptor = Encryptor(settings.ENCRYPTION_KEY)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@auditar_evento(descricao="Acessou prontuário por número", sensivel=True)
@contabilizar_evento("buscar_prontuario")
@observar_tempo("tempo_busca_prontuario")
def buscarProntuario(request):
    numeroProntuario = request.GET.get('prontuario')
    if not numeroProntuario:
        return JsonResponse({'erro': 'Numero do Prontuario nao fornecido'}, status=400)

    try:
        prontuarioMedico = Prontuario.objects.get(numeroProntuario=numeroProntuario)
        return Response({
            'numero_prontuario': prontuarioMedico.numeroProntuario,
            'paciente': prontuarioMedico.paciente.nomeCompleto,
            'queixas_principais': prontuarioMedico.queixas_principais,
            'medicamentos_continuos': prontuarioMedico.medicamentos_continuos,
            'exames': prontuarioMedico.exames,
            'prescicao_medica': encryptor.decrypt(prontuarioMedico.prescricao_medica)
        })
    except Prontuario.DoesNotExist:
        return JsonResponse({'erro': 'Prontuario nao encontrado'}, status=404)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@auditar_evento(descricao="Exportou prontuários em CSV", sensivel=True)
@contabilizar_evento("exportar_prontuarios_csv")
@observar_tempo("exportar_prontuarios_csv")
def exportarProntuariosCSV(request):
    prontuarios = Prontuario.objects.all()

    dados = []
    for prontuario in prontuarios:
        dados.append({
            'Número do Prontuário': prontuario.numeroProntuario,
            'Nome do Paciente': prontuario.paciente.nomeCompleto,
            'Queixas': prontuario.queixas_principais,
            'Medicamentos': prontuario.medicamentos_continuos,
            'Exames': prontuario.exames,
            'Prescrição': prontuario.prescricao_medica,
        })

    return export_csv(
        dados,
        nome_arquivo='prontuarios_exportados.csv'
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@auditar_evento(descricao="Cadastrou prontuário com criptografia", sensivel=True)
def cadastrarProntuarioCriptografado(request):
    dados = request.data
    numero = dados.get("numeroProntuario")
    prescricao_original = dados.get("prescricao_medica")

    if not numero:
        return JsonResponse({"erro": "O número do prontuário é obrigatório."}, status=400)

    try:
        numero = int(numero)
    except ValueError:
        return JsonResponse({"erro": "O número do prontuário deve ser numérico."}, status=400)

    if not prescricao_original:
        return JsonResponse({"erro": "Prescrição médica obrigatória."}, status=400)

    existente = Prontuario.objects.filter(numeroProntuario=numero).first()
    if existente:
        return JsonResponse({
            "erro": "Número de prontuário já cadastrado.",
            "id_existente": existente.id,
            "numeroProntuario": existente.numeroProntuario
        }, status=200)

    prontuario = Prontuario.objects.create(
        numeroProntuario=numero,
        paciente_id=dados.get("paciente_id"),
        queixas_principais=dados.get("queixas_principais", ""),
        medicamentos_continuos=dados.get("medicamentos_continuos", ""),
        exames=dados.get("exames", ""),
        prescricao_medica=encryptor.encrypt(prescricao_original)
    )

    return Response({
        "mensagem": "Prontuário salvo com prescrição criptografada.",
        "id": prontuario.id
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@auditar_evento(descricao="Leu prontuário com descriptografia", sensivel=True)
def visualizarPrescricaoDescriptografada(request, prontuario_id):
    try:
        prontuario = Prontuario.objects.get(id=prontuario_id)
        prescricao = encryptor.decrypt(prontuario.prescricao_medica)

        return Response({
            "id": prontuario.id,
            "numero_prontuario": prontuario.numeroProntuario,
            "prescricao_medica": prescricao
        })
    except Prontuario.DoesNotExist:
        return JsonResponse({"erro": "Prontuário não encontrado"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@auditar_evento(descricao="Visualizou prontuário com número mascarado", sensivel=True)
def visualizarProntuarioMascarado(request, prontuario_id):
    try:
        prontuario = Prontuario.objects.get(id=prontuario_id)
        numero_mascarado = mascarar_texto(prontuario.numeroProntuario)

        return Response({
            "id": prontuario.id,
            "numero_prontuario_mascarado": numero_mascarado,
            "paciente": prontuario.paciente.nomeCompleto
        })
    except Prontuario.DoesNotExist:
        return JsonResponse({"erro": "Prontuário não encontrado"}, status=404)


@csrf_exempt
def listarEventosAuditados(request):
    usuario = request.GET.get('usuario')
    tipo = request.GET.get('tipo')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    qs = EventoAuditavel.objects.select_related('usuario').all()

    if usuario:
        qs = qs.filter(usuario__username=usuario)
    if data_inicio:
        data_inicio_dt = datetime.combine(parse_date(data_inicio), time.min)
        qs = qs.filter(data_hora__gte=data_inicio_dt)

    if data_fim:
        data_fim_dt = datetime.combine(parse_date(data_fim), time.max)
        qs = qs.filter(data_hora__lte=data_fim_dt)

    eventos = []
    for e in qs:
        eventos.append({
            "usuario": e.usuario.username if e.usuario else "Anônimo",
            "descricao_evento": e.descricao_evento or "",
            "data": e.data_hora.strftime("%Y-%m-%d %H:%M:%S") if e.data_hora else "",
            "status_code": e.status_code,
            "caminho": e.caminho,
            "metodo": e.metodo,
        })

    return JsonResponse({"eventos": eventos}, safe=False)

#novos que precisam de front e urls
# @csrf_exempt
# def detectarAnomalia(request):
#     eventos_db = EventoAuditavel.objects.order_by('-data')[:20]
#     eventos = [
#         {
#             "status_code": e.status_code if hasattr(e, "status_code") else 200,
#             "tipo_evento": getattr(e, "tipo_evento", None),
#             "usuario": getattr(e, "usuario", None),
#             "data": e.data.isoformat() if hasattr(e, "data") else "",
#         }
#         for e in eventos_db
#     ]

#     anomalia = detectar_anomalia(eventos)
#     return JsonResponse({
#         "anomalia_detectada": anomalia,
#         "eventos_avaliados": len(eventos),
#         "detalhe": "Anomalia detectada!" if anomalia else "Nenhuma anomalia."
#     })


# @csrf_exempt
# def exportarEventosCsv(request):
#     usuario = request.GET.get("usuario")
#     tipo = request.GET.get("tipo")
#     data_inicio = request.GET.get("data_inicio")
#     data_fim = request.GET.get("data_fim")

#     eventos = EventoAuditavel.objects.all()

#     if usuario:
#         eventos = eventos.filter(usuario__username=usuario)
#     if tipo:
#         eventos = eventos.filter(tipo_evento=tipo)
#     if data_inicio:
#         eventos = eventos.filter(data__gte=parse_date(data_inicio))
#     if data_fim:
#         eventos = eventos.filter(data__lte=parse_date(data_fim))

#     response = HttpResponse(content_type="text/csv")
#     response["Content-Disposition"] = "attachment; filename=eventos_filtrados.csv"

#     writer = csv.writer(response)
#     writer.writerow(["Usuário", "Tipo de Evento", "Data", "Status Code", "Caminho", "Método"])

#     for evento in eventos:
#         writer.writerow([
#             evento.usuario.username if evento.usuario else "",
#             evento.tipo_evento,
#             evento.data.strftime("%Y-%m-%d %H:%M:%S"),
#             evento.status_code,
#             evento.caminho,
#             evento.metodo
#         ])

#     return response