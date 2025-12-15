from django.db import models
from apps.usuarios.models import Usuario
from apps.contas.models import Conta
from django.utils import timezone
import random
from datetime import date


# Create your models here.
class TipoCartao(models.Model):
    TIPO = (
        ('debito', 'Débito'),
        ('credito', 'Crédito'),
    )
    id = models.BigAutoField(primary_key=True, null=False, blank=False)
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPO)
    limite_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    limite_maximo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vantagens = models.TextField()

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class SolicitacaoCartao(models.Model):
    STATUS = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    )
    id = models.BigAutoField(primary_key=True, null=False, blank=False)
    cartao = models.ForeignKey('TipoCartao', on_delete=models.CASCADE)
    solicitante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='solicitacoes_cartao'
    )
    gerente_responsavel = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cartoes_para_aprovar'
    )
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS, default='pendente')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_analise = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.cartao.nome} - {self.solicitante.nome}"

class CartaoCliente(models.Model):
    solicitacao = models.OneToOneField(
        SolicitacaoCartao,
        on_delete=models.CASCADE
    )
    id = models.BigAutoField(primary_key=True, null=False, blank=False)
    numero = models.CharField(max_length=16, unique=True)
    cvv = models.CharField(max_length=3)
    senha = models.CharField(max_length=4)
    validade = models.DateField()
    limite = models.DecimalField(max_digits=12, decimal_places=2)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Cartão **** {self.numero[-4:]}"
