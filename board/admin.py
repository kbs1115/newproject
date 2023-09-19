from django.contrib import admin
from .models import Post, Media, Comment

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Media)
