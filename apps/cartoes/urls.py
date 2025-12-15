from django.urls import path
from . import views

urlpatterns = [
    #cliente
    path('listar_cartoes/', views.listar_cartoes, name='listar_cartoes'),
    path('solicitar/<int:cartao_id>/', views.solicitar_cartao, name='solicitar_cartao'),
    path('gerente/cartoes/', views.solicitacoes_cartao_gerente, name='solicitacoes_cartao_gerente'),
    path("meus-cartoes/", views.meus_cartoes, name="meus_cartoes"),
    #gerente
    path('gerente/cartoes/aprovar/<int:solicitacao_id>/', views.aprovar_cartao, name='aprovar_cartao'),
    path('gerente/cartoes/rejeitar/<int:solicitacao_id>/', views.rejeitar_cartao, name='rejeitar_cartao'),

]