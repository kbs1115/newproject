from django.db.models import Q, Count
from django.shortcuts import render
from users.models import User

from ..models import Post


def index(request):
    notice = Post.objects.filter(category='40').order_by('-create_date')
    question_korean = Post.objects.filter(category='11').order_by('-create_date')
    question_math = Post.objects.filter(category='12').order_by('-create_date')
    question_english = Post.objects.filter(category='13').order_by('-create_date')
    question_etc = Post.objects.filter(category='14').order_by('-create_date')
    free = Post.objects.filter(category='20').order_by('-create_date')
    best_voter = Post.objects.exclude(category='40')
    best_voter = best_voter.annotate(voter_cnt=Count('voter')).order_by('-voter_cnt')

    notice = notice[:10]
    question_korean = question_korean[:5]
    question_math = question_math[:5]
    question_english = question_english[:5]
    question_etc = question_etc[:5]
    free = free[:10]
    best_voter = best_voter[:10]

    context = {'notice_board': notice, 'question_korean': question_korean, 'question_math': question_math,
               'question_english': question_english, 'question_etc': question_etc, 'free_board': free,
               'best_voter': best_voter}
    return render(request, 'board/index.html', context)


def nav_search(request):
    kw = request.GET.get('kw', '')
    order_category = {0: '2', 1: '3', 2: '1'}
    target_list = [list(), list(), list()]
    for i in [0, 1, 2]:
        target_list[i] = Post.objects.filter(category__startswith=order_category[i])  # 문제인 부분!
        target_list[i] = target_list[i].annotate(voter_count=Count('voter')).order_by('-voter_count')
        target_list[i] = target_list[i].filter(
            Q(subject__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(comment__content__icontains=kw) |  # 답변 내용 검색
            Q(user__nickname__icontains=kw) |  # 질문 글쓴이 검색
            Q(comment__user__nickname__icontains=kw)  # 답변 글쓴이 검색
        ).distinct()
        target_list[i] = target_list[i][:5]

    context = {'free_list': target_list[0], 'data_list': target_list[1], 'question_list': target_list[2], 'kw': kw}
    return render(request, 'board/search_list.html', context)


def posts(request, category: int):

    if category % 10 == 0:  # question_list , data_board의 전체를 다 가져오고싶을때
        quotient = category // 10
        quotient = str(quotient)
        post = Post.object.filter(category__startswith=quotient)
    else:
        category = str(category)
        post = Post.object.filter(category=category)

    detail = request.GET.get('detail', 'all')  # all , subject ,content, user, subAndContent
    kw = request.GET.get('kw', '')
    sort = request.GET.get('sort', '-create_date')  # sort 종류는 -create_date, 추천수 2개가있음

    if detail == 'all':
        post = post.filter(
            Q(subject__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(comment__content__icontains=kw) |  # 답변 내용 검색
            Q(user__nickname__icontains=kw) |  # 질문 글쓴이 검색
            Q(comment__user__nickname__icontains=kw)  # 답변 글쓴이 검색
        ).distinct()
    elif detail == 'subject':
        post = post.filter(Q(subject__icontains=kw))
    elif detail == 'content':
        post = post.filter(Q(content__icontains=kw))
    elif detail == 'user':
        post = post.filter(Q(user__nickname__icontains=kw))
    elif detail == 'subAndContent':
        post = post.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw)
        ).distinct()

    if sort == 'voter_count':
        post = post.annotate(voter_count=Count('voter')).order_by('-voter_count')
    else:
        post = post.order_by('-create_date')

    context = {'post': post}
    return render(request, 'board/posts.html', context)
