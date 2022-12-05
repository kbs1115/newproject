from django.db.models import Count
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

