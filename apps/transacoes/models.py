from django.db import models
from apps.contas.models import Conta

# Create your models here.
class Transacao(models.Model):
    STATUS_TRANSACAO = (
    ('pendente', 'Pendente'),
    ('concluida', 'Concluída'),
    ('falhou', 'Falhou'),
)
    
    id_transacao = models.BigAutoField(primary_key=True)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_hora = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField(blank=True, null=True, default="Transferência realizada")
    conta_origem = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='transacoes_origem')
    conta_destino = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='transacoes_destino')
    status = models.CharField(max_length=20, choices=STATUS_TRANSACAO, default='concluida')
    
    def __str__(self):
        return f"De {self.conta_origem.numero_conta} para {self.conta_destino.numero_conta} - R$ {self.valor}"
