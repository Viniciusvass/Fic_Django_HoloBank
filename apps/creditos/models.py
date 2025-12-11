from django.db import models
from apps.usuarios.models import Usuario
from apps.contas.models import Conta

# Create your models here.
class SolicitacaoCredito(models.Model):
    STATUS = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    )
    id_solicitacaoCredito = models.BigAutoField(primary_key=True)
    valor_solicitado = models.DecimalField(max_digits=12, decimal_places=2)
    taxa_juros = models.FloatField()
    status_credito = models.CharField(max_length=20, choices=STATUS, default='pendente')
    data_solicitacao = models.DateField(auto_now_add=True)
    data_analise = models.DateField(null=True, blank=True)
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    gerente_responsavel = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name="analises_credito")

    def __str__(self):
        return f"Crédito #{self.id_solicitacaoCredito} - {self.valor_solicitado}"
