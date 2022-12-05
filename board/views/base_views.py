from django.shortcuts import render
from django.db.models import Q, Count
from ..models import Post


def search_view(request):
    kw = request.GET.get('kw', '')
    free_list, data_list, question_list = list()
    order_category = {1: 'free', 2: 'data', 3: 'question'}
    target_list = {1: free_list, 2: data_list, 3: question_list}
    for i in [1, 2, 3]:
        target_list[i] = Post.objects.filter(category__startswith=order_category[i])
        target_list[i] = target_list[i].annotate(voter_count=Count('voter')).order_by('-voter_count')
        target_list[i] = target_list[i].filter(
            Q(subject__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(comment__content__icontains=kw) |  # 답변 내용 검색
            Q(author__nickname__icontains=kw) |  # 질문 글쓴이 검색
            Q(comment__author__nickname__icontains=kw)  # 답변 글쓴이 검색
        ).distinct()
        target_list[i] = target_list[i][:5]

    context = {'free_list': free_list, 'data_list': data_list, 'question_list': question_list, 'kw': kw}
    return render(request, 'board/search_list.html', context)
