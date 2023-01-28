from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import resolve_url
from django.contrib.messages import get_messages
from django.contrib.auth.hashers import make_password
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from .forms import CommentForm
from .models import Post, Comment, Media
from users.models import User
from django.utils import timezone
from django.utils.datastructures import MultiValueDict
import time
from .forms import PostForm
from django.core.files.uploadedfile import SimpleUploadedFile


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
        self.assertEqual(response.templates[0].name, 'board/search_list.html')

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


class PostDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        hashed_password = make_password('as1df1234')
        user1 = User.objects.create(userid='bruce1115', email='bruce1115@naver.com',
                                    password=hashed_password, nickname='BRUCE')
        p1 = Post.objects.create(subject='1', content='no data', create_date=timezone.now(),
                                 user_id=1, category='31')

    def setUp(self):
        client = Client()

    def test_postDataRight(self):
        response = self.client.get(reverse('board:post_detail', args=[1]))
        post = response.context['post']
        self.assertEqual(post.user.userid, 'bruce1115')  # id가 일치하는지 검증(user 검증)
        self.assertEqual(post.subject, '1')
        self.assertEqual(post.content, 'no data')
        self.assertEqual(post.category, '31')


class CreatePostTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        hashed_password = make_password('as1df1234')
        user1 = User.objects.create(userid='bruce1115', email='bruce1115@naver.com',
                                    password=hashed_password, nickname='BRUCE')

    def setUp(self) -> None:
        client = Client()

    def test_formValid(self):
        image1 = SimpleUploadedFile(name='test_image1.jpg', content=b'111', content_type='image/jpeg')
        image2 = SimpleUploadedFile(name='test_image2.jpg', content=b'12', content_type='image/jpeg')

        form = PostForm(data={'content': '1111', 'subject': 'test', 'category': '20'},
                        files={'file_field': image1})  # image를 업로드한 경우
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['file_field'], image1)

        form = PostForm(data={'content': '1111', 'subject': 'test', 'category': '20'},
                        files={})  # image가 존재하지 않는 경우
        self.assertTrue(form.is_valid())

        form = PostForm(data={'content': '1111', 'subject': 'test', 'category': '20'},
                        files=MultiValueDict({'file_field': [image1, image2]}))  # image가 두개 이상 들어갈 때
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['file_field'], image2)

    def test_getAccess(self):
        response = self.client.get(reverse('board:post_create'))
        self.assertRedirects(response, reverse("common:login") + '?next=' + reverse("board:post_create"),
                             status_code=302)  # 로그인이 안 되었을 시 login page로 redirect. ?next=를 써야 함에 유의!
        self.client.login(userid='bruce1115', password='as1df1234')
        response = self.client.get(reverse('board:post_create'))
        self.assertTemplateUsed(response, 'board/create_post.html')  # 로그인이 되었을 시 의도했던 글 작성 템플릿 render

    def test_postAccessValid(self):
        image1 = SimpleUploadedFile(name='test_image1.jpg', content=b'111', content_type='image/jpeg')
        image2 = SimpleUploadedFile(name='test_image2.jpg', content=b'12', content_type='image/jpeg')

        self.client.login(userid='bruce1115', password='as1df1234')
        response = self.client.post(reverse('board:post_create'), {'subject': 'test dat', 'content': '111',
                                                                   'category': '20', 'file_field': image1})
        post = Post.objects.get(subject='test dat')  # Queryset으로 만든 게시글 가져 오기
        self.assertEqual(post.content, '111')
        self.assertEqual(post.user.id, 1)
        self.assertEqual(post.category, '20')
        m = post.media.all()
        self.assertEqual(len(m), 1)

        response = self.client.post(reverse('board:post_create'), {'subject': 'test dat2', 'content': '111',
                                                                   'category': '20'})
        post = Post.objects.get(subject='test dat2')  # 이미지가 없는 게시글 만들기
        self.assertEqual(post.content, '111')
        self.assertEqual(post.user.id, 1)
        self.assertEqual(post.category, '20')
        m = post.media.all()
        self.assertEqual(len(m), 0)

        response = self.client.post(reverse('board:post_create'), {'subject': 'test dat3', 'content': '111',
                                                                   'category': '20', 'file_field': [image1, image2]})
        post = Post.objects.get(subject='test dat3')  # 이미지가 두 개인 게시글 만들기.(multiple = True 처리)
        self.assertEqual(post.content, '111')
        self.assertEqual(post.user.id, 1)
        self.assertEqual(post.category, '20')
        m = post.media.all()
        self.assertEqual(len(m), 2)

        self.assertRedirects(response, reverse('board:post_detail', args=[post.id]))  # 작성한 글 상세 페이지로 이동하는지 체크

    def test_postAccessInValid(self):
        image1 = SimpleUploadedFile(name='test_image1.jpg', content=b'111', content_type='image/jpeg')

        self.client.login(userid='bruce1115', password='as1df1234')
        response = self.client.post(reverse('board:post_create'), {'subject': '', 'content': '111',
                                                                   'category': '20',
                                                                   'file_field': image1})  # invalid form 입력
        self.assertEqual(len(Post.objects.all()), 0)  # Post가 저장이 되지 않아야 한다.
        self.assertTemplateUsed(response, 'board/create_post.html')  # post 작성 템플릿으로 다시 이동


class ModifyPostTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        hashed_password = make_password('as1df1234')
        image1 = SimpleUploadedFile(name='test_modifyimage1.jpg', content=b'111', content_type='image/jpeg')
        user1 = User.objects.create(userid='bruce1115', email='bruce1115@naver.com',
                                    password=hashed_password, nickname='BRUCE')
        user2 = User.objects.create(userid='kbs1115', email='bruce11158@naver.com',
                                    password=hashed_password, nickname='BRUCE2')
        p = Post.objects.create(subject='test 1', content='no data', user_id=1, category='20'
                                , create_date=timezone.now())
        p.media.create(file=image1)

    def setUp(self) -> None:
        client = Client()

    def test_wrongLogin(self):
        response = self.client.get(reverse('board:post_modify', args=[1]))  # 로그인하지 않았을 때
        self.assertRedirects(response, reverse("common:login") + '?next=' + reverse("board:post_modify", args=[1]),
                             status_code=302)

        self.client.login(userid='kbs1115', password='as1df1234')  # 로그인한 사용자가 글 작성자와 다를 때
        response = self.client.get(reverse('board:post_modify', args=[1]))
        self.assertRedirects(response, reverse("board:post_detail", args=[1]), status_code=302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "게시글 수정 권한이 없습니다.")

    def test_getAccess(self):
        self.client.login(userid='bruce1115', password='as1df1234')  # 올바른 사용자의 로그인 후 접근
        response = self.client.get(reverse('board:post_modify', args=[1]))
        form = response.context['form']
        self.assertTemplateUsed(response, 'board/create_post.html')
        self.assertEqual(form['subject'].value(), 'test 1')
        self.assertEqual(form['content'].value(), 'no data')
        self.assertEqual(form['category'].value(), '20')
        file_list = form['file_field'].value()
        self.assertEqual(file_list[0].name, 'board/test_modifyimage1.jpg')

    def test_postRightAccess(self):
        image2 = SimpleUploadedFile(name='test_modifyimage2.jpg', content=b'1112', content_type='image/jpeg')
        self.client.login(userid='bruce1115', password='as1df1234')  # 올바른 사용자의 로그인 후 접근
        response = self.client.post(reverse('board:post_modify', args=[1]), {'subject': 'test 1', 'content': 'data',
                                                                             'category': '21', 'file_field': [image2]})
        post = Post.objects.get(subject='test 1')
        self.assertEqual(post.content, 'data')
        self.assertEqual(post.category, '21')
        self.assertEqual(post.media.get(post_id=1).file.name, 'board/' + image2.name)
        self.assertRedirects(response, reverse('board:post_detail', args=[1]), status_code=302)

    def test_postWrongAccess(self):
        image2 = SimpleUploadedFile(name='test_modifyimage2.jpg', content=b'1112', content_type='image/jpeg')
        self.client.login(userid='bruce1115', password='as1df1234')  # 올바른 사용자의 로그인 후 접근
        response = self.client.post(reverse('board:post_modify', args=[1]), {'subject': '', 'content': 'data',
                                                                             'category': '21', 'file_field': [
                image2]})  # invalid form이 입력될 때의 결과
        form = response.context['form']
        self.assertTemplateUsed(response, 'board/create_post.html')
        self.assertEqual(form['subject'].value(), 'test 1')
        self.assertEqual(form['content'].value(), 'no data')
        self.assertEqual(form['category'].value(), '20')
        file_list = form['file_field'].value()
        self.assertEqual(file_list[0].name, 'board/test_modifyimage1.jpg')


class CreateCommentTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        hashed_password = make_password('dbsrbals1')
        User.objects.create(userid='dbsrbals1', email='dbsrbals27@gmail.com',  # user_id=1
                            password=hashed_password, nickname='ygm1')
        hashed_password = make_password('dbsrbals')
        User.objects.create(userid='dbsrbals', email='dbsrbals26@gmail.com',  # user_id=2
                            password=hashed_password, nickname='ygm')
        hashed_password = make_password('as1df1234')
        User.objects.create(userid='bruce11156', email='bruce1115123@naver.com',  # user_id=3
                            password=hashed_password, nickname='BRUCE123123')

    def setUp(self) -> None:
        client = Client()

    def test_formIsvalid(self):
        file1 = SimpleUploadedFile(name='test_image1.jpg', content=b'1', content_type='image/jpeg')
        file2 = SimpleUploadedFile(name='test_image2.jpg', content=b'2', content_type='image/jpeg')
        file3 = SimpleUploadedFile(name='test_image3.jpg', content=b'3', content_type='image/jpeg')
        form = CommentForm(data={'content': 'comment_content'},
                           files=MultiValueDict({'file_field': [file1, file2, file3]}))
        self.assertTrue(form.is_valid())

    def test_checkDataSave(self):
        file1 = SimpleUploadedFile(name='test_image1.jpg', content=b'1', content_type='image/jpeg')
        file2 = SimpleUploadedFile(name='test_image2.jpg', content=b'2', content_type='image/jpeg')
        file3 = SimpleUploadedFile(name='test_image3.jpg', content=b'3', content_type='image/jpeg')
        Post.objects.create(subject='30', content='no data', create_date=timezone.now(),
                            user_id=1, category='33')
        form = CommentForm(data={'content': 'comment_content'},
                           files=MultiValueDict({'file_field': [file1, file2, file3]}))
        self.assertTrue(form.is_valid())
        self.client.login(userid='bruce11156', password='as1df1234')
        self.assertEqual(Comment.objects.count(), 0)
        self.client.post(reverse('board:comment_create', args=[1]),
                         {'content': 'comment_content', 'file_field': [file1, file2, file3]})
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Media.objects.count(), 3)
        self.client.logout()

    def test_childComment(self):
        file1 = SimpleUploadedFile(name='test_image1.jpg', content=b'1', content_type='image/jpeg')
        file2 = SimpleUploadedFile(name='test_image2.jpg', content=b'2', content_type='image/jpeg')
        file3 = SimpleUploadedFile(name='test_image3.jpg', content=b'3', content_type='image/jpeg')
        file4 = SimpleUploadedFile(name='test_image4.jpg', content=b'4', content_type='image/jpeg')
        file5 = SimpleUploadedFile(name='test_image5.jpg', content=b'5', content_type='image/jpeg')
        file6 = SimpleUploadedFile(name='test_image6.jpg', content=b'6', content_type='image/jpeg')
        file7 = SimpleUploadedFile(name='test_image7.jpg', content=b'7', content_type='image/jpeg')
        file8 = SimpleUploadedFile(name='test_image8.jpg', content=b'8', content_type='image/jpeg')
        Post.objects.create(subject='test_data', content='no data', create_date=timezone.now(),
                            user_id=1, category='34')
        self.client.login(userid='dbsrbals1', password='dbsrbals1')  # id=1
        self.client.post(reverse('board:comment_create', args=[1]),
                         {'content': 'comment_content', 'file_field': [file1, file2, file3]})
        self.client.post(reverse('board:comment_create', args=[1, 1]),
                         {'content': 'child_comment_content1', 'file_field': [file4, file5, file6]})
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Media.objects.count(), 6)
        self.assertEqual(len(Comment.objects.filter(parent_comment=1)), 1)
        self.assertEqual(len(Comment.objects.filter(parent_comment=None)), 1)
        self.client.logout()
        self.client.login(userid='dbsrbals', password='dbsrbals')  # id=2
        self.client.post(reverse('board:comment_create', args=[1, 1]),
                         {'content': 'child_comment_content1', 'file_field': [file7, file8]})
        self.assertEqual(Comment.objects.count(), 3)
        self.assertEqual(Media.objects.count(), 8)
        self.assertEqual(len(Comment.objects.filter(parent_comment=1)), 2)
        self.assertEqual(len(Comment.objects.filter(parent_comment=None)), 1)
        self.client.post(reverse('board:comment_create', args=[1]),
                         {'content': 'child_comment_content1'})
        self.assertEqual(Comment.objects.count(), 4)
        self.assertEqual(Media.objects.count(), 8)
        self.assertEqual(len(Comment.objects.filter(parent_comment=1)), 2)
        self.assertEqual(len(Comment.objects.filter(parent_comment=None)), 2)
        self.client.logout()

    def test_DeleteCommentByDeletePost(self):
        file1 = SimpleUploadedFile(name='test_image1.jpg', content=b'1', content_type='image/jpeg')
        file2 = SimpleUploadedFile(name='test_image2.jpg', content=b'2', content_type='image/jpeg')
        file3 = SimpleUploadedFile(name='test_image3.jpg', content=b'3', content_type='image/jpeg')
        file4 = SimpleUploadedFile(name='test_image4.jpg', content=b'4', content_type='image/jpeg')
        Post.objects.create(subject='test_data', content='no data', create_date=timezone.now(),
                            user_id=1, category='34')
        self.client.login(userid='dbsrbals1', password='dbsrbals1')  # id=1
        self.client.post(reverse('board:comment_create', args=[1]),
                         {'content': 'comment_content', 'file_field': [file1, file2]})
        self.client.post(reverse('board:comment_create', args=[1, 1]),
                         {'content': 'child_comment_content1', 'file_field': [file3, file4]})
        self.client.logout()
        self.client.login(userid='dbsrbals', password='dbsrbals')  # id=2
        self.client.post(reverse('board:comment_create', args=[1, 1]),
                         {'content': 'child_comment_content1'})
        self.assertEqual(Comment.objects.count(), 3)
        self.assertEqual(Media.objects.count(), 4)
        self.assertEqual(len(Comment.objects.filter(parent_comment=1)), 2)
        self.assertEqual(len(Comment.objects.filter(parent_comment=None)), 1)
        self.client.logout()

        self.client.login(userid='dbsrbals1', password='dbsrbals1')  # id=1
        Post.objects.filter(id=1).delete()
        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(Media.objects.count(), 0)
        self.assertEqual(len(Comment.objects.filter(parent_comment=1)), 0)
        self.assertEqual(len(Comment.objects.filter(parent_comment=None)), 0)
        self.client.logout()

    def test_commentDelete(self):
        file1 = SimpleUploadedFile(name='test_image1.jpg', content=b'1', content_type='image/jpeg')
        file2 = SimpleUploadedFile(name='test_image2.jpg', content=b'2', content_type='image/jpeg')
        file3 = SimpleUploadedFile(name='test_image3.jpg', content=b'3', content_type='image/jpeg')
        file4 = SimpleUploadedFile(name='test_image4.jpg', content=b'4', content_type='image/jpeg')
        file5 = SimpleUploadedFile(name='test_image5.jpg', content=b'5', content_type='image/jpeg')
        file6 = SimpleUploadedFile(name='test_image6.jpg', content=b'6', content_type='image/jpeg')

        Post.objects.create(subject='test_data', content='no data', create_date=timezone.now(),
                            user_id=1, category='34')
        self.client.login(userid='dbsrbals1', password='dbsrbals1')  # id=1
        self.client.post(reverse('board:comment_create', args=[1]),
                         {'content': 'comment_content', 'file_field': [file1, file2]})
        self.client.post(reverse('board:comment_create', args=[1, 1]),
                         {'content': 'child_comment_content1', 'file_field': [file3, file4]})
        self.client.logout()
        self.client.login(userid='dbsrbals', password='dbsrbals')  # id=2
        self.client.post(reverse('board:comment_create', args=[1, 1]),
                         {'content': 'child_comment_content2'})
        self.client.post(reverse('board:comment_create', args=[1]),
                         {'content': 'child_comment_content3', 'file_field': [file5, file6]})
        self.assertEqual(Comment.objects.count(), 4)
        self.assertEqual(Media.objects.count(), 6)
        self.assertEqual(len(Comment.objects.filter(parent_comment=1)), 2)
        self.assertEqual(len(Comment.objects.filter(parent_comment=None)), 2)
        self.client.logout()

        self.client.login(userid='dbsrbals1', password='dbsrbals1')  # id=1
        Comment.objects.filter(content='comment_content').delete()
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Media.objects.count(), 2)
        self.assertEqual(len(Comment.objects.filter(parent_comment=1)), 0)
        self.assertEqual(len(Comment.objects.filter(parent_comment=None)), 1)
