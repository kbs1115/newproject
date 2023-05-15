from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client

from common.models import Notification
from users.models import User
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user
from django.contrib.messages import get_messages
from common.forms import UserForm
from board.models import Post, Comment
from django.utils import timezone
import time


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
        self.assertTemplateUsed(response, 'common/signup.html')  # 만약 로그인이 안 되는 조건인 경우에는 다시 signup으로 render

    def test_signUpGet(self):
        response = self.client.get(reverse("common:signup"))
        self.assertTemplateUsed(response, 'common/signup.html')


class MyPageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        hashed_password = make_password('as1df1235')
        user1 = User.objects.create(userid='bruce1115', email='bruce1115@naver.com',
                                    password=hashed_password, nickname='BRUCE')
        for i in range(1, 21):
            p = Post(subject='free_board %03d' % i, content='free data',
                     create_date=timezone.now(), user_id=1, category='20')
            p.save()
            time.sleep(0.01)

        for i in range(1, 21):
            c = Comment.objects.create(content='Commenttt %02d' % i, post_id=i, user_id=1, create_date=timezone.now())
            c.save()
            time.sleep(0.01)

    def setUp(self):
        client = Client()

    def test_userData(self):
        self.client.login(userid="bruce1115", password='as1df1235')
        response = self.client.get(reverse("common:mypage"))
        user = get_user(self.client)
        self.assertEqual(user.userid, "bruce1115")
        self.assertEqual(user.nickname, "BRUCE")
        self.assertEqual(user.email, "bruce1115@naver.com")
        post_list = response.context['post_list']
        comment_list = response.context['comment_list']
        self.assertEqual(post_list[0].subject, 'free_board 020')
        self.assertEqual(len(post_list), 5)
        self.assertEqual(comment_list[0].content, 'Commenttt 20')
        self.assertEqual(len(comment_list), 5)


class UpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        hashed_password = make_password('as1df1234')
        user1 = User.objects.create(userid='bruce1115', email='bruce1115@naver.com',
                                    password=hashed_password, nickname='BRUCE')
        user2 = User.objects.create(userid='kbs1115', email='bruce11158@gmail.com',
                                    password=hashed_password, nickname='KBS')

    def setUp(self):
        client = Client()

    def test_modifyUser(self):
        self.client.login(userid="kbs1115", password="as1df1234")
        response = self.client.post(reverse("common:update"), {"nickname": "KKBBSS", "email": "absoluteqed@gmail.com"})
        user = User.objects.get(userid="kbs1115")
        self.assertEqual(user.nickname, "KKBBSS")
        self.assertEqual(user.email, "absoluteqed@gmail.com")
        self.assertRedirects(response, reverse("common:mypage"), status_code=302)

    def test_modifyError(self):
        self.client.login(userid="bruce1115", password="as1df1234")
        response = self.client.post(reverse("common:update"),
                                    {"nickname": "KKBBSS", "email": "bruce11158@gmail.com"})  # email 중복
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), '유효하지 않은 입력입니다.')
        form = response.context['form']
        self.assertEqual(form["nickname"].value(), "BRUCE")
        self.assertEqual(form["email"].value(), "bruce1115@naver.com")
        self.assertTemplateUsed(response, "common/modify.html")

    def test_getMethod(self):
        self.client.login(userid="bruce1115", password="as1df1234")
        response = self.client.get(reverse("common:update"))
        form = response.context['form']
        self.assertEqual(form["nickname"].value(), "BRUCE")
        self.assertEqual(form["email"].value(), "bruce1115@naver.com")
        self.assertTemplateUsed(response, "common/modify.html")


class NotificationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        hashed_password = make_password('as1df1234')
        User.objects.create(userid='aa', email='bruce1115@naver.com',
                            password=hashed_password, nickname='BRUCE')
        User.objects.create(userid='bb', email='bruce11158@gmail.com',
                            password=hashed_password, nickname='KBS')
        User.objects.create(userid='cc', email='bruce11q158@gmail.com',
                            password=hashed_password, nickname='yun')
        Post.objects.create(subject='yahoo', content='1111 cccc', create_date=timezone.now(),
                            user_id=1, category='20')

    def setUp(self):
        client = Client()

    def test_Is_data_in_notificationModel_if_post_vote(self):
        self.client.login(userid="bb", password="as1df1234")
        notice_count = Notification.objects.count()
        self.assertEqual(notice_count, 0)
        response = self.client.get(reverse('board:post_vote', args=[1]))
        user_bb = response.wsgi_request.user
        post = Post.objects.get(pk=1)
        notice = Notification.objects.get(pk=1)
        self.assertEqual(post.voter.all().count(), 1)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notice.received_user, post.user)
        self.assertEqual(notice.data.post, post)
        self.assertEqual(notice.data.sent_user, user_bb)
        self.assertEqual(notice.data.notice_type, "vote_of_post")

    def test_Is_data_in_notificationModel_if_comment_vote(self):
        self.client.login(userid="cc", password="as1df1234")
        notice_count = Notification.objects.count()
        self.assertEqual(notice_count, 0)
        Comment.objects.create(content='test data', user_id=2, post_id=1, create_date=timezone.now())
        self.client.get(reverse('board:comment_vote', args=[1]))
        notice = Notification.objects.get(received_user=2, data__sent_user=3, data__comment=1,
                                          data__notice_type='vote_of_comment')
        self.assertEqual(notice, Notification.objects.get(pk=1))

    def test_Is_data_in_notificationModel_if_comment_of_post(self):
        self.client.login(userid="bb", password="as1df1234")
        comment = Post.objects.get(pk=1).comment_set.all()
        self.assertEqual(comment.count(), 0)
        self.assertEqual(Notification.objects.all().count(), 0)
        self.client.post(reverse('board:comment_create', args=[1]),
                         {'content': 'test_content'})
        comment = Post.objects.get(pk=1).comment_set.all()
        self.assertEqual(comment.count(), 1)
        self.assertEqual(Notification.objects.all().count(), 1)

        notice = Notification.objects.get(pk=1)
        post = Post.objects.get(pk=1)
        comment = Comment.objects.get(pk=1)
        self.assertEqual(notice.received_user, post.user)
        self.assertEqual(notice.data.sent_user, comment.user)
        self.assertEqual(notice.data.comment, comment)
        self.assertEqual(notice.data.notice_type, "comment_of_post")

    def test_Is_data_in_notificationModel_if_reply_of_comment(self):
        self.client.login(userid="cc", password="as1df1234")
        Comment.objects.create(post_id=1, content="test_comment", create_date=timezone.now(), user_id=2)
        self.client.post(reverse("board:comment_create", args=[1, 1]),
                         {'content': "child_comment"})
        data = Notification.objects.get(data__sent_user=3, data__comment=2,
                                        data__notice_type='reply_of_comment')
        self.assertEqual(Notification.objects.get(pk=1), data)

    def test_Is_voteData_in_notificationModel_if_post_delete(self):
        self.client.login(userid="bb", password="as1df1234")
        self.assertEqual(Post.objects.all().count(), 1)
        self.client.get(reverse('board:post_vote', args=[1]))
        self.assertEqual(Notification.objects.count(), 1)
        self.client.logout()
        self.client.login(userid="aa", password="as1df1234")
        self.client.get(reverse('board:post_delete', args=[1]))
        self.assertEqual(Post.objects.all().count(), 0)
        self.assertEqual(Notification.objects.count(), 0)
