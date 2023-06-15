from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from brainservice.models import Team, Profile, Channel, Post, Comment, Star

admin.site.register(Team)
admin.site.register(Profile)
admin.site.register(Channel)
admin.site.register(Post, MarkdownxModelAdmin)
admin.site.register(Comment)
admin.site.register(Star)
