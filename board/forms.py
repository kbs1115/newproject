from django import forms

from board.models import Post


class PostForm(forms.Form):
    category = forms.CharField()
    subject = forms.CharField(max_length=50)
    content = forms.CharField()
    # file = forms.FileField(required=False)
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)


class CommentForm(forms.Form):
    content = forms.CharField()
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
