from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, CreateView, UpdateView

from brainservice.auth import IsTeamMemberRequiredMixin
from brainservice.forms import ThreadForm
from brainservice.models import Team, Channel, Post, Star, Comment
import json

from brainservice.util import depth_first_search


# Create your views here.

class MainPage(IsTeamMemberRequiredMixin, TemplateView):
    template_name = 'brain/main.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_pk = self.kwargs.get('team_pk')
        team = get_object_or_404(Team, pk=team_pk)
        channels = Channel.objects.filter(team=team_pk)
        context['team'] = team
        context['channels'] = channels
        return context

class ChannelCreate(LoginRequiredMixin, CreateView):
    model = Channel
    fields = ['name', 'type', 'disc']
    template_name = 'brain/channel_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_pk = self.kwargs.get('team_pk')
        team = get_object_or_404(Team, pk=team_pk)
        context['team'] = team
        return context

    def form_valid(self, form):
        team = get_object_or_404(Team, pk=self.kwargs.get('team_pk'))
        form.instance.team = team
        form.save()
        return super().form_valid(form)




class ChannelPage(IsTeamMemberRequiredMixin, TemplateView):
    template_name = 'brain/channel_type_docs.html'

    def get_template_names(self):
        channel_pk = self.kwargs.get('pk')
        channel = get_object_or_404(Channel, pk=channel_pk)
        channel_type = channel.type
        if channel_type == 'DOCS':
            return ['brain/channel_type_docs.html']
        elif channel_type == 'THREAD':
            return ['brain/channel_type_thread.html']
        elif channel_type == 'BRAINSTORM':
            return ['brain/channel_type_brainstorm.html']
        elif channel_type == 'ARGUMENT':
            return ['brain/channel_type_argument.html']
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        channel_pk = self.kwargs.get('pk')
        channel = get_object_or_404(Channel, pk=channel_pk)
        channels = Channel.objects.filter(team=self.kwargs.get('team_pk'))
        team = get_object_or_404(Team, pk=self.kwargs.get('team_pk'))
        if channel.type == 'BRAINSTORM':
            # 별점 기준으로 상위 3개 게시물 가져오기
            top_posts = Post.objects.filter(channel=channel_pk).annotate(average_rate=Avg('star__rate')).order_by(
                '-average_rate', '-created_at')[:3]
            # 나머지 게시물 가져오기
            remaining_posts = Post.objects.filter(channel=channel_pk).exclude(pk__in=top_posts.values('pk')).order_by(
                '-created_at')
            posts = list(top_posts) + list(remaining_posts)
        elif channel.type == 'ARGUMENT':
            channel_posts = Post.objects.filter(channel=channel_pk).order_by('arg_type', '-created_at')
            posts = depth_first_search(channel_posts)
        else:
            posts = Post.objects.filter(channel=channel_pk).order_by('-created_at')
        context['thread_form'] = ThreadForm
        context['team'] = team
        context['channels'] = channels
        context['channel'] = channel
        context['posts'] = posts
        return context

class PostDocTypeCreate(IsTeamMemberRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'docs_content','image']
    template_name = 'brain/post_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_pk = self.kwargs.get('team_pk')
        team = get_object_or_404(Team, pk=team_pk)
        context['team'] = team
        return context

    def form_valid(self, form):
        channel = get_object_or_404(Channel, pk=self.kwargs.get('channel_pk'))
        user = self.request.user
        form.instance.channel = channel
        form.instance.user = user
        form.save()
        return super().form_valid(form)

class PostBrainTypeCreate(IsTeamMemberRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'image']
    template_name = 'brain/post_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_pk = self.kwargs.get('team_pk')
        team = get_object_or_404(Team, pk=team_pk)
        context['team'] = team
        return context

    def form_valid(self, form):
        channel = get_object_or_404(Channel, pk=self.kwargs.get('channel_pk'))
        user = self.request.user
        form.instance.channel = channel
        form.instance.user = user
        form.save()
        return super().form_valid(form)



class PostDocTypeUpdate(IsTeamMemberRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'docs_content','image']
    template_name = 'brain/post_form_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_pk = self.kwargs.get('team_pk')
        team = get_object_or_404(Team, pk=team_pk)
        context['team'] = team
        return context

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        form.save()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        return super(PostDocTypeUpdate, self).dispatch(request, *args, **kwargs)

def postThreadTypeCreate(request, team_pk, channel_pk):
    if request.user.is_authenticated:   # 1. 인증 여부 확인
        channel= get_object_or_404(Channel, pk=channel_pk)
        if request.method == 'POST':    # 2. 메서드가 POST일 경우
            post_form = ThreadForm(request.POST)
            if post_form.is_valid(): # 3. 폼 유효성 검사 통과시
                post = post_form.save(commit=False)
                post.channel = channel
                post.user = request.user
                post.save()
                return redirect(channel.get_absolute_url())
        else:
            return redirect(channel.get_absolute_url())

    else:
        raise PermissionDenied


def brainstorm_starrate_input(request, team_pk, channel_pk, pk):
    if request.user.is_authenticated:   # 1. 인증 여부 확인
        post = get_object_or_404(Post, pk=pk)
        if request.method == 'POST':    # 2. 메서드가 POST일 경우
            try:
                request_data = json.loads(request.body)
                user = request.user
                if Star.objects.filter(user=user, post=post).exists():
                    return HttpResponse(status=409)
                rate = request_data.get('rate')
                star = Star(user=user, post=post, rate=rate)
                star.save()
                return HttpResponse(status=200)
            except json.JSONDecodeError:
                return HttpResponse(status=500)
        else:
            return HttpResponse(status=404)
    else:
        raise PermissionDenied


def comment_input(request, post_pk):
    if request.user.is_authenticated:   # 1. 인증 여부 확인
        post = get_object_or_404(Post, pk=post_pk)
        if request.method == 'POST':    # 2. 메서드가 POST일 경우
            try:
                request_data = json.loads(request.body)
                user = request.user
                content = request_data.get('content')
                comment = Comment(user=user, post=post, content=content)
                comment.save()
                return HttpResponse(status=200)
            except json.JSONDecodeError:
                return HttpResponse(status=500)
        else:
            return HttpResponse(status=404)
    else:
        raise PermissionDenied


def get_comment_list(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comments = Comment.objects.filter(post=post)

    comment_list = []
    for comment in comments:
        comment_data = {
            '등록일': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            '글쓴이': comment.user.username,
            '내용': comment.content,
        }
        comment_list.append(comment_data)

    return JsonResponse(data=comment_list, safe=False, status=200)



def argument_post_input(request, team_pk, channel_pk, pk):
    if request.user.is_authenticated:

        if request.method == 'POST':
            try:
                request_data = json.loads(request.body)
                user = request.user
                channel = get_object_or_404(Channel, pk=channel_pk)
                title = request_data.get('title')
                content = request_data.get('content')
                arg_type = request_data.get('arg_type')

                if pk == 0:
                    arg_tree_level = 0
                    post = None
                else:
                    post = get_object_or_404(Post, pk=pk)
                    arg_tree_level = post.arg_tree_level + 1
                post = Post(title=title, content=content, arg_type=arg_type, user=user, channel=channel,
                            arg_tree_level=arg_tree_level, arg_tree_parent=post)
                post.save()
                return HttpResponse(status=200)
            except json.JSONDecodeError:
                return HttpResponse(status=500)
        else:
            return HttpResponse(status=404)
    else:
        raise PermissionDenied