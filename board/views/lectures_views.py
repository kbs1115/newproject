from django.shortcuts import render

from board.models import LecturesLink


def lectures(request, category: int, teacher_id: int):
    lecture_obj = LecturesLink.objects.filter(category=category, teacher_id=teacher_id).order_by('-id')
    context = {'lectures': lecture_obj}
    return render(request, 'board/lectures.html', context)
