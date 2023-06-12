from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView

from brainservice.models import Team


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

def team_page(request):
    return render(
        request,
        'main/team.html'
)


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