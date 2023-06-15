from django.contrib.auth.models import User
from django.db import models

from brainservice.models import Team


# Create your models here.
# 글의 별점
class Invite(models.Model):


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Invite <-> User N:1, 초대자
    from_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name="invite_host_team")

    # Invite <-> User N:1, 수신자
    to_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name="invite_guest_team")

    # Invite <-> Team N:1, 수신자
    team = models.ForeignKey(Team, null=False, on_delete=models.CASCADE)
    is_accept = models.BooleanField(null=True)

    def __str__(self):
        return f'[{self.pk}]'

    def inviting_info(self):
        if self.is_accept == True:
            accept = "수락완료"
        elif self.is_accept == False:
            accept = "거절완료"
        else:
            accept = "미확인"

        return accept

    def get_absolute_url(self):
        return f'/main/invite'

    def created_at_datetime(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S')