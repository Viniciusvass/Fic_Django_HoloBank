from django.test import TestCase
from .forms import TransferenciaForm
from django.db.utils import IntegrityError
from apps.usuarios.models import Usuario
from apps.contas.models import Conta, Extrato
from django.urls import reverse
from decimal import Decimal
from apps.transacoes.models import Transacao

# FORMS
class TransferenciaFormTest(TestCase):

    def test_form_transferencia_valido(self):
        form = TransferenciaForm(data={
            'numero_destino': '12345678',
            'valor': '150.00'
        })

        self.assertTrue(form.is_valid())

    def test_form_sem_numero_destino(self):
        form = TransferenciaForm(data={
            'valor': '100.00'
        })

        self.assertFalse(form.is_valid())

    def test_form_sem_valor(self):
        form = TransferenciaForm(data={
            'numero_destino': '12345678'
        })

        self.assertFalse(form.is_valid())

    def test_form_valor_zero(self):
        form = TransferenciaForm(data={
            'numero_destino': '12345678',
            'valor': '0'
        })

        self.assertFalse(form.is_valid())

    def test_form_valor_negativo(self):
        form = TransferenciaForm(data={
            'numero_destino': '12345678',
            'valor': '-50'
        })

        self.assertFalse(form.is_valid())

    def test_form_valor_decimal_valido(self):
        form = TransferenciaForm(data={
            'numero_destino': '12345678',
            'valor': '25.75'
        })

        self.assertTrue(form.is_valid())

# MODELS
class ContaModelTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Vinicius",
            cpf="12345678999",
            email="vinicius@email.com",
            telefone="81999999999",
            senha="123456"
        )

    def test_criar_conta_padrao(self):
        conta = Conta.objects.create(
            numero_conta="10020030",
            tipo_conta="corrente",
            usuario=self.usuario
        )

        self.assertEqual(conta.saldo, 0)
        self.assertEqual(conta.status_conta, "ativa")

    def test_numero_conta_unico(self):
        Conta.objects.create(
            numero_conta="99988877",
            tipo_conta="corrente",
            usuario=self.usuario
        )

        with self.assertRaises(IntegrityError):
            Conta.objects.create(
                numero_conta="99988877",
                tipo_conta="poupanca",
                usuario=self.usuario
            )

    def test_relacao_conta_usuario(self):
        conta = Conta.objects.create(
            numero_conta="55544433",
            tipo_conta="corrente",
            usuario=self.usuario
        )

        self.assertEqual(conta.usuario.nome, "Vinicius")

    def test_str_conta(self):
        conta = Conta.objects.create(
            numero_conta="12345678",
            tipo_conta="corrente",
            usuario=self.usuario
        )

        self.assertIn("12345678", str(conta))


class ExtratoModelTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Maria",
            cpf="88877766655",
            email="maria@email.com",
            telefone="81988888888",
            senha="123456"
        )

        self.conta = Conta.objects.create(
            numero_conta="22233344",
            tipo_conta="poupanca",
            usuario=self.usuario
        )

    def test_criar_extrato(self):
        extrato = Extrato.objects.create(
            conta=self.conta,
            valor=150.50,
            descricao="Depósito inicial"
        )

        self.assertEqual(extrato.valor, 150.50)
        self.assertEqual(extrato.descricao, "Depósito inicial")

    def test_extrato_associado_conta(self):
        extrato = Extrato.objects.create(
            conta=self.conta,
            valor=20
        )

        self.assertEqual(extrato.conta.numero_conta, "22233344")

    def test_str_extrato(self):
        extrato = Extrato.objects.create(
            conta=self.conta,
            valor=50,
            descricao="Saque"
        )

        self.assertIn("Saque", str(extrato))

# VIEWS
class DashboardClienteViewTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Cliente",
            cpf="11122233344",
            email="cliente@email.com",
            telefone="81999999999",
            senha="123456"
        )

        self.conta = Conta.objects.create(
            numero_conta="10000001",
            tipo_conta="corrente",
            saldo=Decimal('500.00'),
            usuario=self.usuario
        )

    def test_dashboard_sem_login_redireciona(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_logado_carrega(self):
        session = self.client.session
        session["usuario_id"] = self.usuario.id_usuario
        session.save()

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class TransferenciaViewTest(TestCase):

    def setUp(self):
        self.usuario_origem = Usuario.objects.create(
            nome="Origem",
            cpf="55566677788",
            email="origem@email.com",
            telefone="81111111111",
            senha="123"
        )

        self.usuario_destino = Usuario.objects.create(
            nome="Destino",
            cpf="99988877766",
            email="destino@email.com",
            telefone="82222222222",
            senha="123"
        )

        self.conta_origem = Conta.objects.create(
            numero_conta="20000001",
            tipo_conta="corrente",
            saldo=Decimal('300.00'),
            usuario=self.usuario_origem
        )

        self.conta_destino = Conta.objects.create(
            numero_conta="20000002",
            tipo_conta="corrente",
            saldo=Decimal('100.00'),
            usuario=self.usuario_destino
        )

        session = self.client.session
        session["usuario_id"] = self.usuario_origem.id_usuario
        session.save()

    def test_transferencia_sucesso(self):
        response = self.client.post(reverse('transferir'), {
            'numero_destino': '20000002',
            'valor': '50.00'
        })

        self.conta_origem.refresh_from_db()
        self.conta_destino.refresh_from_db()

        self.assertEqual(self.conta_origem.saldo, Decimal('250.00'))
        self.assertEqual(self.conta_destino.saldo, Decimal('150.00'))
        self.assertEqual(Transacao.objects.count(), 1)
        self.assertEqual(Extrato.objects.count(), 2)
        self.assertEqual(response.status_code, 302)

    def test_transferencia_saldo_insuficiente(self):
        response = self.client.post(reverse('transferir'), {
            'numero_destino': '20000002',
            'valor': '500.00'
        })

        self.assertContains(response, 'Saldo insuficiente')

    def test_transferencia_conta_invalida(self):
        response = self.client.post(reverse('transferir'), {
            'numero_destino': '00000000',
            'valor': '10.00'
        })

        self.assertContains(response, 'Conta destino inválida')


class ExtratoViewTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Cliente",
            cpf="12121212121",
            email="cliente2@email.com",
            telefone="81988888888",
            senha="123"
        )

        self.conta = Conta.objects.create(
            numero_conta="30000001",
            tipo_conta="corrente",
            usuario=self.usuario
        )

        session = self.client.session
        session["usuario_id"] = self.usuario.id_usuario
        session.save()

    def test_extrato_carrega(self):
        response = self.client.get(reverse('extrato'))
        self.assertEqual(response.status_code, 200)


class GerenteViewsTest(TestCase):

    def setUp(self):
        self.gerente = Usuario.objects.create(
            nome="Gerente",
            cpf="99900011122",
            email="gerente@email.com",
            telefone="81977777777",
            senha="admin",
            isAdm=True
        )

        self.cliente = Usuario.objects.create(
            nome="Cliente",
            cpf="44433322211",
            email="cliente3@email.com",
            telefone="81966666666",
            senha="123",
            gerente_responsavel=self.gerente
        )

        self.conta = Conta.objects.create(
            numero_conta="40000001",
            tipo_conta="corrente",
            usuario=self.cliente
        )

        session = self.client.session
        session["usuario_id"] = self.gerente.id_usuario
        session["isAdm"] = True
        session.save()

    def test_dashboard_gerente(self):
        response = self.client.get(reverse('dashboard_gerente'))
        self.assertEqual(response.status_code, 200)

    def test_bloquear_conta(self):
        response = self.client.get(reverse('bloquear_conta', args=[self.conta.id_conta]))

        self.conta.refresh_from_db()
        self.assertEqual(self.conta.status_conta, 'bloqueada')

    def test_reativar_conta(self):
        self.conta.status_conta = 'bloqueada'
        self.conta.save()

        response = self.client.get(reverse('reativar_conta', args=[self.conta.id_conta]))

        self.conta.refresh_from_db()
        self.assertEqual(self.conta.status_conta, 'ativa')
