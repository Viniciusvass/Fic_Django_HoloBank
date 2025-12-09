from django.urls import path
from . import views

urlpatterns = [
    #cliente
    path("dashboard/", views.dashboard, name="dashboard"),
    path('transferir/', views.transferir, name='transferir'),
    path('extrato/', views.extrato, name='extrato'),
    #gerente
    path('dashboard_gerente/', views.dashboard_gerente, name='dashboard_gerente'),
    path("cliente/<int:id_usuario>/", views.detalhes_cliente, name="detalhes_cliente"),
    path("gerente/conta/<int:id_conta>/bloquear/", views.bloquear_conta, name="bloquear_conta"),
    path("gerente/conta/<int:id_conta>/reativar/", views.reativar_conta, name="reativar_conta"),

]
