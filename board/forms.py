from importlib.resources import _

from django import forms
from django.core.exceptions import ValidationError

from board.models import Post, Comment


class PostForm(forms.ModelForm):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Post
        fields = ['content', 'subject', 'category']


class CommentForm(forms.ModelForm):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Comment
        fields = ['content']


class A(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
