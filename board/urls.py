from django.urls import path
from .views import base_views

app_name = 'board'

urlpatterns = [
    path('search/', base_views.search_view, name='search_view'),
]
