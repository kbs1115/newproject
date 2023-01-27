from django.db import models

# user_id ->user , modify_date추가
from users.models import User

"""
1.1수정) category 필드에 들어가는 데이터종류(단 데이터타입이 String이다):
또한 category중 일의자리가 0으로 끝나는 데이터는 실제로 존재하지않음. 단순히 views에서 처리하기위함.
-----------------------
question_list ->'10'
question_korean ->'11'
question_math ->'12'
question_english ->'13'
question_etc ->'14'
-----------------------
free_board ->'20'
-----------------------
data_board -> '30'
data_korean ->'31'
data_math ->'32'
data_english -> '33'
data_etc -> '34'
-----------------------
notice_board ->'40'
------------------
"""


# 12.4수정) 게시판 종류를 결정하는 카테고리 필드추가
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post')
    subject = models.CharField(max_length=50)
    content = models.TextField()
    create_date = models.DateTimeField()
    category = models.TextField(default='20')
    voter = models.ManyToManyField(User, related_name='voter_post')
    modify_date = models.DateTimeField(null=True, blank=True)


# user_id ->user, voter_id -> voter, post_id->post , modify_date 추가
# parent_comment는 대댓글여부를 판단하는 필드이다. 부모댓글이 없는경우 대댓글이 아닌걸로 판단한다.
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    voter = models.ManyToManyField(User, related_name='voter_comment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment')
    modify_date = models.DateTimeField(null=True, blank=True)
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, related_name='parent_comment_comment',
                                       null=True)


# 파일테이블 추가 Post테이블을 바라봄
class Media(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_media', blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_media', blank=True, null=True)
    file = models.FileField(upload_to='board/', null=True, blank=True)
