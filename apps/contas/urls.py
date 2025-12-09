from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path('transferir/', views.transferir, name='transferir'),
    path('extrato/', views.extrato, name='extrato'),

]
