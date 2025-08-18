
from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.home, name='Home'),
    path('login/', views.login, name='Login'),
    path('admin_login/', views.admin_login, name='Admin Login'),
    path('quiz/', views.quiz, name='Quiz'),
]
