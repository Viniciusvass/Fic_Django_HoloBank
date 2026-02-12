from django.test import TestCase
from apps.usuarios.forms import UsuarioForm, LoginForm
from apps.usuarios.models import Usuario
from django.db.utils import IntegrityError
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth.hashers import make_password
from apps.contas.models import Conta

# FORMS
class UsuarioFormTest(TestCase):

    def test_usuario_form_valido(self):
        form = UsuarioForm(data={
            'nome': 'Vinicius Santos',
            'cpf': '12345678900',
            'email': 'vinicius@email.com',
            'telefone': '81999999999',
            'senha': '123456',
            'tipo_conta': 'corrente'
        })

        self.assertTrue(form.is_valid())

    def test_usuario_form_sem_nome(self):
        form = UsuarioForm(data={
            'cpf': '12345678900',
            'email': 'vinicius@email.com',
            'telefone': '81999999999',
            'senha': '123456',
            'tipo_conta': 'corrente'
        })

        self.assertFalse(form.is_valid())

    def test_usuario_form_sem_cpf(self):
        form = UsuarioForm(data={
            'nome': 'Vinicius',
            'email': 'vinicius@email.com',
            'telefone': '81999999999',
            'senha': '123456',
            'tipo_conta': 'corrente'
        })

        self.assertFalse(form.is_valid())

    def test_usuario_form_email_invalido(self):
        form = UsuarioForm(data={
            'nome': 'Vinicius',
            'cpf': '12345678900',
            'email': 'emailinvalido',
            'telefone': '81999999999',
            'senha': '123456',
            'tipo_conta': 'corrente'
        })

        self.assertFalse(form.is_valid())

    def test_usuario_form_sem_senha(self):
        form = UsuarioForm(data={
            'nome': 'Vinicius',
            'cpf': '12345678900',
            'email': 'vinicius@email.com',
            'telefone': '81999999999',
            'tipo_conta': 'corrente'
        })

        self.assertFalse(form.is_valid())


class LoginFormTest(TestCase):

    def test_login_form_valido(self):
        form = LoginForm(data={
            'email': 'vinicius@email.com',
            'senha': '123456'
        })

        self.assertTrue(form.is_valid())

    def test_login_form_sem_email(self):
        form = LoginForm(data={
            'senha': '123456'
        })

        self.assertFalse(form.is_valid())

    def test_login_form_sem_senha(self):
        form = LoginForm(data={
            'email': 'vinicius@email.com'
        })

        self.assertFalse(form.is_valid())

    def test_login_form_email_invalido(self):
        form = LoginForm(data={
            'email': 'emailerrado',
            'senha': '123456'
        })

        self.assertFalse(form.is_valid())

# MODEL
class UsuarioModelTest(TestCase):

    def test_criar_usuario_comum(self):
        usuario = Usuario.objects.create(
            nome="Vinicius Santos",
            cpf="12345678900",
            email="vinicius@email.com",
            telefone="81999999999",
            senha="123456"
        )

        self.assertEqual(usuario.nome, "Vinicius Santos")
        self.assertFalse(usuario.isAdm)

    def test_criar_usuario_administrador(self):
        adm = Usuario.objects.create(
            nome="Gerente João",
            cpf="99999999999",
            email="gerente@email.com",
            telefone="81888888888",
            senha="admin123",
            isAdm=True
        )

        self.assertTrue(adm.isAdm)

    def test_cpf_unico(self):
        Usuario.objects.create(
            nome="User 1",
            cpf="11111111111",
            email="user1@email.com",
            telefone="111111111",
            senha="123"
        )

        with self.assertRaises(IntegrityError):
            Usuario.objects.create(
                nome="User 2",
                cpf="11111111111",
                email="user2@email.com",
                telefone="222222222",
                senha="456"
            )

    def test_email_unico(self):
        Usuario.objects.create(
            nome="User 1",
            cpf="22222222222",
            email="teste@email.com",
            telefone="111111111",
            senha="123"
        )

        with self.assertRaises(IntegrityError):
            Usuario.objects.create(
                nome="User 2",
                cpf="33333333333",
                email="teste@email.com",
                telefone="222222222",
                senha="456"
            )

    def test_usuario_com_gerente(self):
        gerente = Usuario.objects.create(
            nome="Gerente",
            cpf="99999999991",
            email="gerente@email.com",
            telefone="888888888",
            senha="admin",
            isAdm=True
        )

        cliente = Usuario.objects.create(
            nome="Cliente",
            cpf="44444444444",
            email="cliente@email.com",
            telefone="777777777",
            senha="123",
            gerente_responsavel=gerente
        )

        self.assertEqual(cliente.gerente_responsavel, gerente)
        self.assertIn(cliente, gerente.clientes_gerenciados.all())

# VIEWS
class CadastroViewTest(TestCase):

    def test_cadastro_usuario_cria_usuario_e_conta(self):
        response = self.client.post(reverse('cadastro'), {
            'nome': 'Vinicius',
            'cpf': '12345678901',
            'email': 'vinicius@email.com',
            'telefone': '81999999999',
            'senha': '123456',
            'tipo_conta': 'corrente'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(Conta.objects.count(), 1)

    def test_cadastro_form_invalido_nao_cria_usuario(self):
        response = self.client.post(reverse('cadastro'), {
            'nome': '',
            'cpf': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)


class LoginViewTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome='Vinicius',
            cpf='99999999999',
            email='vinicius@email.com',
            telefone='81999999999',
            senha=make_password('123456'),
            isAdm=False
        )

    def test_login_sucesso(self):
        response = self.client.post(reverse('login'), {
            'email': 'vinicius@email.com',
            'senha': '123456'
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn("usuario_id", self.client.session)

    def test_login_senha_errada(self):
        response = self.client.post(reverse('login'), {
            'email': 'vinicius@email.com',
            'senha': 'errada'
        })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Senha incorreta.")

    def test_login_usuario_inexistente(self):
        response = self.client.post(reverse('login'), {
            'email': 'naoexiste@email.com',
            'senha': '123456'
        })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Usuário não encontrado.")


class LogoutViewTest(TestCase):

    def test_logout_remove_sessao(self):
        session = self.client.session
        session["usuario_id"] = 1
        session.save()

        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("usuario_id", self.client.session)
