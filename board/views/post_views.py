from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.views import generic
from board.forms import PostForm
from board.models import Post, Media


def posts(request, category: int):
    detail = request.GET.get('detail', 'all')  # all , subject ,content, user, subAndContent
    kw = request.GET.get('kw', '')
    sort = request.GET.get('sort', 'update')  # sort 종류는 -create_date, 추천수 2개가 있음
    page = request.GET.get('page', '1')  # 페이징 처리

    if category % 10 == 0:  # question_list , data_board의 전체를 다 가져오고싶을때
        quotient = category // 10
        quotient = str(quotient)
        post = Post.objects.filter(category__startswith=quotient)
    else:
        category = str(category)
        post = Post.objects.filter(category=category)

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
    elif sort == 'update':
        post = post.order_by('-create_date')

    paginator = Paginator(post, 30)  # 페이징처리
    page_obj = paginator.get_page(page)

    # testcode를 위해 detail과 category를 같이 넘겨주었음. 사실 post,page_obj만 필요함!!! 실질적으로는 page_obj만 필요 !
    category = int(category)
    context = {'post': post, 'page_obj': page_obj, 'detail': detail, 'category': category}
    return render(request, 'board/posts.html', context)


@login_required(login_url="common:login")
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.user:
        messages.error(request, "게시글 삭제 권한이 없습니다.")
        # return redirect("board:posts", category=post.category) 여기에 post_detail url로 넘겨 줘야함.
    post.delete()
    return redirect("board:posts", category=post.category)


@login_required(login_url="common:login")
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        # if form.is_valid():
        post = Post()
        post.category = request.POST['category']
        post.subject = request.POST['subject']
        post.content = request.POST['content']
        post.user = request.user
        post.create_date = timezone.now()
        post.save()
<<<<<<< HEAD
        # files = request.FILES['file']
=======

>>>>>>> fe6d08e440ca0bb3842bd864be3de3604e4af60c
        files = request.FILES.getlist('file_field')
        if files is not None:
            for f in files:
                media = Media()
                media.post = post
                media.file = f
                media.save()
        return redirect('board:posts', post.category)
    else:
        form = PostForm()
    context = {'form': form}
    return render(request, 'board/create_post.html', context)



<<<<<<< HEAD
=======
    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        for field in form:
            print("Field Error:", field.name, field.errors)

>>>>>>> fe6d08e440ca0bb3842bd864be3de3604e4af60c
