from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from common.forms import UserForm
from users.models import User


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






