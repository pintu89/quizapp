from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from home.utils import responses 
from home.models import Player

def home(request):
    return render(request, 'home/home.html')


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')   # CMS ID for player OR username for admin
        password = request.POST.get('password')   # Mobile no for player OR admin password

        print(f"Login attempt: {username} / {password}")

        # 1️⃣ Try authenticating as Django Admin/User
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f"Admin authenticated: {user.username}")
            auth_login(request, user)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "redirect_url": "/redirect-after-login/"})
            
            return redirect('redirect_after_login')

        # 2️⃣ If not an admin → Try authenticating as Player
        try:
            player = Player.objects.get(crewid=username)
            if player.mobile_no == password:   # ✅ password = mobile number
                # Store player ID in session manually
                request.session['player_id'] = player.id
                print(f"Player authenticated: {player.crew_name}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"success": True, "redirect_url": "/quiz/"})

                return redirect('quiz')
            else:
                print("Player password mismatch")
        except Player.DoesNotExist:
            print("No such player")

        # ❌ Authentication failed
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "Invalid username or password"}, status=400)

        return render(request, 'home/login.html', {'error': 'Invalid username or password'})

    return render(request, 'home/login.html')

@login_required
def redirect_after_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_login')   # Admin goes to dashboard
    elif 'player_id' in request.session:
        return redirect('quiz')          # Player goes to quiz page
    else:
        return redirect('login')


@login_required
def player(request):
    return render(request, 'home/player.html')


@login_required
def admin_login(request):
    return render(request, 'home/admin.html')


@login_required
def quiz(request):
    if 'player_id' not in request.session:
        return redirect('login')
    return render(request, 'home/quiz_start.html')

@login_required
def add_player(request):
    if request.method == "POST":
        try:
            player = Player.objects.create(
                crewid=request.POST.get("crewid"),
                crew_name=request.POST.get("crewname"),
                father=request.POST.get("father"),
                emp_code=request.POST.get("emp_no"),
                mobile_no=request.POST.get("mobile_no"),
            )
            return responses.success(
                message=f"Player {player.crew_name} added successfully.",
                data={"id": player.id}
            )
        except Exception as e:
            return responses.error(message=str(e))
    return render(request, "admin.html")
