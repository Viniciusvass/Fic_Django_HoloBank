from django.db import models
from apps.usuarios.models import Usuario
from apps.contas.models import Conta

# Create your models here.
class SolicitacaoCartao(models.Model):
    STATUS = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    )
    TIPO = (
        ('credito', 'Crédito'),
        ('debito', 'Débito'),
    )
    id_solicitacaoCartao = models.BigAutoField(primary_key=True)
    tipo_cartao = models.CharField(max_length=20, choices=TIPO)
    status_solicitacao = models.CharField(max_length=20, choices=STATUS, default='pendente')
    data_solicitacao = models.DateField(auto_now_add=True)
    data_analise = models.DateField(null=True, blank=True)
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="solicitacoes_cartao")
    gerente_responsavel = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name="analises_cartao")

    def __str__(self):
        return f"Solicitação #{self.id} - {self.tipo_cartao}"


class Cartao(models.Model):
    STATUS_CARTAO = (
        ('solicitado', 'Solicitado'),
        ('aprovado', 'Aprovado'),
        ('bloqueado', 'Bloqueado'),
    )
    id_cartao = models.BigAutoField(primary_key=True)
    numero_cartao = models.CharField(max_length=20, unique=True)
    limite_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status_cartao = models.CharField(max_length=20, choices=STATUS_CARTAO)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.numero_cartao}"