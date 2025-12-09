from django.db import models
from apps.usuarios.models import Usuario

# Create your models here.
class Conta(models.Model):
    TIPO_CONTA = (
        ('corrente', 'Corrente'),
        ('poupanca', 'Poupança'),
    )
    STATUS_CONTA = (
        ('ativa', 'Ativa'),
        ('bloqueada', 'Bloqueada'),
    )
    id_conta = models.BigAutoField(primary_key=True)
    numero_conta = models.CharField(max_length=20, unique=True)
    tipo_conta = models.CharField(max_length=20, choices=TIPO_CONTA)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status_conta = models.CharField(max_length=20, choices=STATUS_CONTA, default='ativa')
    data_abertura = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.numero_conta} - {self.usuario.nome}"

class Extrato(models.Model):
    id_extrato = models.BigAutoField(primary_key=True)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    data_emissao = models.DateTimeField(auto_now_add=True)
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descricao = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.descricao or 'Transação'} de R${self.valor} - {self.data_emissao.strftime('%d/%m/%Y %H:%M')}"
