from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView

from brainservice.models import Team, Channel, Post, Profile
from mainservice.forms import InviteForm, InviteResponseForm
from mainservice.models import Invite
import json

from django.http import HttpResponseServerError, HttpResponse


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
    template_name = 'main/team_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        teams = user.team_set.all()  # 사용자가 속한 모든 팀 가져오기
        context['teams'] = teams
        return context



class TeamCreate(LoginRequiredMixin, CreateView):
    model = Team
    fields = ['title', 'thumbnail', 'disc']
    template_name = 'main/team_form.html'   #템플릿 설정

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.admin = current_user
            form.save()  # Team 객체를 먼저 저장하여 id 할당
            users = [current_user]
            form.instance.users.set(users)

            channel = Channel(name="TEAM MAIN ARTICLE", disc="대문 글을 편집하세요", type="DOCS", team=form.instance)
            channel.save()
            content = '''<h1>Welcome!!</h1>
                    <br><hr><br>
                    <h2>DOCS</h2>
                    <p>마크다운 기반의 이미지가 포함된 문서를 작성할 수 있습니다.</p>
                    <hr>
                    <h2>THREAD</h2>
                    <p>주제에 대한 대화를 진행하고, 메모를 남겨둘 수 있습니다.</p>
                    <hr>
                    <h2>BRAINSTORM</h2>
                    <p>주제에 대한 생각나는 의견을 자유롭게 말해보세요! 댓글로 소통하고, 별점을 매기며 좋은 의견을 뽑을 수 있어요. 별점이 가장 높은 상위 3개가 상단에 뽑히게 됩니다.</p>
                    <hr>
                    <h2>ARGUMENT</h2>
                    <p>주제에 대한 찬반토론을 해보세요. 극명히 의견이 갈릴 것 같은 난제는 끝장토론을 해야 재격입니다.</p>'''

            post = Post(title="새로운 팀을 만든 것을 축하드립니다!", docs_content=content, channel=channel, user=current_user)
            post.save()
            return super(TeamCreate, self).form_valid(form)
        else:
            return redirect('/main')



## 초대 리스트
class InviteList(LoginRequiredMixin, TemplateView):
    template_name = 'main/invite.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from_invite = user.invite_host_team.all().order_by('-created_at')
        to_invite = user.invite_guest_team.all().order_by('-created_at')
        context['from_invite'] = from_invite
        context['to_invite'] = to_invite
        return context


class InviteCreate(LoginRequiredMixin, CreateView):
    model = Invite
    form_class = InviteForm
    template_name = 'main/invite_form.html'

    def get_form_kwargs(self):
        kwargs = super(InviteCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            email = self.request.POST.get('to_user_email')  # 이메일을 POST 데이터에서 가져옴
            print(email)
            from_user = current_user
            try:
                to_user = User.objects.get(email=email)
                is_in_team = form.instance.team.users.filter(id=to_user.id).exists()
                if to_user == self.request.user:
                    error_message = "자신에게는 초대할 수 없습니다."
                    return self.form_invalid(form, error_message)
                if is_in_team:
                    error_message = "이미 팀에 속해있습니다."
                    return self.form_invalid(form, error_message)
                is_already_invite = Invite.objects.filter(to_user=to_user, team=form.instance.team, is_accept=None).exists()
                if is_already_invite:
                    error_message = "이미 초대를 보냈습니다."
                    return self.form_invalid(form, error_message)
            except User.DoesNotExist:
                error_message = "이메일을 찾을 수 없습니다."
                return self.form_invalid(form, error_message)
            else:
                form.instance.from_user = from_user
                form.instance.to_user = to_user
        return super().form_valid(form)

    def form_invalid(self, form, error_message=None):
        context = {
            'message': error_message,
            'href': '/main'
        }
        return render(self.request, 'main/alert.html', context)



# 초대 수락
def invite_accept(request, pk):
    if request.user.is_authenticated:   # 1. 인증 여부 확인
        invite = get_object_or_404(Invite, pk=pk)
        if request.method == 'POST':    # 2. 메서드가 POST일 경우
            try:
                request_data = json.loads(request.body)
                to_user = invite.to_user
                team = invite.team
                if team.users.filter(pk=to_user.pk).exists():
                    print('Exist')
                    return HttpResponse(status=500)

                is_accept = request_data.get('is_accept')
                invite.is_accept = is_accept
                invite.save()
                if is_accept == True:
                    team.users.add(to_user)
                return HttpResponse(status=200)
            except json.JSONDecodeError:
                return HttpResponse(status=500)
        else:
            return HttpResponse(status=404)
    else:
        raise PermissionDenied



class InsertProfile(LoginRequiredMixin, CreateView):
    model = Profile
    fields = ['thumbnail']
    template_name = 'main/profile_form.html'   #템플릿 설정

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.user = current_user
            form.save()
            return super(InsertProfile, self).form_valid(form)
        else:
            return redirect('/main')


class ModifyProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['thumbnail']
    template_name = 'main/profile_form.html'  # 템플릿 설정
    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            return super(ModifyProfile, self).form_valid(form)
        else:
            return redirect('/main')

    def dispatch(self, request, *args, **kwargs):
        return super(UpdateView, self).dispatch(request, *args, **kwargs)