from django.db import models
from board.models import Post, Comment
from users.models import User
from common.models import Data


# 알림 기능
# notice_type: vote_of_post, vote_of_comment, reply_of_comment, comment_of_post, favorite_of_post,
# 여기서 user은 notice를 받은 user이고 data 는 notice를 줄때 넘겨받은 여러 데이터들이다
class Notification(models.Model):
    received_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_alert')
    notice_type = models.CharField(max_length=20, null=False, blank=False)
    create_date = models.DateTimeField()
    data = models.ForeignKey(Data, on_delete=models.CASCADE, related_name='data_alert')


# notice를 발생시킨게 post인지 comment인지, 어떤 user에 의해서 notice가 발생했는지
class Data(models.Model):
    sent_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_data', null=False, blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_data', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_data', null=True, blank=True)
