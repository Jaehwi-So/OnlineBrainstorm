from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404

from brainservice.models import Team


class IsTeamMemberRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        team = get_object_or_404(Team, pk=self.kwargs['team_pk'])
        return team.users.filter(pk=user.pk).exists()