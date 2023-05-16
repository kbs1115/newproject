from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from common.models import Data, Notification
from ..forms import CommentForm
from django.contrib import messages
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
            if parent_comment_id is not None:
                data = Data.objects.create(sent_user=request.user, comment=comment,
                                           notice_type="reply_of_comment")
                data.save()
                receiver = Comment.objects.get(id=parent_comment_id).user
                notification = Notification.objects.create(received_user=receiver, create_date=timezone.now(),
                                                           data=data)
                notification.save()
            else:
                data = Data.objects.create(sent_user=request.user, comment=comment, notice_type="comment_of_post")
                data.save()
                receiver = Post.objects.get(id=post_id).user
                notification = Notification.objects.create(received_user=receiver, create_date=timezone.now(),
                                                           data=data)
                notification.save()
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


# modify button click event 발생시 발생된 댓글의 id를 get형식으로 넘겨줌
@login_required(login_url="common:login")
def comment_modify(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.user:
        messages.error(request, "댓글 수정 권한이 없습니다.")
        return redirect('board:post_detail', post_id=comment.post.id)
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES, instance=comment)
        files = comment.comment_media.all()
        if form.is_valid():
            files.delete()
            comment = form.save(commit=False)
            comment.modify_date = timezone.now()
            comment.save()
            files = request.FILES.getlist('file_field')
            for f in files:
                media = Media()
                media.comment = comment
                media.file = f
                media.save()
            return redirect('board:post_detail', post_id=comment.post.id)
    comment = Comment.objects.get(id=comment_id)
    content = str(comment)
    form = CommentForm(data={'content': content},
                       instance=comment)
    filelist = list()
    for med in comment.comment_media.all():
        filelist = filelist + [med.file]
    form.fields['file_field'].initial = filelist
    context = {'form': form}
    return render(request, 'board/post_detail.html', context)


@login_required(login_url="common:login")
def comment_vote(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.user:
        messages.error(request, '본인이 작성한 댓글은 추천할 수 없습니다.')
    else:
        comment.voter.add(request.user)
        data = Data.objects.create(sent_user=request.user, comment=comment, notice_type="vote_of_comment")
        data.save()
        notification = Notification.objects.create(received_user=comment.user, create_date=timezone.now(), data=data)
        notification.save()
    return redirect('board:post_detail', post_id=comment.post.id)
