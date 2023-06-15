from brainservice.models import Team
from .models import Invite
from django import forms
class InviteForm(forms.ModelForm):
    to_user_email = forms.EmailField(label='To User Email')

    class Meta:
        model = Invite
        fields = ['team']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(InviteForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['team'].queryset = Team.objects.filter(users=user)


class InviteResponseForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ('is_accept',)
