from django.test import TestCase
from apps.transacoes.models import Transacao
from apps.contas.models import Conta
from apps.usuarios.models import Usuario

# MODEL
class TransacaoModelTest(TestCase):

    def setUp(self):
        self.usuario1 = Usuario.objects.create(
            nome="João",
            email="joao@test.com",
            senha="123",
            cpf="11111111111"
        )

        self.usuario2 = Usuario.objects.create(
            nome="Maria",
            email="maria@test.com",
            senha="123",
            cpf="22222222222"
        )

        self.conta_origem = Conta.objects.create(
            numero_conta="11111111",
            tipo_conta="corrente",
            usuario=self.usuario1,
            saldo=1000
        )

        self.conta_destino = Conta.objects.create(
            numero_conta="22222222",
            tipo_conta="corrente",
            usuario=self.usuario2,
            saldo=500
        )

        self.transacao = Transacao.objects.create(
            valor=100,
            conta_origem=self.conta_origem,
            conta_destino=self.conta_destino
        )

    def test_transacao_criada_com_sucesso(self):
        self.assertEqual(Transacao.objects.count(), 1)

    def test_valor_transacao(self):
        self.assertEqual(self.transacao.valor, 100)

    def test_status_padrao_concluida(self):
        self.assertEqual(self.transacao.status, 'concluida')

    def test_descricao_padrao(self):
        self.assertEqual(self.transacao.descricao, "Transferência realizada")

    def test_relacionamento_conta_origem(self):
        self.assertEqual(self.transacao.conta_origem, self.conta_origem)

    def test_relacionamento_conta_destino(self):
        self.assertEqual(self.transacao.conta_destino, self.conta_destino)

    def test_data_hora_gerada(self):
        self.assertIsNotNone(self.transacao.data_hora)

    def test_str_transacao(self):
        texto = str(self.transacao)
        self.assertIn("11111111", texto)
        self.assertIn("22222222", texto)
        self.assertIn("100", texto)
