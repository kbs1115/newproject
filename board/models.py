from django.db import models

# user_id ->user , modify_date추가
from users.models import User


# 12.4수정) 게시판 종류를 결정하는 카테고리 필드추가
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_post')
    subject = models.CharField(max_length=50)
    content = models.TextField()
    create_date = models.DateTimeField()
    voter = models.ManyToManyField(User, related_name='voter_post')
    modify_date = models.DateTimeField(null=True, blank=True)
    category = models.TextField(null=False, blank=False, default="free_board")
    # notice, question, free , data 게시판


# user_id ->user, voter_id -> voter, post_id->post , modify_date 추가
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField
    voter = models.ManyToManyField(User, related_name='voter_comment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment')
    modify_date = models.DateTimeField(null=True, blank=True)


# 파일테이블 추가 Post테이블을 바라봄
class Media(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_media')
    file = models.FileField(upload_to='board/')
