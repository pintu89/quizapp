
from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.home, name='Home'),
    path('login/', views.login, name='Login'),
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),
    path('player/', views.player, name='player'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('quiz/', views.quiz, name='quiz'),
]

