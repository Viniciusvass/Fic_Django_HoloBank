from django.db import models

# Create your models here.
class Usuario(models.Model):
    id_usuario = models.BigAutoField(primary_key=True)
    isAdm = models.BooleanField(default=False)
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    senha = models.CharField(max_length=255)
    data_cadastro = models.DateField(auto_now_add=True)
    gerente_responsavel = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'isAdm': True},
        related_name='clientes_gerenciados'
    )
    
    def __str__(self):
        return self.nome