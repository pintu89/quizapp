from django.contrib import admin
from django.urls import path
from ai import views

urlpatterns = [
    path('', views.ai, name='ai'),
]