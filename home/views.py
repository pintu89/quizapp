from django.shortcuts import render, HttpResponse
from .models import Player
from django.http import JsonResponse

def add_player(request):
    if request.method == "POST":
        Player.objects.create(
            cms_id=request.POST.get("cms_id"),
            name=request.POST.get("name"),
            father_name=request.POST.get("father_name"),
            pf_no=request.POST.get("pf_no")
        )
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)
# Create your views here.
def home(request):
    return render(request, 'home/home.html')

def login(request):
   return render(request, 'home/login.html')

def quiz(request):
    return render(request, 'home/quiz.html')

def admin_login(request):
    return render(request, 'home/admin.html')
