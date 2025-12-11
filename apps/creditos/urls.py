from django.urls import path
from . import views

urlpatterns = [
    path('solicitar/', views.solicitar_credito, name="solicitar_credito"),
    path('minhas_solicitações/', views.minhas_solicitacoes, name='minhas_solicitacoes'),
    path("gerente/solicitacoes/", views.listar_solicitacoes_credito, name="listar_solicitacoes_credito"),
    path("gerente/solicitacoes/<int:id>/acao/", views.atualizar_status_credito, name="atualizar_status_credito"),

]