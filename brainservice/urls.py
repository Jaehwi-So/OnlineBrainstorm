from django.urls import path
from . import views


urlpatterns = [
    path('<int:team_pk>/main/', views.MainPage.as_view()),
    path('<int:team_pk>/members/', views.MemberInfo.as_view()),
    path('<int:team_pk>/create_channel/', views.ChannelCreate.as_view()),
    path('<int:team_pk>/channel/<int:channel_pk>/create_post/', views.PostDocTypeCreate.as_view()),
    path('<int:team_pk>/channel/<int:channel_pk>/create_post_brainstorm/', views.PostBrainTypeCreate.as_view()),
    path('<int:team_pk>/channel/<int:channel_pk>/create_post_argument/<int:pk>/', views.argument_post_input),
    path('<int:team_pk>/channel/<int:channel_pk>/create_post_tread/', views.postThreadTypeCreate),
    path('<int:team_pk>/channel/<int:channel_pk>/update_post/<int:pk>/', views.PostDocTypeUpdate.as_view()),
    path('<int:team_pk>/channel/<int:channel_pk>/post_star/<int:pk>/', views.brainstorm_starrate_input),
    path('post/<int:post_pk>/insert_comment/', views.comment_input),
    path('post/<int:post_pk>/get_comments/', views.get_comment_list),
    path('<int:team_pk>/channel/<int:pk>/', views.ChannelPage.as_view()),

]
