from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario, Conta, Extrato
from .forms import TransferenciaForm
from apps.transacoes.models import Transacao
from apps.creditos.models import SolicitacaoCredito

#cliente
def dashboard(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect('login')    
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    contas = Conta.objects.filter(usuario=usuario)
    creditos = SolicitacaoCredito.objects.filter(solicitante=usuario)
    credito_total = creditos.count()
    credito_aprovado = creditos.filter(status_credito="aprovado").count()
    credito_pendente = creditos.filter(status_credito="pendente").count()
    credito_rejeitado = creditos.filter(status_credito="rejeitado").count()
    credito_ultimo = creditos.order_by("-data_solicitacao").first()
    saldo_total = sum(conta.saldo for conta in contas)
    context = {
        'usuario': usuario,
        'contas': contas,
        'credito_total': credito_total,
        'credito_aprovado': credito_aprovado,
        'credito_pendente': credito_pendente,
        'credito_rejeitado': credito_rejeitado,
        'credito_ultimo': credito_ultimo,
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
    
#gerente
def dashboard_gerente(request):
    if not request.session.get("isAdm"):
        return redirect('login')
    gerente_id = request.session.get("usuario_id")
    gerente = Usuario.objects.get(id_usuario=gerente_id)
    clientes = Usuario.objects.filter(gerente_responsavel_id=gerente_id, isAdm=False)
    return render(request, "gerente/dashboard_gerente.html", {
        'gerente': gerente,
        "clientes": clientes
    })

def detalhes_cliente(request, id_usuario):
    if not request.session.get("isAdm"):
        return redirect('login')
    cliente = get_object_or_404(Usuario, id_usuario=id_usuario)
    conta = get_object_or_404(Conta, usuario=cliente)
    return render(request, "gerente/detalhes_cliente.html", {
        "cliente": cliente,
        "conta": conta
    })

def bloquear_conta(request, id_conta):
    if not request.session.get("isAdm"):
        return redirect('login')
    conta = get_object_or_404(Conta, id_conta=id_conta)
    conta.status_conta = "bloqueada"
    conta.save()
    return redirect('detalhes_cliente', id_usuario=conta.usuario.id_usuario)

def reativar_conta(request, id_conta):
    if not request.session.get("isAdm"):
        return redirect('login')
    conta = get_object_or_404(Conta, id_conta=id_conta)
    conta.status_conta = "ativa"
    conta.save()
    return redirect('detalhes_cliente', id_usuario=conta.usuario.id_usuario)
