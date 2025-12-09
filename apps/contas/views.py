from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario, Conta, Extrato
from django.contrib import messages
from .forms import TransferenciaForm
from apps.transacoes.models import Transacao
from django.contrib.auth.decorators import login_required

# Create your views here.
def dashboard(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect('login')
    
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    contas = Conta.objects.filter(usuario=usuario)
    saldo_total = sum(conta.saldo for conta in contas)

    context = {
        'usuario': usuario,
        'contas': contas,
        'saldo_total': saldo_total,
    }
    return render(request, 'cliente/dashboard.html', context)

def get_usuario_logado(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        return get_object_or_404(Usuario, id_usuario=usuario_id)
    return None

def transferir(request):
    usuario = get_usuario_logado(request)
    if not usuario:
        return redirect('/login/')

    conta_origem = get_object_or_404(Conta, usuario=usuario)

    if request.method == 'POST':
        form = TransferenciaForm(request.POST)
        if form.is_valid():
            numero_destino = form.cleaned_data['numero_destino']
            valor = form.cleaned_data['valor']

            try:
                conta_destino = get_object_or_404(Conta, numero_conta=numero_destino)

                if conta_origem.saldo < valor:
                    form.add_error('valor', 'Saldo insuficiente para realizar a transferência.')
                else:
                    conta_origem.saldo -= valor
                    conta_destino.saldo += valor
                    conta_origem.save()
                    conta_destino.save()

                    Transacao.objects.create(
                        valor=valor,
                        conta_origem=conta_origem,
                        conta_destino=conta_destino
                    )

                    Extrato.objects.create(
                        conta=conta_origem,
                        valor=-valor,
                        descricao=f'Transferência para {conta_destino.numero_conta}'
                    )

                    Extrato.objects.create(
                        conta=conta_destino,
                        valor=valor,
                        descricao=f'Transferência recebida de {conta_origem.numero_conta}'
                    )

                    return redirect('dashboard')
            except:
                form.add_error('numero_destino', 'Conta destino inválida.')
    else:
        form = TransferenciaForm()

    return render(request, 'cliente/transferir.html', {'form': form})

def extrato(request):
    conta = get_object_or_404(Conta, usuario_id=request.session.get("usuario_id"))

    transacoes = Transacao.objects.filter(
        conta_origem=conta
    ).union(
        Transacao.objects.filter(conta_destino=conta)
    ).order_by('-data_hora')

    return render(request, 'cliente/extrato.html', {
        'transacoes': transacoes,
        'conta': conta
    })
