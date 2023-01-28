from django import forms

from board.models import Post


class PostForm(forms.ModelForm):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    class Meta:
        model = Post
        fields = ['content', 'subject', 'category']

class CommentForm(forms.Form):
    content = forms.CharField()
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

