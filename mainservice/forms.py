from .models import Invite
from django import forms
class InviteForm(forms.ModelForm):
    to_user_email = forms.EmailField(label='To User Email')

    class Meta:
        model = Invite
        fields = ['team']