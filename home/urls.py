
from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.home, name='Home'),
    path('login/', views.login, name='Login'),
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),
    path('player/', views.player, name='player'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('start_quiz/', views.start_quiz, name='start_quiz'),
    path('quiz/', views.quiz, name='quiz'),
    path("quiz/submit/", views.submit_quiz, name="submit_quiz"),
    path("add_player/", views.add_player, name="add_player"),
    path("add_bulk_player/", views.add_bulk_player, name="add_bulk_player")
]

