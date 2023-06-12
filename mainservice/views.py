from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView

from brainservice.models import Team
from mainservice.forms import InviteForm
from mainservice.models import Invite


def main_page(request):
    return render(
        request,
        'main/main.html'
)

def invite_page(request):
    return render(
        request,
        'main/invite.html'
)



#CBV

## 포스팅 리스트
class TeamList(LoginRequiredMixin, TemplateView):
    template_name = 'main/team.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        teams = user.team_set.all()  # 사용자가 속한 모든 팀 가져오기
        context['teams'] = teams
        return context



class TeamCreate(LoginRequiredMixin, CreateView):
    model = Team
    fields = ['title']
    template_name = 'main/team_form.html'   #템플릿 설정

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.admin = current_user
            form.save()  # Team 객체를 먼저 저장하여 id 할당
            users = [current_user]
            form.instance.users.set(users)
            return super(TeamCreate, self).form_valid(form)
        else:
            return redirect('/main')


#CBV

## 초대 리스트
class InviteList(LoginRequiredMixin, TemplateView):
    template_name = 'main/invite.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from_invite = user.invite_host_team.all()
        to_invite = user.invite_guest_team.all()
        context['from_invite'] = from_invite
        context['to_invite'] = to_invite
        return context


class InviteCreate(LoginRequiredMixin, CreateView):
    model = Invite
    form_class = InviteForm
    template_name = 'main/invite_form.html'

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            email = self.request.POST.get('to_user_email')  # 이메일을 POST 데이터에서 가져옴
            print(email)
            from_user = current_user
            try:
                to_user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise PermissionDenied
            else:
                form.instance.from_user = from_user
                form.instance.to_user = to_user
        return super().form_valid(form)
