from .models import Prontuario
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
            'prescicao_medica': prontuarioMedico.prescricao_medica
                        })

    except Prontuario.DoesNotExist:
        return JsonResponse({'erro': 'Prontuario nao encontrado'}, status=404)
