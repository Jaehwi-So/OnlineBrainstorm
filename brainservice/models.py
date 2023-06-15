from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from markdownx.models import MarkdownxField
from markdownx.utils import markdown


# 팀
class Team(models.Model):
    title = models.CharField(max_length=50, null=False)
    thumbnail = models.ImageField(upload_to='brainservice/images/%Y/%m/%d/', blank=True, null=True)
    disc = models.CharField(max_length=200, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Team <-> User N:M
    users = models.ManyToManyField(User, blank=True)   # null=True를 설정필요없음

    # Team <-> User N:1
    admin = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE, related_name='admin_teams')

    def __str__(self):
        return f'[{self.pk}] - {self.title}'

    def get_absolute_url(self):
        return f'/brain/{self.pk}/main'




# 유저 프로필
class Profile(models.Model):
    thumbnail = models.ImageField(upload_to='brainservice/images/%Y/%m/%d/', blank=True, null=True)

    # Profile <-> User 1:1
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'[{self.pk}] - {self.user.pk}-{self.name}'

    def get_absolute_url(self):
        return f'/main'


# 팀 내 개설 채널
class Channel(models.Model):
    ChannelType = models.TextChoices("ChannelType", "DOCS BRAINSTORM ARGUMENT THREAD")
    name = models.CharField(null=False, blank=False, max_length=50)
    disc = models.CharField(null=True, blank=True, max_length=200)
    type = models.CharField(null=False, blank=False, max_length=50, choices=ChannelType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Channel <-> Team N:1
    team = models.ForeignKey(Team, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f'[{self.type}] {self.name}'

    def get_absolute_url(self):
        return f'/brain/{self.team.pk}/channel/{self.pk}'

    def created_at_datetime(self):
        return self.created_at.strftime('%Y-%m-%d')


# 채널 내 글
class Post(models.Model):
    title = models.CharField(null=False, blank=False, max_length=50)
    content = models.TextField(null=True, blank=True)

    AgreeType = models.TextChoices("AgreeType", "AGREE NETURAL DISAGREE")
    docs_content = MarkdownxField(null=True, blank=True)
    arg_type = models.CharField(null=True, blank=True, max_length=50, choices=AgreeType.choices)
    arg_tree_level = models.IntegerField(null=True, blank=True)

    # Post <-> Post Self N:1
    arg_tree_parent =  models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='arg_tree_children')
    image = models.ImageField(upload_to='brainservice/images/%Y/%m/%d/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Post <-> Channel N:1
    channel = models.ForeignKey(Channel, null=False, on_delete=models.CASCADE)

    # Post <-> User N:1
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'[{self.pk}] - {self.title}'

    def get_absolute_url(self):
        return f'/brain/{self.channel.team.pk}/channel/{self.channel.pk}'

    def get_markdown_docs_content(self):
        return markdown(self.content)

    def get_average_star(self):
        stars = Star.objects.filter(post=self)
        average = 0
        if stars.exists():
            average = stars.aggregate(Avg('rate'))['rate__avg']
        return average

    def get_comments_count(self):
        comments = Comment.objects.filter(post=self)
        length = 0
        if comments.exists():
            length = len(comments)
        return length

# 글의 코멘트
class Comment(models.Model):
    content = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Comment <-> Post N:1
    post = models.ForeignKey(Post, null=False, on_delete=models.CASCADE)

    # Comment <-> User N:1
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'[{self.pk}]'



# 글의 별점
class Star(models.Model):
    rate = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Star <-> Post N:1
    post = models.ForeignKey(Post, null=False, on_delete=models.CASCADE)

    # Star <-> User N:1
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'[{self.pk}]'
