from django.urls import path
from . import views


urlpatterns = [
    path('main/', views.main_page),
    path('team/', views.TeamList.as_view()),
    path('create_team/', views.TeamCreate.as_view()),
    path('invite/', views.invite_page),
    path('', views.main_page),
]