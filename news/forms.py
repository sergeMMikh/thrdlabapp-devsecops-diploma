from .models import Articles
from django.forms import ModelForm, TextInput, Textarea, Select


class ArticlesForm(ModelForm):
    class Meta:
        model = Articles
        fields = ('title', 'full_text', 'author')

        widgets = {
            "title": TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Title',
                },
            ),
            "author": Select(
                attrs={
                    'class': 'form-control',
                },
            ),
            "full_text": Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Text of article',
                },
            ),
        }
