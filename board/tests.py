from django.test import TestCase, Client
from django.urls import reverse
from .models import Post
from users.models import User
from django.utils import timezone

class NavSearchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(userid='bruce1115', email='bruce1115@naver.com', nickname='BRUCE')
        User.objects.create(userid='admin', email='bruce11158@gmail.com', nickname='KBS')
        for i in range(200):
            p = Post(subject='free_board %03d' % i, content='free data',
                     create_date=timezone.now(), user_id=1, category='free_board')
            p.save()

    def setUp(self):
        client = Client()

    def test_noRightData(self):  # 올바른 검색 데이터가 없는 경우 list 안에 데이터가 없어야 한다.
        Post.objects.create(subject='yahoo', content='1111 data', create_date=timezone.now(),
                            user_id=1, category='free_board')
        response = self.client.get(reverse('board:search'), {'kw': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['free_list']), 0)
        self.assertEqual(len(response.context['data_list']), 0)
        self.assertEqual(len(response.context['question_list']), 0)
