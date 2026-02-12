from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
from apps.creditos.models import SolicitacaoCredito
from apps.creditos.forms import SolicitacaoCreditoForm
from apps.usuarios.models import Usuario

# FORMS
class SolicitacaoCreditoFormTest(TestCase):
    def test_form_valido(self):
        form = SolicitacaoCreditoForm(data={'valor_solicitado': '1500.50'})
        self.assertTrue(form.is_valid())

    def test_form_invalido_valor_negativo(self):
        form = SolicitacaoCreditoForm(data={'valor_solicitado': '-500.00'})
        self.assertFalse(form.is_valid())


# MODEL
class SolicitacaoCreditoModelTest(TestCase):
    def setUp(self):
        self.usuario_solicitante = Usuario.objects.create(
            email="cliente@test.com",
            isAdm=False
        )
        self.gerente = Usuario.objects.create(
            email="gerente@test.com",
            isAdm=True
        )

    def test_criacao_solicitacao_credito(self):
        solicitacao = SolicitacaoCredito.objects.create(
            valor_solicitado=Decimal('1500.50'),
            taxa_juros=1.5,
            solicitante=self.usuario_solicitante,
            gerente_responsavel=self.gerente
        )
        self.assertEqual(solicitacao.valor_solicitado, Decimal('1500.50'))
        self.assertEqual(solicitacao.taxa_juros, 1.5)
        self.assertEqual(solicitacao.status_credito, 'pendente')
        self.assertEqual(solicitacao.solicitante, self.usuario_solicitante)
        self.assertEqual(solicitacao.gerente_responsavel, self.gerente)
        self.assertIsNotNone(solicitacao.data_solicitacao)
        self.assertIsNone(solicitacao.data_analise)

    def test_str_retorna_valor_corretamente(self):
        solicitacao = SolicitacaoCredito.objects.create(
            valor_solicitado=Decimal('2000.00'),
            taxa_juros=2.0,
            solicitante=self.usuario_solicitante,
            gerente_responsavel=self.gerente
        )
        self.assertEqual(str(solicitacao), f"Crédito #{solicitacao.id_solicitacaoCredito} - {solicitacao.valor_solicitado}")

    def test_status_credito_default(self):
        solicitacao = SolicitacaoCredito.objects.create(
            valor_solicitado=Decimal('1000.00'),
            taxa_juros=1.2,
            solicitante=self.usuario_solicitante,
            gerente_responsavel=self.gerente
        )
        self.assertEqual(solicitacao.status_credito, 'pendente')


# VIEWS
class SolicitacaoCreditoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(
            email="cliente@test.com",
            isAdm=False
        )
        self.gerente = Usuario.objects.create(
            email="gerente@test.com",
            isAdm=True
        )
        self.usuario.gerente_responsavel = self.gerente
        self.usuario.save()

    def test_solicitar_credito_redireciona_login_quando_nao_logado(self):
        response = self.client.get(reverse('solicitar_credito'))
        self.assertRedirects(response, reverse('login'))

    def test_solicitar_credito_get_form(self):
        session = self.client.session
        session['usuario_id'] = self.usuario.id_usuario
        session.save()
        response = self.client.get(reverse('solicitar_credito'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('usuario', response.context)
        self.assertIn('gerente', response.context)

    def test_solicitar_credito_post_valido_cria_solicitacao(self):
        session = self.client.session
        session['usuario_id'] = self.usuario.id_usuario
        session.save()
        response = self.client.post(reverse('solicitar_credito'), {'valor_solicitado': '1500.50'})
        self.assertRedirects(response, reverse('dashboard'))
        solicitacao = SolicitacaoCredito.objects.first()
        self.assertEqual(solicitacao.valor_solicitado, Decimal('1500.50'))
        self.assertEqual(solicitacao.taxa_juros, 5.0)
        self.assertEqual(solicitacao.solicitante, self.usuario)
        self.assertEqual(solicitacao.gerente_responsavel, self.gerente)
        self.assertEqual(solicitacao.status_credito, 'pendente')

    def test_minhas_solicitacoes_redireciona_login(self):
        response = self.client.get(reverse('minhas_solicitacoes'))
        self.assertRedirects(response, reverse('login'))

    def test_minhas_solicitacoes_lista_corretamente(self):
        SolicitacaoCredito.objects.create(
            valor_solicitado=1000.0,
            taxa_juros=2.0,
            solicitante=self.usuario,
            gerente_responsavel=self.gerente
        )
        session = self.client.session
        session['usuario_id'] = self.usuario.id_usuario
        session.save()
        response = self.client.get(reverse('minhas_solicitacoes'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['solicitacoes']), 1)

    def test_listar_solicitacoes_credito_redireciona_login(self):
        response = self.client.get(reverse('listar_solicitacoes_credito'))
        self.assertRedirects(response, reverse('login'))

    def test_listar_solicitacoes_credito_restringe_nao_adm(self):
        nao_adm = Usuario.objects.create(email='user@test.com', isAdm=False)
        session = self.client.session
        session['usuario_id'] = nao_adm.id_usuario
        session.save()
        response = self.client.get(reverse('listar_solicitacoes_credito'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_atualizar_status_credito_aprovar(self):
        solicitacao = SolicitacaoCredito.objects.create(
            valor_solicitado=1000.0,
            taxa_juros=2.0,
            solicitante=self.usuario,
            gerente_responsavel=self.gerente
        )
        session = self.client.session
        session['usuario_id'] = self.gerente.id_usuario
        session.save()
        response = self.client.get(reverse('atualizar_status_credito', args=[solicitacao.id_solicitacaoCredito]) + '?acao=aprovar')
        self.assertRedirects(response, reverse('listar_solicitacoes_credito'))
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status_credito, 'aprovado')
        self.assertIsNotNone(solicitacao.data_analise)

    def test_atualizar_status_credito_rejeitar(self):
        solicitacao = SolicitacaoCredito.objects.create(
            valor_solicitado=1000.0,
            taxa_juros=2.0,
            solicitante=self.usuario,
            gerente_responsavel=self.gerente
        )
        session = self.client.session
        session['usuario_id'] = self.gerente.id_usuario
        session.save()
        response = self.client.get(reverse('atualizar_status_credito', args=[solicitacao.id_solicitacaoCredito]) + '?acao=rejeitar')
        self.assertRedirects(response, reverse('listar_solicitacoes_credito'))
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status_credito, 'rejeitado')
        self.assertIsNotNone(solicitacao.data_analise)
