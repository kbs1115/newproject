import datetime

from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from ..forms import CommentForm
from ..models import Post, Comment, Media


@login_required(login_url="common:login")
def comment_create(request, post_id, parent_comment_id=None):
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = Comment()
            comment.post = get_object_or_404(Post, id=post_id)
            comment.content = form.cleaned_data['content']
            comment.user = request.user
            comment.create_date = timezone.now()
            if parent_comment_id is not None:
                comment.parent_comment = Comment.objects.get(id=parent_comment_id)
            comment.save()
            files = request.FILES.getlist('file_field')
            if files is not None:
                for f in files:
                    media = Media()
                    media.comment = comment
                    media.file = f
                    media.save()
    return redirect('board:post_detail', post_id=post_id)


@login_required(login_url="common:login")
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.user:
        messages.error(request, "댓글 삭제 권한이 없습니다.")
        return redirect('board:post_detail', post_id=comment.post.id)
    comment.delete()
    return redirect('board:post_detail', post_id=comment.post.id)

# def comment_modify(request, ):
#     pass


@login_required(login_url="common:login")
def comment_vote(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.user:
        messages.error(request, '본인이 작성한 댓글은 추천할 수 없습니다.')
    else:
        comment.voter.add(request.user)
    return redirect('board:post_detail', post_id=comment.post.id)
