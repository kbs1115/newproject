from django.test import TestCase, Client
from django.urls import reverse
from .models import Post, Comment
from users.models import User
from django.utils import timezone


class NavSearchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(userid='bruce1115', email='bruce1115@naver.com', nickname='BRUCE')
        User.objects.create(userid='admin', email='bruce11158@gmail.com', nickname='KBS')
        Post.objects.create(subject='yahoo', content='1111 cccc', create_date=timezone.now(),
                            user_id=2, category='20')
        for i in range(200):
            p = Post(subject='free_board %03d' % i, content='free data',
                     create_date=timezone.now(), user_id=1, category='20')
            p.save()

    def setUp(self):
        client = Client()

    def test_rightKw(self):  # 올바른 kw 값이 잘 적용되었는지 확인한다.
        response = self.client.get(reverse('board:search'), {'kw': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['kw'], 'test')

    def test_voterCountAlign(self):  # 게시글이 voter 수대로 정렬이 잘 되는지 확인하기
        p1 = Post.objects.create(subject='Best', content='no data', create_date=timezone.now(),
                                 user_id=1, category='20')
        p2 = Post.objects.create(subject='Second', content='no data', create_date=timezone.now(),
                                 user_id=2, category='20')
        p1.voter.add(1, 2)
        p2.voter.add(1)  # 새롭게 만든 Post 객체에 voter를 각각 둘, 하나 추가한다. 이 둘이 순서대로 상단에 노출될 것이다.
        response = self.client.get(reverse('board:search'), {'kw': 'data'})
        context = response.context['free_list']
        self.assertEqual(context[0].subject, 'Best')  # 첫 번째 Post가 Best인지 확인
        self.assertEqual(context[1].subject, 'Second')  # 두 번째 Post가 Second인지 확인

    def test_fiveOverPosts(self):  # 5개 이상이 검색되는 경우 5개까지만 검색되어야 한다.
        response = self.client.get(reverse('board:search'), {'kw': 'free'})
        self.assertEqual(len(response.context['free_list']), 5)
        self.assertEqual(len(response.context['data_list']), 0)
        self.assertEqual(len(response.context['question_list']), 0)

    def test_noRightData(self):  # 올바른 검색 데이터가 없는 경우 list 안에 데이터가 없어야 한다.
        response = self.client.get(reverse('board:search'), {'kw': 'test'})
        self.assertEqual(len(response.context['free_list']), 0)
        self.assertEqual(len(response.context['data_list']), 0)
        self.assertEqual(len(response.context['question_list']), 0)

    def test_subjectData(self):  # subject 통해 검색했으므로 free_list 에만 원소 한 개가 있어야 한다.
        response = self.client.get(reverse('board:search'), {'kw': 'yahoo'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['free_list']), 1)
        self.assertEqual(len(response.context['data_list']), 0)
        self.assertEqual(len(response.context['question_list']), 0)

    def test_contentData(self):  # 올바른 검색 데이터가 없는 경우 list 안에 데이터가 없어야 한다.
        response = self.client.get(reverse('board:search'), {'kw': 'cccc'})
        self.assertEqual(len(response.context['free_list']), 1)
        self.assertEqual(len(response.context['data_list']), 0)
        self.assertEqual(len(response.context['question_list']), 0)

    def test_nicknameData(self):  # nickname KBS로 검색하는 test code
        response = self.client.get(reverse('board:search'), {'kw': 'KBS'})
        self.assertEqual(len(response.context['free_list']), 1)
        self.assertEqual(len(response.context['data_list']), 0)
        self.assertEqual(len(response.context['question_list']), 0)

    def test_commentContentData(self):  # comment의 content 바탕으로 user를 검색한다.
        Comment.objects.create(content='Commenttt', post_id=10, user_id=1, create_date=timezone.now())
        response = self.client.get(reverse('board:search'), {'kw': 'Commenttt'})
        self.assertEqual(len(response.context['free_list']), 1)
        self.assertEqual(len(response.context['data_list']), 0)
        self.assertEqual(len(response.context['question_list']), 0)

    def test_commentUserData(self):  # nickname KBS로 검색하는 test code
        Comment.objects.create(content='Commenttt', post_id=10, user_id=2, create_date=timezone.now())
        response = self.client.get(reverse('board:search'), {'kw': 'KBS'})
        self.assertEqual(len(response.context['free_list']), 2)
        self.assertEqual(len(response.context['data_list']), 0)
        self.assertEqual(len(response.context['question_list']), 0)


class BoardModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(userid='bruce1115', email='bruce1115@naver.com', nickname='BRUCE')
        User.objects.create(userid='admin', email='bruce11158@gmail.com', nickname='KBS')
        Post.objects.create(subject='subject 1', content='data 1', create_date=timezone.now(),
                            user_id=1, category='20')
        Post.objects.create(subject='subject 22', content='data 22', create_date=timezone.now(),
                            user_id=1, category='20')

    def test_postCreate(self):
        p = Post.objects.create(subject='subject 2', content='data 2', create_date=timezone.now(),
                                user_id=1, category='10')
        self.assertEqual(p.subject, 'subject 2')
        self.assertEqual(p.content, 'data 2')
        self.assertEqual(p.user_id, 1)
        self.assertEqual(p.category, '10')

    def test_commentCreate(self):
        c = Comment.objects.create(content='data 2', create_date=timezone.now(), user_id=1, post_id=1)
        self.assertEqual(c.content, 'data 2')
        self.assertEqual(c.user_id, 1)
        self.assertEqual(c.post_id, 1)

    def test_postModify(self):
        p = Post.objects.create(subject='subject 2', content='data 2', create_date=timezone.now(),
                                user_id=1, category='10')
        self.assertEqual(p.subject, 'subject 2')
        self.assertEqual(p.content, 'data 2')
        self.assertEqual(p.user_id, 1)
        self.assertEqual(p.category, '10')

        p.subject = 'aaa'
        p.content = 'aa'
        p.user_id = 2
        p.category = '30'

        self.assertEqual(p.subject, 'aaa')
        self.assertEqual(p.content, 'aa')
        self.assertEqual(p.user_id, 2)
        self.assertEqual(p.category, '30')

    def test_commentModify(self):
        c = Comment.objects.create(content='data 2', create_date=timezone.now(), user_id=1, post_id=1)
        self.assertEqual(c.content, 'data 2')
        self.assertEqual(c.user_id, 1)
        self.assertEqual(c.post_id, 1)

        c.content = 'aaa'
        c.user_id = 2
        c.post_id = 2

        self.assertEqual(c.content, 'aaa')
        self.assertEqual(c.user_id, 2)
        self.assertEqual(c.post_id, 2)

    def test_postDelete(self):
        Post.objects.filter(id=1).delete()
        self.assertFalse(Post.objects.filter(id=1).exists())
        self.assertTrue(Post.objects.filter(id=2).exists())

    def test_commentDelete(self):
        c1 = Comment.objects.create(content='data 2', create_date=timezone.now(), user_id=1, post_id=1)
        c2 = Comment.objects.create(content='data 3', create_date=timezone.now(), user_id=1, post_id=2)
        c1.delete()
        self.assertFalse(Comment.objects.filter(post_id=1).exists())
        self.assertTrue(Comment.objects.filter(content='data 3').exists())


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(userid='bruce1115', email='bruce1115@naver.com', nickname='BRUCE')  # id=1
        User.objects.create(userid='admin', email='bruce11158@gmail.com', nickname='KBS')  # id=2
        User.objects.create(userid='dbsrbals', email='dbsrbals26@gmail.com', nickname='ygm')  # id=3
        User.objects.create(userid='dbsrbals1', email='dbsrbals27@gmail.com', nickname='ygm1')  # id=4

        for i in range(100):
            p = Post(subject='notice_board %03d' % i, content='notice data',
                     create_date=timezone.now(), user_id=1, category='40')
            p.save()

        for i in range(100):
            p = Post(subject='question_korean_board %03d' % i, content='question_korean_data',
                     create_date=timezone.now(), user_id=2, category='11')
            p.save()

        for i in range(100):
            p = Post(subject='question_math_board %03d' % i, content='question_math_data',
                     create_date=timezone.now(), user_id=2, category='12')
            p.save()

        for i in range(100):
            p = Post(subject='question_english_board %03d' % i, content='question_english_data',
                     create_date=timezone.now(), user_id=2, category='13')
            p.save()

        for i in range(100):
            p = Post(subject='question_etc_board %03d' % i, content='question_etc_data',
                     create_date=timezone.now(), user_id=2, category='14')
            p.save()

        for i in range(100):
            p = Post(subject='free_board %03d' % i, content='free data',
                     create_date=timezone.now(), user_id=1, category='20')
            p.save()

    def setUp(self):
        client = Client()

    def test_voterCountAlign(self):
        p1 = Post.objects.create(subject='1', content='no data', create_date=timezone.now(),
                                 user_id=4, category='20')
        p2 = Post.objects.create(subject='cannot in best voter', content='no data', create_date=timezone.now(),
                                 user_id=1, category='40')
        p3 = Post.objects.create(subject='2', content='no data', create_date=timezone.now(),
                                 user_id=2, category='11')
        p4 = Post.objects.create(subject='3', content='no data', create_date=timezone.now(),
                                 user_id=3, category='12')
        p1.voter.add(1, 2, 3)
        p2.voter.add(2, 3, 4)
        p3.voter.add(1, 4)
        p4.voter.add(1)

        response = self.client.get(reverse('board:index'))
        context = response.context['best_voter']
        self.assertEqual(context[0].subject, '1')
        self.assertEqual(context[1].subject, '2')
        self.assertEqual(context[2].subject, '3')

    def test_checkPostCount(self):
        response = self.client.get(reverse("board:index"))
        notice = len(response.context['notice_board'])
        question_korean = len(response.context['question_korean'])
        question_math = len(response.context['question_math'])
        question_english = len(response.context['question_english'])
        question_etc = len(response.context['question_etc'])
        free_board = len(response.context['free_board'])
        best_voter = len(response.context['best_voter'])

        self.assertEqual(notice, 10)
        self.assertEqual(question_korean, 5)
        self.assertEqual(question_math, 5)
        self.assertEqual(question_english, 5)
        self.assertEqual(question_etc, 5)
        self.assertEqual(free_board, 10)
        self.assertEqual(best_voter, 10)

class PostViewTest(TestCase):
