from django import forms
from .models import Usuario

TIPO_CONTA = (
    ('corrente', 'Corrente'),
    ('poupanca', 'Poupança'),
)

class UsuarioForm(forms.ModelForm):
    tipo_conta = forms.ChoiceField(choices=TIPO_CONTA, label="Tipo de Conta")
    
    class Meta:
        model = Usuario
        fields = ['nome', 'cpf', 'email', 'telefone', 'senha']
        

class LoginForm(forms.Form):
    email = forms.EmailField(label="E-mail", max_length=200)
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")
