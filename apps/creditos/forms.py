from django.forms import ModelForm
from .models import SolicitacaoCredito

class SolicitacaoCreditoForm(ModelForm):
    class Meta:
        model = SolicitacaoCredito
        fields = ['valor_solicitado']
