from django.shortcuts import render

from board.models import LecturesLink


# default 는 category =3, teacher_id 1 -> 영어, 선생님1
# 번호는 model 참고
def lectures(request, category: int, teacher_id: int):
    lecture_objs = LecturesLink.objects.filter(category=category, teacher=teacher_id).order_by('-id')
    context = {'lectures': lecture_objs}
    return render(request, 'board/lectures.html', context)
