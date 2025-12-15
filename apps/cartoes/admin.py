from django.contrib import admin
from .models import TipoCartao, SolicitacaoCartao, CartaoCliente

# Register your models here.
admin.site.register(TipoCartao)
admin.site.register(SolicitacaoCartao)
admin.site.register(CartaoCliente)