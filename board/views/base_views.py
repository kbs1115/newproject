from django.db.models import Q, Count
from django.shortcuts import render
from board.models import Post
from users.models import User

def index(request):
    notice = Post.objects.filter(category='notice_board').order_by('-create_date')
    question_korean = Post.objects.filter(category='question_korean').order_by('-create_date')
    question_math = Post.objects.filter(category='question_math').order_by('-create_date')
    question_english = Post.objects.filter(category='question_english').order_by('-create_date')
    question_etc = Post.objects.filter(category='question_etc').order_by('-create_date')
    free = Post.objects.filter(category='free_board').order_by('-create_date')
    best_voter = Post.objects.exclude(category='notice_board')
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
    return render(request, 'index.html', context)

def nav_search(request):
    kw = request.GET.get('kw', '')
    free_list = list()
    data_list = list()
    question_list = list()
    order_category = {1: 'free', 2: 'data', 3: 'question'}
    target_list = {1: free_list, 2: data_list, 3: question_list}
    for i in [1, 2, 3]:
        target_list[i] = Post.objects.filter(category__startswith=order_category[i])
        target_list[i] = target_list[i].annotate(voter_count=Count('voter')).order_by('-voter_count')
        target_list[i] = target_list[i].filter(
            Q(subject__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(comment__content__icontains=kw) |  # 답변 내용 검색
            Q(user__nickname__icontains=kw) |  # 질문 글쓴이 검색
            Q(comment__user__nickname__icontains=kw)  # 답변 글쓴이 검색
        ).distinct()
        target_list[i] = target_list[i][:5]

    context = {'free_list': free_list, 'data_list': data_list, 'question_list': question_list, 'kw': kw}
    return render(request, 'board/search_list.html', context)
