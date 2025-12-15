from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from apps.creditos.models import SolicitacaoCredito
from apps.usuarios.models import Usuario
from .models import TipoCartao
from django.contrib import messages
from .models import TipoCartao, SolicitacaoCartao, CartaoCliente
from apps.contas.models import Conta
from django.utils import timezone
from .utils import gerar_numero_cartao, gerar_cvv, gerar_validade, gerar_senha
from decimal import Decimal

#cliente
def calcular_credito_aprovado(usuario):
    resultado = SolicitacaoCredito.objects.filter(
        solicitante=usuario,
        status_credito='aprovado'
    ).aggregate(total=Sum('valor_solicitado'))

    return resultado['total'] or 0

def listar_cartoes(request):
    if "usuario_id" not in request.session:
        return redirect("login")

    usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])

    credito_aprovado = SolicitacaoCredito.objects.filter(
        solicitante=usuario,
        status_credito='aprovado'
    ).aggregate(total=Sum('valor_solicitado'))['total'] or 0

    cartoes_disponiveis = []
    cartoes_indisponiveis = []

    for cartao in TipoCartao.objects.all():
        if cartao.tipo == 'debito':
            cartoes_disponiveis.append(cartao)
        else:
            if credito_aprovado >= cartao.limite_minimo:
                cartoes_disponiveis.append(cartao)
            else:
                cartoes_indisponiveis.append(cartao)

    context = {
        "usuario": usuario,
        "credito_aprovado": credito_aprovado,
        "cartoes_disponiveis": cartoes_disponiveis,
        "cartoes_indisponiveis": cartoes_indisponiveis,
    }

    return render(request, "listar_cartoes.html", context)

def meus_cartoes(request):
    if "usuario_id" not in request.session:
        return redirect("login")

    usuario = get_object_or_404(Usuario, id_usuario=request.session["usuario_id"])

    cartoes = CartaoCliente.objects.filter(
        solicitacao__solicitante=usuario,
        solicitacao__status="aprovado",
        ativo=True
    ).select_related("solicitacao__cartao")

    return render(request, "meus_cartoes.html", {
        "cartoes": cartoes
    })


#gerente
def solicitar_cartao(request, cartao_id):
    if "usuario_id" not in request.session:
        return redirect("login")

    cliente = get_object_or_404(Usuario, id_usuario=request.session["usuario_id"])
    cartao = get_object_or_404(TipoCartao, id=cartao_id)

    # Conta do cliente
    conta = Conta.objects.filter(usuario=cliente).first()

    if not conta:
        messages.error(request, "Você precisa ter uma conta ativa.")
        return redirect("listar_cartoes")

    # Impede duplicidade
    if SolicitacaoCartao.objects.filter(
        solicitante=cliente,
        cartao=cartao
    ).exclude(status="rejeitado").exists():
        messages.warning(request, "Você já solicitou este cartão.")
        return redirect("listar_cartoes")

    SolicitacaoCartao.objects.create(
        cartao=cartao,
        solicitante=cliente,
        gerente_responsavel=cliente.gerente_responsavel,
        conta=conta
    )

    messages.success(request, f"Solicitação do cartão {cartao.nome} enviada com sucesso!")
    return redirect("listar_cartoes")

def solicitacoes_cartao_gerente(request):
    if "usuario_id" not in request.session:
        return redirect("login")

    gerente = get_object_or_404(Usuario, id_usuario=request.session["usuario_id"])

    if not gerente.isAdm:
        return redirect("dashboard")

    solicitacoes = SolicitacaoCartao.objects.filter(
        gerente_responsavel=gerente,
        status='pendente'
    ).select_related('solicitante', 'cartao').order_by('-data_solicitacao')

    return render(request, "solicitacoes_cartao.html", {
        "solicitacoes": solicitacoes
    })

def aprovar_cartao(request, solicitacao_id):
    if "usuario_id" not in request.session:
        return redirect("login")

    gerente = get_object_or_404(Usuario, id_usuario=request.session["usuario_id"])

    if not gerente.isAdm:
        return redirect("dashboard")

    solicitacao = get_object_or_404(
        SolicitacaoCartao,
        id=solicitacao_id,
        gerente_responsavel=gerente
    )

    # Define limite
    tipo = solicitacao.cartao

    if tipo.tipo == "debito":
        limite = Decimal("0.00")
    else:
        limite = tipo.limite_maximo

    # Cria o cartão do cliente
    CartaoCliente.objects.create(
        solicitacao=solicitacao,
        numero=gerar_numero_cartao(),
        cvv=gerar_cvv(),
        senha=gerar_senha(),
        validade=gerar_validade(),
        limite=limite
    )

    solicitacao.status = "aprovado"
    solicitacao.data_analise = timezone.now()
    solicitacao.save()

    messages.success(request, "Cartão aprovado com sucesso!")
    return redirect("solicitacoes_cartao_gerente")

def rejeitar_cartao(request, solicitacao_id):
    if "usuario_id" not in request.session:
        return redirect("login")

    gerente = get_object_or_404(Usuario, id_usuario=request.session["usuario_id"])

    if not gerente.isAdm:
        return redirect("dashboard")

    solicitacao = get_object_or_404(
        SolicitacaoCartao,
        id=solicitacao_id,
        gerente_responsavel=gerente
    )

    solicitacao.status = "rejeitado"
    solicitacao.data_analise = timezone.now()
    solicitacao.save()

    messages.error(request, "Solicitação rejeitada.")
    return redirect("solicitacoes_cartao_gerente")
