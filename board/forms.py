from importlib.resources import _

from django import forms
from django.core.exceptions import ValidationError

from board.models import Post, Comment
from ckeditor.widgets import CKEditorWidget


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "subject", "category"]


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textarea_id_counter = 0
        self.fields["content"].widget = CKEditorWidget(
            attrs={"id": self.get_textarea_next_id}
        )

    def get_textarea_next_id(self):
        result = self.textarea_id_counter
        self.textarea_id_counter += 1
        return result

    class Meta:
        model = Comment
        fields = ["content"]
