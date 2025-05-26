from django.db import models

class Usuario(models.Model):
    nomeCompleto= models.CharField(max_length=100)
    cpf= models.CharField(max_length=11)
    dataNascimento= models.CharField(max_length=8)


    class Meta:
        verbose_name_plural='Usuarios'

    def __str__(self):
        return self.nomeCompleto 

class Prontuario(models.Model): 
    paciente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    queixas_principais = models.TextField(default="Sem queixas principais")
    medicamentos_continuos= models.TextField(default="Sem medicamentos continuos")
    exames =  models.TextField(default="Sem exames")
    prescricao_medica= models.TextField(default="Sem prescição médica")
    numeroProntuario= models.BigIntegerField(unique=True, null=True, blank=True)


    class Meta:
        verbose_name='Prontuario'
        verbose_name_plural='Prontuarios'

    def __str__(self):
        return "Prontuário: " + str(self.numeroProntuario) +  " | Nome completo: " + self.paciente.nomeCompleto
    
