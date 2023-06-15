
from django import forms

from brainservice.models import Post

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', )
