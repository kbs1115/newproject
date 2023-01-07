from django import forms

from board.models import Search


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Search
        fields = ['content']
