from django.test import TestCase, Client
from users.models import User
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user
from django.contrib.messages import get_messages
from common.forms import UserForm


class LogInOutTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        hashed_password = make_password('asdf1234')
        user1 = User.objects.create(userid='bruce1115', email='bruce1115@naver.com',
                                    password=hashed_password, nickname='BRUCE')

    def setUp(self):
        client = Client()

    def test_login_idWrong(self):  # 올바른 kw 값이 잘 적용 되었는지 확인한다.
        response = self.client.post(reverse('common:login'), {'userid': 'bru1115', 'password': 'asdf1234'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '아이디 혹은 비밀번호가 틀렸습니다.')
        self.assertTemplateUsed(response, 'common/login.html')

    def test_login_pwLong(self):
        response = self.client.post(reverse('common:login'), {'userid': 'bruce1115', 'password': 'asdf124'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '아이디 혹은 비밀번호가 틀렸습니다.')
        self.assertTemplateUsed(response, 'common/login.html')

    def test_login_right(self):
        response = self.client.post(reverse('common:login'), {'userid': 'bruce1115', 'password': 'asdf1234'})
        self.assertEqual(int(self.client.session['_auth_user_id']), 1)
        self.assertRedirects(response, reverse("board:index"), status_code=302)

    def test_already_login(self):
        self.client.login(userid='bruce1115', password='asdf1234')
        response = self.client.get(reverse("common:login"))
        self.assertRedirects(response, reverse("board:index"), status_code=302)

    def test_redirect_login(self):
        response = self.client.get(reverse("common:login"))
        self.assertTemplateUsed(response, 'common/login.html')

    def test_logout(self):
        self.client.login(userid='bruce1115', password='asdf1234')
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        response = self.client.get(reverse("common:logout"))
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)


class SignUpTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        hashed_password = make_password('asdf1234')
        user1 = User.objects.create(userid='bruce1115', email='bruce1115@naver.com',
                                    password=hashed_password, nickname='BRUCE')

    def setUp(self):
        client = Client()

    def test_signUpForm(self):
        form = UserForm(data={"userid": "kbs1115", "nickname": "KBS",
                              "password1": "bb1122cc", "password2": "bb1122cc",
                              "email": "bruce11158@gmail.com"})
        self.assertTrue(form.is_valid())

        form = UserForm(data={"userid": "kbs1115", "nickname": "KBS",
                              "password1": "bb1122cc", "password2": "bb122cc",
                              "email": "bruce11158@gmail.com"})
        self.assertFalse(form.is_valid())

        form = UserForm(data={"userid": "kbs1115", "nickname": "KBS",
                              "password1": "bb1122cc", "password2": "bb1122cc",
                              "email": "bruce11158gmail.com"})
        self.assertFalse(form.is_valid())

        form = UserForm(data={"userid": "kbs11111111111111111111111115", "nickname": "KBS",
                              "password1": "bb1122cc", "password2": "bb1122cc",
                              "email": "bruce11158@gmail.com"})
        self.assertFalse(form.is_valid())

    def test_signUpRight(self):
        response = self.client.post(reverse("common:signup"), {"userid": "kbs1115", "nickname": "KBS",
                                                               "password1": "bb1122cc", "password2": "bb1122cc",
                                                               "email": "bruce11158@gmail.com"})
        user = User.objects.get(userid="kbs1115")
        self.assertEqual(user.userid, "kbs1115")
        self.assertEqual(user.nickname, "KBS")
        self.assertEqual(user.email, "bruce11158@gmail.com")
        self.assertTrue(user.check_password("bb1122cc"))

        self.assertRedirects(response, reverse("board:index"), status_code=302)

        response = self.client.post(reverse("common:signup"), {"userid": "kbs1115", "nickname": "KBS",
                                                               "password1": "bb11122cc", "password2": "bb1122cc",
                                                               "email": "bruce11158@gmail.com"})
        self.assertTemplateUsed(response, 'common/signup.html') # 만약 로그인이 안 되는 조건인 경우에는 다시 signup으로 render

    def test_signUpGet(self):
        response = self.client.get(reverse("common:signup"))
        self.assertTemplateUsed(response, 'common/signup.html')
