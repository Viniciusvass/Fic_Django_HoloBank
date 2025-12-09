from django import forms

class TransferenciaForm(forms.Form):
    numero_destino = forms.CharField(
        label="Conta Destino",
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Número da conta destino'})
    )
    valor = forms.DecimalField(
        label="Valor",
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={'placeholder': 'R$ 0,00'})
    )
