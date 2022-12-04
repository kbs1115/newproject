from django.shortcuts import render
from django.core.paginator import Paginator
from board.models import Post
from django.db.models import Q


def search_view(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    post_list = Post.objects.order_by('-create_date')
    post_list = post_list.filter(
        Q(subject__icontains=kw) |  # 제목 검색
        Q(content__icontains=kw) |  # 내용 검색
        Q(comment__content__icontains=kw) |  # 답변 내용 검색
        Q(author__nickname__icontains=kw) |  # 질문 글쓴이 검색
        Q(comment__author__nickname__icontains=kw)  # 답변 글쓴이 검색
    ).distinct()
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(page)
    context = {'post_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'pybo/search_list.html', context)
