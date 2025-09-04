# urls.py
from django.contrib import admin
from django.urls import path
from home import views
from django.shortcuts import redirect

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('account/login/', lambda request: redirect('login')),
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),
    path('start_quiz/', views.start_quiz, name='start_quiz'),
    path('quiz/', views.quiz, name='quiz'),
    path("quiz/submit/", views.submit_quiz, name="submit_quiz"),
    path("add_player/", views.add_player, name="add_player"),
    path("add_bulk_player/", views.add_bulk_player, name="add_bulk_player"),
    path("edit_player/", views.edit_player_redirect, name="edit_player"),
    path("edit_player/<str:pk>", views.edit_player, name="edit_player"),
    path("add_question/", views.add_question, name="add_question"),
    path("edit_question/", views.edit_question_redirect, name = "edit_question"),
    path("edit_question/<int:pk>", views.edit_question, name="edit_question"),
    path("add_bulk_questions/", views.add_bulk_questions, name="add_bulk_questions"),
]

