from django.test import TestCase
from users.models import User
from django.utils import timezone
import datetime


class UserModelTest(TestCase):
    def test_userCreate(self):# 일반 user model이 잘 의도한 대로 만들어졌는지 테스트한다.
        user = User.objects.create_user(userid='kbs1115', nickname='byeongsu', email='absoluteqed@gmail.com'
                                        , password='1234')
        user.save()
        time_after_create = timezone.now()
        self.assertEqual(user.userid, 'kbs1115')
        self.assertEqual(user.nickname, 'byeongsu')
        self.assertEqual(user.email, 'absoluteqed@gmail.com')
        self.assertTrue(user.check_password('1234'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertGreater(datetime.timedelta(seconds=1), time_after_create - user.date_joined)

    def test_superuserCreate(self):# superuser model이 잘 의도한 대로 만들어졌는지 테스트한다.
        user = User.objects.create_superuser(userid='kbs1115', nickname='byeongsu', email='absoluteqed@gmail.com'
                                        , password='1234')
        user.save()
        time_after_create = timezone.now()
        self.assertEqual(user.userid, 'kbs1115')
        self.assertEqual(user.nickname, 'byeongsu')
        self.assertEqual(user.email, 'absoluteqed@gmail.com')
        self.assertTrue(user.check_password('1234'))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertGreater(datetime.timedelta(seconds=1), time_after_create - user.date_joined)

    def test_userUpdate(self):# 일반 user model이 잘 의도한 대로 업데이트되었는지 테스트한다.
        user = User.objects.create_user(userid='kbs1115', nickname='byeongsu', email='absoluteqed@gmail.com'
                                        , password='1234')
        user.save()
        time_after_create = timezone.now()
        self.assertEqual(user.userid, 'kbs1115')
        self.assertEqual(user.nickname, 'byeongsu')
        self.assertEqual(user.email, 'absoluteqed@gmail.com')
        self.assertTrue(user.check_password('1234'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertGreater(datetime.timedelta(seconds=1), time_after_create - user.date_joined)

        user.userid = 'kbskbs'
        user.nickname = 'KBS'
        user.email = 'aaaa@naver.com'
        user.set_password('123456')
        user.is_staff = True

        self.assertEqual(user.userid, 'kbskbs')
        self.assertEqual(user.nickname, 'KBS')
        self.assertEqual(user.email, 'aaaa@naver.com')
        self.assertTrue(user.check_password('123456'))
        self.assertTrue(user.is_staff)

    def test_userDelete(self):  # 일반 user model이 잘 의도한 대로 만들어졌는지 테스트한다.
        user1 = User.objects.create_user(userid='kbs1115', nickname='byeongsu', email='absoluteqed@gmail.com',
                                         password='1234')
        user2 = User.objects.create_user(userid='kbs111115', nickname='byeongsu2', email='absoluteqed22@gmail.com',
                                         password='123456')
        user1.delete()
        self.assertFalse(User.objects.filter(userid='kbs1115').exists())
        self.assertTrue(User.objects.filter(nickname='byeongsu2').exists())
