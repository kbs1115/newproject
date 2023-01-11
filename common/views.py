from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from common.forms import UserForm
from board.models import Post, Comment
from django.core.paginator import Paginator
from users.models import User
from django.contrib.auth.decorators import login_required


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            userid = form.cleaned_data.get('userid')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(userid=userid, password=raw_password)  # 사용자 인증
            login(request, user)  # 로그인
            return redirect('board:index')
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('board:index')

    if request.method == 'POST':
        userid = request.POST['userid'].lower()
        password = request.POST['password']

        user = authenticate(request, userid=userid, password=password)

        if user is not None:
            login(request, user)
            return redirect('board:index')
        else:
            messages.error(request, '아이디 혹은 비밀번호가 틀렸습니다.')

    return render(request, 'common/login.html')


@login_required(login_url="common:login")
def mypage(request):
    page_post = request.GET.get('page1', '1')
    page_comment = request.GET.get('page2', '1')
    post_list = Post.objects.filter(user=request.user).order_by('-create_date')
    comment_list = Comment.objects.filter(user=request.user).order_by('-create_date')
    paginator_post = Paginator(post_list, 5)
    paginator_comment = Paginator(comment_list, 5)
    post_obj = paginator_post.get_page(page_post)
    comment_obj = paginator_comment.get_page(page_comment)
    context = {'post_list': post_obj, 'comment_list': comment_obj}
    return render(request, 'common/mypage.html', context)


# @login_required(login_url="common:login")
# def mypage_modify(request):

