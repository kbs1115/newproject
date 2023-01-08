from django.shortcuts import resolve_url
from django.test import TestCase, Client
from django.urls import reverse
from .models import Post, Comment
from users.models import User
from django.utils import timezone
import time


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
    @classmethod
    def setUpTestData(cls):
        User.objects.create(userid='bruce1115', email='bruce1115@naver.com', nickname='BRUCE')  # id=1
        User.objects.create(userid='admin', email='bruce11158@gmail.com', nickname='KBS')  # id=2
        User.objects.create(userid='dbsrbals', email='dbsrbals26@gmail.com', nickname='ygm')  # id=3
        User.objects.create(userid='dbsrbals1', email='dbsrbals27@gmail.com', nickname='ygm1')  # id=4

        for i in range(40):
            p = Post(subject='notice_board %03d' % i, content='notice data',
                     create_date=timezone.now(), user_id=1, category='40')
            p.save()

        for i in range(10):
            p = Post(subject='question_list %03d' % i, content='question_list',
                     create_date=timezone.now(), user_id=2, category='10')
            p.save()

        for i in range(11):
            p = Post(subject='question_korean_board %03d' % i, content='question_korean_data',
                     create_date=timezone.now(), user_id=2, category='11')
            p.save()

        for i in range(12):
            p = Post(subject='question_math_board %03d' % i, content='question_math_data',
                     create_date=timezone.now(), user_id=2, category='12')
            p.save()

        for i in range(13):
            p = Post(subject='question_english_board %03d' % i, content='question_english_data',
                     create_date=timezone.now(), user_id=2, category='13')
            p.save()

        for i in range(14):
            p = Post(subject='question_etc_board %03d' % i, content='question_etc_data',
                     create_date=timezone.now(), user_id=2, category='14')
            p.save()

        for i in range(20):
            p = Post(subject='free_board %03d' % i, content='free data',
                     create_date=timezone.now(), user_id=1, category='20')
            p.save()

        for i in range(30):
            p = Post(subject='data_list %03d' % i, content='data_list',
                     create_date=timezone.now(), user_id=1, category='30')
            p.save()

        for i in range(31):
            p = Post(subject='data_list_ko %03d' % i, content='data_list_ko',
                     create_date=timezone.now(), user_id=1, category='31')
            p.save()

        for i in range(32):
            p = Post(subject='data_list_ma %03d' % i, content='data_list_ma',
                     create_date=timezone.now(), user_id=1, category='32')
            p.save()

        for i in range(33):
            p = Post(subject='data_list_eg %03d' % i, content='data_list_eg',
                     create_date=timezone.now(), user_id=1, category='33')
            p.save()

        for i in range(34):
            p = Post(subject='data_list_etc %03d' % i, content='data_list_etc',
                     create_date=timezone.now(), user_id=1, category='34')
            p.save()

    def setUp(self) -> None:
        client = Client()

    def test_checkBoardCategory(self):  # category에 맞게 들어갔는지 확인
        category_list = [10, 11, 12, 13, 14, 20, 30, 31, 32, 33, 34, 40]
        for i in category_list:
            response = self.client.get(reverse("board:posts", args=[i]))
            category = response.context['category']
            self.assertEqual(category, i)

    def test_checkBoardCount(self):  # 카테고리에 맞는 post 객체들의 개수를 조사한다
        category_list = [10, 11, 12, 13, 14, 20, 30, 31, 32, 33, 34, 40]
        post_count = [60, 11, 12, 13, 14, 20, 160, 31, 32, 33, 34, 40]
        for i in range(len(category_list)):
            response = self.client.get(reverse("board:posts", args=[category_list[i]]))
            post_cnt = len(response.context['post'])
            self.assertEqual(post_cnt, post_count[i])

    def test_checkDetail(self):  # all , subject ,content, user, subAndContent
        detail_list = ['', 'all', 'subject', 'content', 'user', 'subAndContent']
        input_list = ['', 'all', 'subject', 'content', 'user', 'subAndContent']
        for i in range(len(input_list)):
            response = self.client.get(reverse("board:posts", args=[40]),
                                       {'detail': f'{input_list[i]}', 'kw': '', 'sort': '', 'page': '1'},
                                       )
            detail = response.context['detail']
            self.assertEqual(detail, detail_list[i])

    def test_checkKwCount(self):
        detail_list = ['all', 'subject', 'content', 'user', 'subAndContent']
        kw_list = ['1', 'ma', 'data']
        post_cnt_list = [15, 15, 0, 0, 15, 12, 12, 12, 0, 12, 50, 0, 50, 0, 50]
        k = 0
        for i in range(len(kw_list)):
            for j in range(len(detail_list)):
                response = self.client.get(reverse("board:posts", args=[10]),
                                           {'detail': f'{detail_list[j]}', 'kw': f'{kw_list[i]}', 'sort': '',
                                            'page': '1'},
                                           )
                post_cnt = len(response.context['post'])
                self.assertEqual(post_cnt, post_cnt_list[k])
                k += 1

    def test_pagingDataCount(self):
        response = self.client.get(reverse("board:posts", args=[10]),
                                   {'kw': '',
                                    'page': '2'},
                                   )
        page_cnt = len(response.context['page_obj'])
        self.assertEqual(page_cnt, 30)

        response = self.client.get(reverse("board:posts", args=[10]),
                                   {'kw': '!@#!@#QESE!@#',
                                    'page': ''},
                                   )
        post_cnt = len(response.context['post'])
        self.assertEqual(post_cnt, 0)

    def test_checkSort_voter(self):

        p2 = Post.objects.create(subject='4', content='no data', create_date=timezone.now(),
                                 user_id=1, category='32')
        p1 = Post.objects.create(subject='1', content='no data', create_date=timezone.now(),
                                 user_id=4, category='31')
        p4 = Post.objects.create(subject='3', content='no data', create_date=timezone.now(),
                                 user_id=3, category='34')
        p3 = Post.objects.create(subject='2', content='no data', create_date=timezone.now(),
                                 user_id=2, category='33')
        p1.voter.add(1, 2, 3)
        p2.voter.add(2, 3)
        p3.voter.add(1)
        p4.voter.add()

        response = self.client.get(reverse("board:posts", args=[30]),
                                   {'detail': 'content', 'kw': 'no data', 'sort': 'voter_count',
                                    'page': ''},
                                   )
        context = response.context['post']
        self.assertEqual(context[0].subject, '1')
        self.assertEqual(context[1].subject, '4')
        self.assertEqual(context[2].subject, '2')
        self.assertEqual(context[3].subject, '3')

    def test_checkSort_createdate(self):
        Post.objects.create(subject='10', content='no data', create_date=timezone.now(),
                            user_id=4, category='31')
        time.sleep(0.01)
        Post.objects.create(subject='20', content='no data', create_date=timezone.now(),
                            user_id=1, category='32')
        time.sleep(0.01)
        Post.objects.create(subject='30', content='no data', create_date=timezone.now(),
                            user_id=2, category='33')
        time.sleep(0.01)
        Post.objects.create(subject='40', content='no data', create_date=timezone.now(),
                            user_id=3, category='34')
        time.sleep(0.01)
        response = self.client.get(reverse("board:posts", args=[30]),
                                   {'detail': 'content', 'kw': 'no data', 'sort': 'update',
                                    'page': ''},
                                   )
        context = response.context['post']
        post_cnt = len(response.context['post'])
        self.assertEqual(post_cnt, 4)
        self.assertEqual(context[0].subject, '40')
        self.assertEqual(context[1].subject, '30')
        self.assertEqual(context[2].subject, '20')
        self.assertEqual(context[3].subject, '10')
