import csv
import os

from django.core.management.base import BaseCommand

from trackapi.models import EventoAuditavel


class Command(BaseCommand):
    help = "Exporta todos os eventos de auditoria para um CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            default="audit_log.csv",
            help="Caminho do arquivo CSV de saída",
        )

    def handle(self, *args, **options):
        output_path = options["output"]
        qs = EventoAuditavel.objects.all().order_by("data_hora")

        with open(output_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "ID",
                    "Usuário",
                    "Caminho",
                    "Método",
                    "DataHora",
                    "Sensível",
                    "Descrição",
                ]
            )
            for evt in qs:
                writer.writerow(
                    [
                        evt.id,
                        evt.usuario.username if evt.usuario else "",
                        evt.caminho,
                        evt.metodo,
                        evt.data_hora.isoformat(),
                        evt.evento_sensivel,
                        evt.descricao_evento or "",
                    ]
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Exportado {qs.count()} eventos para {os.path.abspath(output_path)}"
            )
        )
