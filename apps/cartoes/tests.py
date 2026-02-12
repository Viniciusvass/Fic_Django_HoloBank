from django.test import TestCase, Client
from apps.cartoes.models import TipoCartao, SolicitacaoCartao, CartaoCliente
from apps.usuarios.models import Usuario
from apps.contas.models import Conta
from datetime import date, timedelta
import random
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from apps.cartoes.utils import gerar_numero_cartao, gerar_cvv, gerar_validade, gerar_senha

# MODEL
class TipoCartaoModelTest(TestCase):
    def test_criacao_tipo_cartao(self):
        cartao = TipoCartao.objects.create(
            nome="Gold",
            tipo="credito",
            limite_minimo=1000,
            limite_maximo=10000,
            vantagens="Cashback e pontos"
        )
        self.assertEqual(cartao.nome, "Gold")
        self.assertEqual(cartao.tipo, "credito")
        self.assertEqual(str(cartao), "Gold (Crédito)")

class SolicitacaoCartaoModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            email="usuario_cartao@test.com",
            cpf=f"000000000{Usuario.objects.count()}",
            nome="Cliente Teste"
        )
        self.conta = Conta.objects.create(
            usuario=self.usuario,
            saldo=1000
        )
        self.tipo_cartao = TipoCartao.objects.create(
            nome="Gold",
            tipo="credito",
            limite_minimo=1000,
            limite_maximo=10000,
            vantagens="Cashback e pontos"
        )

    def test_criacao_solicitacao_cartao(self):
        solicitacao = SolicitacaoCartao.objects.create(
            cartao=self.tipo_cartao,
            solicitante=self.usuario,
            conta=self.conta
        )
        self.assertEqual(solicitacao.status, "pendente")
        self.assertEqual(str(solicitacao), f"{self.tipo_cartao.nome} - {self.usuario.nome}")

class CartaoClienteModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            email="usuario_cartao2@test.com",
            cpf=f"111111111{Usuario.objects.count()}",
            nome="Cliente Teste 2"
        )
        self.conta = Conta.objects.create(
            usuario=self.usuario,
            saldo=500
        )
        self.tipo_cartao = TipoCartao.objects.create(
            nome="Platinum",
            tipo="credito",
            limite_minimo=5000,
            limite_maximo=20000,
            vantagens="Cashback, pontos e seguro viagem"
        )
        self.solicitacao = SolicitacaoCartao.objects.create(
            cartao=self.tipo_cartao,
            solicitante=self.usuario,
            conta=self.conta
        )

    def test_criacao_cartao_cliente(self):
        cartao_cliente = CartaoCliente.objects.create(
            solicitacao=self.solicitacao,
            numero="1234567812345678",
            cvv="123",
            senha="4321",
            validade=date.today() + timedelta(days=365*3),
            limite=10000
        )
        self.assertTrue(cartao_cliente.ativo)
        self.assertEqual(str(cartao_cliente), f"Cartão **** {cartao_cliente.numero[-4:]}")

# UTILS
def gerar_numero_cartao():
    return ''.join(str(random.randint(0, 9)) for _ in range(16))

def gerar_cvv():
    return ''.join(str(random.randint(0, 9)) for _ in range(3))

def gerar_validade():
    hoje = date.today()
    return hoje.replace(year=hoje.year + 5)

def gerar_senha():
    return ''.join(str(random.randint(0, 9)) for _ in range(4))

class CartaoClienteModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            email="usuario_cartao2@test.com",
            cpf=f"111111111{Usuario.objects.count()}",
            nome="Cliente Teste 2"
        )
        self.conta = Conta.objects.create(
            usuario=self.usuario,
            saldo=500
        )
        self.tipo_cartao = TipoCartao.objects.create(
            nome="Platinum",
            tipo="credito",
            limite_minimo=5000,
            limite_maximo=20000,
            vantagens="Cashback, pontos e seguro viagem"
        )
        self.solicitacao = SolicitacaoCartao.objects.create(
            cartao=self.tipo_cartao,
            solicitante=self.usuario,
            conta=self.conta
        )

    def test_criacao_cartao_cliente(self):
        cartao_cliente = CartaoCliente.objects.create(
            solicitacao=self.solicitacao,
            numero=gerar_numero_cartao(),
            cvv=gerar_cvv(),
            senha=gerar_senha(),
            validade=gerar_validade(),
            limite=10000
        )
        self.assertTrue(cartao_cliente.ativo)
        self.assertEqual(str(cartao_cliente), f"Cartão **** {cartao_cliente.numero[-4:]}")

# VIEWS
class CartaoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.cliente = Usuario.objects.create(
            email="cliente_cartao@test.com",
            cpf="12345678901",
            nome="Cliente Teste"
        )
        self.cliente.gerente_responsavel = self.cliente
        self.cliente.save()

        self.conta = Conta.objects.create(
            usuario=self.cliente,
            saldo=5000
        )

        self.gerente = Usuario.objects.create(
            email="gerente@test.com",
            cpf="10987654321",
            nome="Gerente Teste",
            isAdm=True
        )

        self.cartao_credito = TipoCartao.objects.create(
            nome="Gold",
            tipo="credito",
            limite_minimo=1000,
            limite_maximo=10000,
            vantagens="Cashback"
        )
        self.cartao_debito = TipoCartao.objects.create(
            nome="Debit",
            tipo="debito",
            limite_minimo=0,
            limite_maximo=0,
            vantagens="Sem anuidade"
        )

    def test_listar_cartoes_disponiveis_e_indisponiveis(self):
        self.client.session['usuario_id'] = self.cliente.id_usuario
        self.client.session.save()

        response = self.client.get(reverse('listar_cartoes'))
        self.assertContains(response, "Debit")
        self.assertNotContains(response, "Gold")

        SolicitacaoCartao.objects.create(
            cartao=self.cartao_credito,
            solicitante=self.cliente,
            gerente_responsavel=self.gerente,
            conta=self.conta,
            status='aprovado'
        )
        response = self.client.get(reverse('listar_cartoes'))
        self.assertContains(response, "Gold")
        self.assertContains(response, "Debit")

    def test_solicitar_cartao_e_duplicidade(self):
        self.client.session['usuario_id'] = self.cliente.id_usuario
        self.client.session.save()
        
        url = reverse('solicitar_cartao', args=[self.cartao_credito.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        response = self.client.post(url)
        self.assertEqual(SolicitacaoCartao.objects.count(), 1)
        
        response = self.client.post(url, follow=True)
        self.assertContains(response, "Você já solicitou este cartão.")

    def test_aprovar_cartao_cria_cartao_cliente(self):
        solicitacao = SolicitacaoCartao.objects.create(
            cartao=self.cartao_credito,
            solicitante=self.cliente,
            gerente_responsavel=self.gerente,
            conta=self.conta
        )

        self.client.session['usuario_id'] = self.gerente.id_usuario
        self.client.session.save()

        url = reverse('aprovar_cartao', args=[solicitacao.id])
        response = self.client.post(url, follow=True)
        
        solicitacao.refresh_from_db()
        cartao_cliente = CartaoCliente.objects.get(solicitacao=solicitacao)

        self.assertEqual(solicitacao.status, 'aprovado')
        self.assertIsNotNone(cartao_cliente)
        self.assertTrue(cartao_cliente.ativo)

    def test_rejeitar_cartao_altera_status(self):
        solicitacao = SolicitacaoCartao.objects.create(
            cartao=self.cartao_credito,
            solicitante=self.cliente,
            gerente_responsavel=self.gerente,
            conta=self.conta
        )

        self.client.session['usuario_id'] = self.gerente.id_usuario
        self.client.session.save()

        url = reverse('rejeitar_cartao', args=[solicitacao.id])
        response = self.client.post(url, follow=True)
        
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, 'rejeitado')
