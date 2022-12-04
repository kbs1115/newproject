from django.shortcuts import render
from django.db.models import Q
from ..models import Post


def search_view(request):
    kw = request.GET.get('kw', '')
    free_list = Post.objects.filter(category__startswith='free')
    free_list = free_list.filter(
        Q(subject__icontains=kw) |  # 제목 검색
        Q(content__icontains=kw) |  # 내용 검색
        Q(comment__content__icontains=kw) |  # 답변 내용 검색
        Q(author__nickname__icontains=kw) |  # 질문 글쓴이 검색
        Q(comment__author__nickname__icontains=kw)  # 답변 글쓴이 검색
    ).distinct()
    data_list = Post.objects.filter(category__startswith='data')
    data_list = data_list.filter(
        Q(subject__icontains=kw) |  # 제목 검색
        Q(content__icontains=kw) |  # 내용 검색
        Q(comment__content__icontains=kw) |  # 답변 내용 검색
        Q(author__nickname__icontains=kw) |  # 질문 글쓴이 검색
        Q(comment__author__nickname__icontains=kw)  # 답변 글쓴이 검색
    ).distinct()
    question_list = Post.objects.filter(category__startswith='question')
    question_list = question_list.filter(
        Q(subject__icontains=kw) |  # 제목 검색
        Q(content__icontains=kw) |  # 내용 검색
        Q(comment__content__icontains=kw) |  # 답변 내용 검색
        Q(author__nickname__icontains=kw) |  # 질문 글쓴이 검색
        Q(comment__author__nickname__icontains=kw)  # 답변 글쓴이 검색
    ).distinct()
    context = {'free_list': free_list, 'data_list': data_list, 'question_list': question_list, 'kw': kw}
    return render(request, 'pybo/search_list.html', context)
