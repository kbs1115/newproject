from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from board.forms import PostForm, CommentForm
from board.models import Post, Media
from common.models import Notification, Data


def posts(request, category: int):
    detail = request.GET.get(
        "detail", "all"
    )  # all , subject ,content, user, subAndContent
    kw = request.GET.get("kw_posts", "")
    sort = request.GET.get("sort", "update")  # sort 종류는 -create_date, 추천수 2개가 있음
    page = request.GET.get("page", "1")  # 페이징 처리

    if category % 10 == 0:  # question_list , data_board의 전체를 다 가져오고싶을때
        quotient = category // 10
        quotient = str(quotient)
        post = Post.objects.filter(category__startswith=quotient)
    else:
        category = str(category)
        post = Post.objects.filter(category=category)

    if detail == "all":
        post = post.filter(
            Q(subject__icontains=kw)
            | Q(content__icontains=kw)  # 제목 검색
            | Q(comment__content__icontains=kw)  # 내용 검색
            | Q(user__nickname__icontains=kw)  # 답변 내용 검색
            | Q(comment__user__nickname__icontains=kw)  # 질문 글쓴이 검색  # 답변 글쓴이 검색
        ).distinct()
    elif detail == "subject":
        post = post.filter(Q(subject__icontains=kw))
    elif detail == "content":
        post = post.filter(Q(content__icontains=kw))
    elif detail == "user":
        post = post.filter(Q(user__nickname__icontains=kw))
    elif detail == "subAndContent":
        post = post.filter(
            Q(subject__icontains=kw) | Q(content__icontains=kw)
        ).distinct()

    if sort == "voter_count":
        post = post.annotate(voter_count=Count("voter")).order_by("-voter_count")
    elif sort == "update":
        post = post.order_by("-create_date")

    paginator = Paginator(post, 10)  # 페이징처리
    page_obj = paginator.get_page(page)

    # category 넘기고, 탭메뉴 클릭 시 category 인자를 배열에 넣어서 보내 줌.
    category = int(category)
    quotient = category // 10

    context = {
        "post": page_obj,
        "detail": detail,
        "category": category,
        "quotient": quotient * 10,
    }
    return render(request, "board/posts.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()

    voted = False
    isAuthor = False

    if request.user.is_authenticated:
        if request.user == post.user:
            isAuthor = True
        if post.voter.filter(id=request.user.id).exists():
            voted = True

    context = {
        "post": post,
        "commentForm": form,
        "isVoted": voted,
        "isAuthor": isAuthor,
    }
    return render(request, "board/post_detail.html", context)


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
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = Post()
            post.category = form.cleaned_data["category"]
            post.subject = form.cleaned_data["subject"]
            post.content = form.cleaned_data["content"]
            post.user = request.user
            post.create_date = timezone.now()
            post.save()
            files = request.FILES.getlist("file_field")
            if files is not None:
                for f in files:
                    media = Media()
                    media.post = post
                    media.file = f
                    media.save()
            return redirect("board:post_detail", post_id=post.id)
    else:
        form = PostForm()
    context = {"form": form}
    return render(request, "board/create_post.html", context)


@login_required(login_url="common:login")
def post_modify(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.user:
        messages.error(request, "게시글 수정 권한이 없습니다.")
        return redirect("board:post_detail", post_id=post.id)
    images = post.post_media.all()
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            images.delete()
            post = form.save(commit=False)
            post.modify_date = timezone.now()
            post.save()  # 기존의 데이터는 modelform을 활용하여 저장한다.
            files = request.FILES.getlist("file_field")
            if files is not None:
                for f in files:
                    media = Media()
                    media.post = post
                    media.file = f
                    media.save()  # 이미지 파일은 media 객체를 만들어 추가하는 방식으로 저장한다.
            return redirect("board:post_detail", post_id=post.id)

    post = Post.objects.get(pk=post.id)
    filelist = list()
    for med in post.post_media.all():
        filelist = filelist + [med.file]
    form = PostForm(instance=post)
    form.fields["file_field"].initial = filelist
    context = {"form": form}
    return render(request, "board/create_post.html", context)


@login_required(login_url="common:login")
def post_vote(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.user:
        messages.error(request, "본인이 작성한 글은 추천할 수 없습니다.")
    else:
        post.voter.add(request.user)

        data = Data.objects.create(
            sent_user=request.user, post=post, notice_type="vote_of_post"
        )
        data.save()
        notification = Notification.objects.create(
            received_user=post.user, create_date=timezone.now(), data=data
        )
        notification.save()
    return redirect("board:post_detail", post_id=post.id)
