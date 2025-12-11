from django.shortcuts import render, redirect
from .forms import SolicitacaoCreditoForm
from apps.usuarios.models import Usuario
from .models import SolicitacaoCredito

#cliente
def solicitar_credito(request):
    if "usuario_id" not in request.session:
        return redirect("login")
    usuario_logado = Usuario.objects.get(id_usuario=request.session["usuario_id"])
    gerente = usuario_logado.gerente_responsavel
    if request.method == "POST":
        form = SolicitacaoCreditoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.taxa_juros = 5.0
            solicitacao.solicitante = usuario_logado
            solicitacao.gerente_responsavel = gerente
            solicitacao.save()
            return redirect("dashboard")
    else:
        form = SolicitacaoCreditoForm()
    return render(request, "solicitar_credito.html",{"form": form, "usuario": usuario_logado, "gerente": gerente})

def minhas_solicitacoes(request):
    if "usuario_id" not in request.session:
        return redirect("login")
    usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])
    solicitacoes = SolicitacaoCredito.objects.filter(
        solicitante=usuario
    ).order_by("-data_solicitacao")
    return render(request, "minhas_solicitacoes.html", {"usuario": usuario, "solicitacoes": solicitacoes})

#gerente
def listar_solicitacoes_credito(request):
    if "usuario_id" not in request.session:
        return redirect("login")
    gerente = Usuario.objects.get(id_usuario=request.session["usuario_id"])
    if not gerente.isAdm:
        return redirect("dashboard")
    solicitacoes = SolicitacaoCredito.objects.filter(
        gerente_responsavel=gerente
    ).order_by("-data_solicitacao")
    return render(request, "listar_solicitacoes_credito.html", {"solicitacoes": solicitacoes, "gerente": gerente})

from django.utils import timezone

def atualizar_status_credito(request, id):
    if "usuario_id" not in request.session:
        return redirect("login")
    acao = request.GET.get("acao")
    solicitacao = SolicitacaoCredito.objects.get(id_solicitacaoCredito=id)
    if acao == "aprovar":
        solicitacao.status_credito = "aprovado"
    elif acao == "rejeitar":
        solicitacao.status_credito = "rejeitado"
    solicitacao.data_analise = timezone.now()
    solicitacao.save()
    return redirect("listar_solicitacoes_credito")
