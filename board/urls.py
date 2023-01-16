from django.urls import path
from .views import base_views, post_views

app_name = 'board'
urlpatterns = [
    path('', base_views.index, name='index'),
    path('search/', base_views.nav_search, name='search'),
    path('posts/<int:category>', post_views.posts, name='posts'),
    path('post/delete/<int:post_id>', post_views.post_delete, name='post_delete'),
]