from django.urls import path
from . import views


urlpatterns = [
    path('main/', views.main_page),
    path('team/', views.team_page),
    path('invite/', views.invite_page),
    path('', views.main_page),
]