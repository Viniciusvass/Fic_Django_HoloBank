from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .forms import UsuarioForm, LoginForm
from .models import Usuario
import random
from apps.contas.models import Conta

# Create your views here.
def cadastro(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.senha = make_password(form.cleaned_data['senha'])
            usuario.save()

            # Criar conta automática com o tipo escolhido
            tipo_conta = form.cleaned_data['tipo_conta']
            numero_conta = str(random.randint(10000000, 99999999))
            Conta.objects.create(
                numero_conta=numero_conta,
                tipo_conta=tipo_conta,
                usuario=usuario
            )

            return redirect('index')
    else:
        form = UsuarioForm()

    return render(request, 'cliente/cadastro.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            senha = form.cleaned_data['senha']
            try:
                usuario = Usuario.objects.get(email=email)
                
                if check_password(senha, usuario.senha):
                    request.session["usuario_id"] = usuario.id_usuario
                    messages.success(request, f"Bem-vindo, {usuario.nome}!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Senha incorreta.")
            except Usuario.DoesNotExist:
                messages.error(request, "Usuário não encontrado.")
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def logout(request):
    request.session.pop("usuario_id", None)
    messages.success(request, "Logout realizado com sucesso.")
    return redirect('index')
