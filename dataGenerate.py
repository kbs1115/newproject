import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from board.models import Post
from django.utils import timezone

for i in range(100):
    p = Post(
        user_id=1,
        subject="test",
        content="t",
        create_date=timezone.now(),
        category="31",
    )
    p.save()
