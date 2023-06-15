from django.urls import path
from . import views


urlpatterns = [
    path('main/', views.main_page),
    path('team/', views.TeamList.as_view()),
    path('create_team/', views.TeamCreate.as_view()),
    path('invite_accept/<int:pk>/', views.invite_accept),
    path('invite/', views.InviteList.as_view()),
    path('create_invite/', views.InviteCreate.as_view()),
    path('', views.main_page),
]