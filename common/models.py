from django.db import models
from users.models import User


# 알림 기능
class Alert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_alert')
    alert_type = models.CharField(max_length=20, null=False, blank=False)
    create_date = models.DateTimeField()
    data = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_alert')
