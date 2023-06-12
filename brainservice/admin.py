from django.contrib import admin

from brainservice.models import Team, Profile, Channel, Post, Comment, Star

admin.site.register(Team)
admin.site.register(Profile)
admin.site.register(Channel)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Star)